#!/usr/bin/env python3
"""Run independent search lanes concurrently with a fail-fast preflight.

Each lane is one line of a TSV file with `lane` and `query` columns. The
command template is split like a shell command but run without a shell; the
placeholders {lane}, {query}, and {out} are replaced inside each argument.

1. The optional preflight command runs first under a short timeout. If it
   fails, no lane is launched and every lane is recorded as not run.
2. Lanes run as separate processes, at most --jobs at a time, each under its
   own --timeout, so one hung lane cannot hold up the others.
3. A status line is printed as each lane finishes. Logs are saved per lane
   with credential-like URL parameters redacted, and a JSON summary records
   each lane's query, status, timestamps, and returned count.

Concurrency is safe only when the retrieval tool enforces a rate limit shared
across processes (as polite_http does with a lock file). Otherwise use
--jobs 1. A failed or timed-out lane is never a zero-hit search.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shlex
import signal
import subprocess
import sys
import time

SECRET = re.compile(r"((?:api_?key|token|access_token|key|email|password)=)[^&\s\"']+", re.I)


def redact(text: str) -> str:
    return SECRET.sub(r"\1REDACTED", text)


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def build(template: str, **values: str) -> list[str]:
    return [re.sub(r"\{(lane|query|out)\}", lambda m: values[m[1]], part) for part in shlex.split(template)]


def execute(command: list[str], timeout: float) -> tuple[str, int | None, bool]:
    """Run a command in its own process group; kill the whole group on timeout.

    Killing only `uv run` can leave its Python child retrying in the background.
    Returns (combined output, return code, timed_out).
    """
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, start_new_session=True)
    try:
        output, _ = process.communicate(timeout=timeout)
        return output, process.returncode, False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        output, _ = process.communicate()
        return output or "", None, True


def count_results(path: Path) -> tuple[int | None, str | None]:
    """Return (count, error) from a JSON result file, when it can be read."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None, None
    if isinstance(data, dict) and data.get("error"):
        return None, redact(str(data["error"]))[:300]
    if isinstance(data, list):
        return len(data), None
    if isinstance(data, dict):
        for key in ("count", "ids", "idlist", "pmids", "results"):
            value = data.get(key)
            if isinstance(value, list):
                return len(value), None
            if key == "count" and str(value).isdigit():
                return int(value), None
    return None, None


def named(record: dict) -> str:
    """Lane identifier with its reminder keyword, for example "lane-1 (core self-administration)"."""
    return f"{record['lane']} ({record['label']})" if record.get("label") else record["lane"]


def preflight_advice(detail: str) -> str:
    """Name the likely cause of a failed preflight from its HTTP status, if any."""
    status = re.search(r"\b(429|50[0234]|40[13])\b", detail)
    code = status[1] if status else None
    if code == "429":
        return "the service is rate-limiting requests (HTTP 429); wait at least the Retry-After interval (often about a minute), then rerun"
    if code in ("500", "502", "503", "504"):
        return f"the service reported an error or outage (HTTP {code}); check the provider's root or status page, then rerun later"
    if code in ("401", "403"):
        return f"access was refused (HTTP {code}); check credentials, API key, or network access rules"
    return "check network, proxy, or credentials, then rerun"


def result_ids(path: Path) -> list[str]:
    """Identifiers from a lane result: a list of IDs or of records with an ID field."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if isinstance(data, dict):
        data = next((data[key] for key in ("ids", "idlist", "pmids", "results") if isinstance(data.get(key), list)), [])
    ids = []
    for item in data if isinstance(data, list) else []:
        if isinstance(item, dict):
            item = next((item[key] for key in ("pmid", "doi", "id") if item.get(key)), None)
        if item not in (None, ""):
            ids.append(str(item))
    return ids


def estimate_size(records: list[dict], cap: int | None, batch: int) -> dict:
    """Union size, lane overlap, and screening workload from successful lanes.

    Writes nothing; the caller saves the union and membership files.
    """
    membership: dict[str, list[str]] = {}
    for record in records:
        if record["status"] == "ok":
            for identifier in dict.fromkeys(result_ids(Path(record["out"]))):
                membership.setdefault(identifier, []).append(record["lane"])
    lanes = [record["lane"] for record in records]
    only = {lane: sum(1 for found in membership.values() if found == [lane]) for lane in lanes}
    capped = [record["lane"] for record in records
              if cap and record["status"] == "ok" and (record["returned"] or 0) >= cap]
    not_ok = [record["lane"] for record in records if record["status"] != "ok"]
    return {
        "unique_ids": len(membership),
        "returned_total": sum(record["returned"] or 0 for record in records if record["status"] == "ok"),
        "unique_to_lane": only,
        "lanes_possibly_capped": capped,
        "lanes_not_ok": not_ok,
        "lower_bound": bool(capped or not_ok),
        "screening_batches": -(-len(membership) // batch) if membership else 0,
        "batch_size": batch,
        "_membership": membership,
    }


def run_one(lane: dict, args: argparse.Namespace) -> dict:
    out = args.out_dir / f"{lane['lane']}_results.json"
    log = args.log_dir / f"{lane['lane']}_log.txt"
    command = build(args.command, lane=lane["lane"], query=lane["query"], out=str(out))
    record = {"lane": lane["lane"], "label": (lane.get("label") or "").strip(), "query": lane["query"],
              "out": str(out), "log": str(log), "started": now()}
    start = time.monotonic()
    try:
        output, code, timed_out = execute(command, args.timeout)
        status = "timeout" if timed_out else "ok" if code == 0 else "failed"
    except OSError as error:
        output, code, status = str(error), None, "failed"
    log.write_text(redact(output), encoding="utf-8")
    count, api_error = count_results(out) if status == "ok" else (None, None)
    if api_error:
        status = "failed"
    record.update(ended=now(), seconds=round(time.monotonic() - start, 1), status=status,
                  returncode=code, returned=count, error=api_error)
    if status != "ok" and not api_error:
        tail = redact(output).strip().splitlines()[-2:]
        record["error"] = f"timed out after {args.timeout}s" if status == "timeout" else " | ".join(tail)[:300]
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("lanes", type=Path, help="TSV with lane and query columns")
    parser.add_argument("--command", required=True, help="command template using {lane}, {query}, {out}")
    parser.add_argument("--preflight", help="cheap connectivity/credential check run before any lane")
    parser.add_argument("--preflight-timeout", type=float, default=30)
    parser.add_argument("--jobs", type=int, default=3, help="concurrent lanes (default 3)")
    parser.add_argument("--timeout", type=float, default=120, help="seconds per lane (default 120)")
    parser.add_argument("--out-dir", type=Path, default=Path("searches"))
    parser.add_argument("--log-dir", type=Path, help="default: --out-dir")
    parser.add_argument("--summary", type=Path, help="default: <out-dir>/lanes_summary.json")
    parser.add_argument("--cap", type=int, help="per-lane result limit passed to the tool; lanes reaching it are flagged as possibly capped")
    parser.add_argument("--batch-size", type=int, default=25, help="screening batch size used in the workload estimate (default 25)")
    args = parser.parse_args(argv)
    args.log_dir = args.log_dir or args.out_dir
    args.summary = args.summary or args.out_dir / "lanes_summary.json"
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)

    with args.lanes.open(encoding="utf-8") as handle:
        lanes = [row for row in csv.DictReader(handle, delimiter="\t") if (row.get("lane") or "").strip()]
    ids = [lane["lane"] for lane in lanes]
    if len(set(ids)) != len(ids):
        parser.error("lane identifiers must be unique")
    summary = {"started": now(), "command": redact(args.command), "jobs": args.jobs,
               "timeout": args.timeout, "preflight": None, "lanes": []}
    begin = time.monotonic()

    def write_summary() -> None:
        summary["ended"] = now()
        args.summary.write_text(json.dumps(summary, indent=1) + "\n", encoding="utf-8")

    print(f"[search] {len(lanes)} lanes, up to {args.jobs} at a time, {args.timeout:g}s per lane", flush=True)
    if args.preflight:
        try:
            output, code, timed_out = execute(shlex.split(args.preflight), args.preflight_timeout)
            ok = code == 0 and not timed_out
            detail = f"timed out after {args.preflight_timeout:g}s" if timed_out else (output.strip().splitlines() or [""])[-1]
        except OSError as error:
            ok, detail = False, str(error)
        summary["preflight"] = {"status": "ok" if ok else "failed", "detail": redact(detail)[:300]}
        if not ok:
            print(f"[preflight] FAILED: {redact(detail)[:300]}", flush=True)
            print(f"[search] no lanes launched; {preflight_advice(detail)}", flush=True)
            summary["lanes"] = [dict(lane, status="not run") for lane in lanes]
            write_summary()
            return 2
        print("[preflight] ok", flush=True)

    done = 0
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as pool:
        futures = [pool.submit(run_one, lane, args) for lane in lanes]
        for future in as_completed(futures):
            record = future.result()
            summary["lanes"].append(record)
            done += 1
            result = f"{record['returned']} returned" if record["status"] == "ok" else f"{record['status']}: {record['error']}"
            print(f"[search] {done}/{len(lanes)} lanes; {named(record)} {result}; "
                  f"{record['seconds']}s; elapsed {time.monotonic() - begin:.0f}s", flush=True)
            write_summary()

    order = {lane: index for index, lane in enumerate(ids)}
    summary["lanes"].sort(key=lambda record: order[record["lane"]])
    write_summary()
    failed = [record["lane"] for record in summary["lanes"] if record["status"] != "ok"]

    size = estimate_size(summary["lanes"], args.cap, args.batch_size)
    membership = size.pop("_membership")
    (args.out_dir / "union_ids.json").write_text(json.dumps(sorted(membership, key=lambda i: (len(i), i)), indent=1) + "\n", encoding="utf-8")
    (args.out_dir / "membership.json").write_text(json.dumps(membership, indent=1) + "\n", encoding="utf-8")
    summary["size_estimate"] = size
    write_summary()
    bound = "at least " if size["lower_bound"] else ""
    print(f"[size] {bound}{size['unique_ids']} unique records across {len(lanes) - len(failed)} lanes "
          f"({size['returned_total']} returned before deduplication); about {size['screening_batches']} "
          f"screening batches of {size['batch_size']}", flush=True)
    labels = {record["lane"]: named(record) for record in summary["lanes"]}
    print("[size] unique to one lane: " + ", ".join(f"{labels[lane]} {n}" for lane, n in size["unique_to_lane"].items()), flush=True)
    if size["lanes_possibly_capped"]:
        print(f"[size] possibly capped at {args.cap}: {', '.join(size['lanes_possibly_capped'])}; the true size is larger", flush=True)
    print("[size] decision needed: all records or a defined subset, before abstract retrieval and screening", flush=True)
    print(f"[search] finished: {len(lanes) - len(failed)} ok, {len(failed)} not ok"
          + (f" ({', '.join(failed)}); rerun only those lanes" if failed else "")
          + f"; summary {args.summary}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
