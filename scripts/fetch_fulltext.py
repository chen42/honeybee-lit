#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["polite-http", "python-dotenv"]
# ///
"""Plan and retrieve full texts, reusing wasp-lit's retrieval routes read-only.

Three subcommands, run from the review workspace:

  plan      Cheap access check for each PMID: PMC identifiers (PubMed links and
            Europe PMC metadata), Europe PMC open-access status, and an OpenAlex
            open-access lookup for records not in PMC. Writes fulltext_plan.json
            and needs_user.tsv, prints counts by category, and stops for a
            decision. No full text is downloaded.
  fetch     For the approved categories or PMIDs, tries wasp-lit's routes in
            order (PMC efetch, Europe PMC fullTextXML, PMC BioC), saves the raw
            response and parsed passages with SHA-256 hashes, and records every
            attempt. Records that no route serves are added to needs_user.tsv.
  register  Records a user-supplied or institutionally retrieved file for a
            PMID: copies it unchanged into the full-text folder, hashes it, and
            marks its identity check as pending.

Outcomes follow wasp-lit: retrieved, unavailable (a route confirmed absence),
or failed (every route errored; retry later). A Europe PMC HTTP 500 for an
article whose Europe PMC metadata says isOpenAccess=N is treated as absence
from that route, not as a transient error, and BioC is skipped for such
articles. This script never bypasses paywalls, authentication, or rate limits
and does not scrape publisher sites.

Run with `uv run`, which installs the HTTP client used by the PubMed wrapper.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import threading
import time
import urllib.error
import urllib.request

SKILLS = Path.home() / ".agents" / "skills"
DEFAULT_WASP = SKILLS / "wasp-lit" / "scripts" / "pubmed_extension.py"
DEFAULT_WRAPPER = SKILLS / "pubmed_database" / "scripts" / "pubmed_api.py"
OPENALEX = "https://api.openalex.org/works/pmid:{}"
CATEGORIES = ("pmc_open_access", "pmc_restricted", "pmc_access_unknown",
              "open_elsewhere", "closed", "lookup_failed")
FETCHABLE = ("pmc_open_access", "pmc_restricted", "pmc_access_unknown")
NEEDS_USER_FIELDS = ("pmid", "doi", "category", "status", "oa_status", "oa_url", "landing_url", "note")
SECRET = re.compile(r"((?:api_?key|token|email)=)[^&\s\"']+", re.I)


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def redact(value) -> str:
    return SECRET.sub(r"\1REDACTED", str(value))


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def find_wasp(path: Path | None) -> Path:
    """Locate wasp-lit's retrieval module, tolerating a renamed skill folder."""
    if path is not None:
        return path
    if DEFAULT_WASP.is_file():
        return DEFAULT_WASP
    found = sorted(SKILLS.glob("*/scripts/pubmed_extension.py"))
    if len(found) == 1:
        return found[0]
    raise SystemExit("wasp-lit retrieval module (scripts/pubmed_extension.py) not found under "
                     f"{SKILLS}" + (f"; several candidates: {', '.join(map(str, found))}" if found else "") + "; pass --wasp")


def load_backend_class(wasp: Path):
    """Import wasp-lit's PubmedBackend without modifying wasp-lit.

    The subclass keeps the raw JATS text on success, which wasp-lit discards.
    """
    if not wasp.is_file():
        raise SystemExit(f"wasp-lit retrieval module not found at {wasp}; pass --wasp")
    spec = importlib.util.spec_from_file_location("honeybee_wasp_extension", wasp)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    class Backend(module.PubmedBackend):
        def fulltext(self, pmid, links):
            # BioC serves only the PMC open-access subset. For an article Europe PMC
            # marks isOpenAccess=N it cannot succeed, and its 429 back-off is shared
            # across NCBI hosts, stalling every other request.
            self.skip_bioc = (links.get("europepmc") or {}).get("isOpenAccess") == "N"
            return super().fulltext(pmid, links)

        def provider_document(self, name, pmid, pmcids):
            if name == "pmc-bioc" and getattr(self, "skip_bioc", False):
                return {"provider": name, "status": "skipped",
                        "reason": "BioC serves only the PMC open-access subset; Europe PMC metadata says isOpenAccess=N"}
            return super().provider_document(name, pmid, pmcids)

        def jats_attempt(self, name, raw, pmid, pmcids, url):
            attempt = super().jats_attempt(name, raw, pmid, pmcids, url)
            if attempt.get("status") == "retrieved":
                attempt["document"]["raw"] = raw
            return attempt

    return Backend, module.BackendError


def openalex_lookup(pmid: str, timeout: float = 20) -> dict:
    """Open-access status from OpenAlex; no credentials are sent."""
    request = urllib.request.Request(OPENALEX.format(pmid), headers={"User-Agent": "honeybee-lit"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                data = json.load(response)
            break
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return {"status": "not found"}
            if error.code not in (429, 500, 502, 503) or attempt == 2:
                return {"status": "error", "error": f"HTTP {error.code}"}
        except (urllib.error.URLError, TimeoutError, ValueError) as error:
            if attempt == 2:
                return {"status": "error", "error": str(error)[:200]}
        time.sleep(2 * (attempt + 1))
    best = data.get("best_oa_location") or {}
    access = data.get("open_access") or {}
    return {"status": "ok", "doi": (data.get("doi") or "").replace("https://doi.org/", "") or None,
            "is_oa": access.get("is_oa"), "oa_status": access.get("oa_status"),
            "oa_url": best.get("pdf_url") or access.get("oa_url"),
            "landing_url": best.get("landing_page_url")}


def classify(links: dict | None, openalex: dict | None) -> str:
    """Access category from link and metadata lookups, before any download."""
    if links is None:
        return "lookup_failed"
    if links.get("candidate_pmcids"):
        flag = (links.get("europepmc") or {}).get("isOpenAccess")
        return {"Y": "pmc_open_access", "N": "pmc_restricted"}.get(flag, "pmc_access_unknown")
    if not openalex or openalex.get("status") != "ok":
        return "lookup_failed"
    return "open_elsewhere" if openalex.get("is_oa") else "closed"


def reclassify(result: dict, europepmc: dict | None) -> dict:
    """Record known absence signals as absence, then recount the outcome."""
    if result.get("status") == "retrieved":
        return result
    not_oa = (europepmc or {}).get("isOpenAccess") == "N"
    for attempt in result.get("attempts", []):
        if (not_oa and attempt.get("provider") == "europepmc" and attempt.get("status") == "error"
                and "500" in str(attempt.get("error"))):
            attempt["status"] = "unavailable"
            attempt["reason"] = "Europe PMC fullTextXML HTTP 500 for an article its metadata marks isOpenAccess=N"
        elif (attempt.get("provider") == "pmc-bioc" and attempt.get("status") == "error"
                and "No result can be found" in str(attempt.get("error"))):
            attempt["status"] = "unavailable"
            attempt["reason"] = "BioC answered 'No result can be found' (not in the PMC open-access subset)"
    attempts = result.get("attempts", [])
    negatives = [a["provider"] for a in attempts if a.get("status") == "unavailable"]
    errors = [a["provider"] for a in attempts if a.get("status") == "error"]
    if negatives:
        result.update(status="unavailable", confirmed_by=negatives, errored=errors)
    else:
        result["status"] = "failed"
    return result


class Pool:
    """One backend per worker thread; the HTTP client's rate limit is shared via a lock file."""

    def __init__(self, factory):
        self.factory, self.local = factory, threading.local()

    def get(self):
        if getattr(self.local, "backend", None) is None:
            self.local.backend = self.factory()
        return self.local.backend


def plan_one(pmid: str, pool: Pool, lookup) -> dict:
    entry = {"pmid": pmid, "checked": now()}
    try:
        links = pool.get().links(pmid)
        entry["links"] = json.loads(redact(json.dumps(links)))
    except Exception as error:  # a lookup failure must stay visible, not become "closed"
        links = None
        entry["links_error"] = redact(error)[:300]
    openalex = lookup(pmid) if links is not None and not links.get("candidate_pmcids") else None
    if openalex is not None:
        entry["openalex"] = openalex
    entry["category"] = classify(links, openalex)
    return entry


def fetch_one(entry: dict, pool: Pool, out: Path) -> dict:
    pmid, links = entry["pmid"], entry.get("links") or {"candidate_pmcids": []}
    try:
        result = pool.get().fulltext(pmid, links)
    except Exception as error:
        result = {"status": "failed", "pmid": pmid, "attempts": [], "error": redact(error)[:300]}
    result = reclassify(result, links.get("europepmc"))
    record = {"pmid": pmid, "category": entry.get("category"), "status": result["status"],
              "retrieved_at": now(), "provider": result.get("provider"),
              "attempts": [{k: (redact(v)[:300] if k in ("error", "reason") else v)
                            for k, v in attempt.items() if k not in ("document", "raw_response")}
                           for attempt in result.get("attempts", [])],
              "retry_policy": result.get("retry_policy")}
    if result["status"] == "unavailable":
        record["confirmed_by"] = result.get("confirmed_by")
    attempts_dir = out / "attempts"
    attempts_dir.mkdir(parents=True, exist_ok=True)
    raw_errors = [{"provider": a.get("provider"), "raw_response": a["raw_response"]}
                  for a in result.get("attempts", []) if a.get("raw_response") is not None]
    (attempts_dir / f"{pmid}.json").write_text(json.dumps(
        {"record": record, "raw_error_responses": raw_errors}, indent=1, default=str) + "\n", encoding="utf-8")
    if result["status"] == "retrieved":
        document = result["document"]
        if "raw" in document:
            raw, suffix = document.pop("raw").encode("utf-8"), "xml"
        else:
            raw, suffix = json.dumps(document.pop("raw_bioc", None), ensure_ascii=False).encode("utf-8"), "json"
        raw_path = out / f"{pmid}.{result['provider']}.{suffix}"
        parsed_path = out / f"{pmid}.passages.json"
        raw_path.write_bytes(raw)
        parsed = json.dumps(document, indent=1, ensure_ascii=False).encode("utf-8")
        parsed_path.write_bytes(parsed)
        words = len(" ".join(p.get("text", "") for p in document.get("passages", [])).split())
        record.update(raw_path=str(raw_path), raw_sha256=sha256_bytes(raw), parsed_path=str(parsed_path),
                      parsed_sha256=sha256_bytes(parsed), words=words, pmcid=document.get("pmcid"),
                      license=document.get("license", "not checked"), figures_reviewed=False,
                      supplements_reviewed=False)
    elif result["status"] == "failed":
        record["error"] = redact(result.get("error") or "; ".join(
            f"{a.get('provider')}: {a.get('error')}" for a in result.get("attempts", [])))[:300]
    return record


def run_parallel(items, worker, jobs: int, label: str, describe) -> list[dict]:
    results, begin = [], time.monotonic()
    with ThreadPoolExecutor(max_workers=max(1, jobs)) as executor:
        futures = [executor.submit(worker, item) for item in items]
        for done, future in enumerate(as_completed(futures), 1):
            record = future.result()
            results.append(record)
            print(f"[{label}] {done}/{len(items)} PMID {record['pmid']} {describe(record)}; "
                  f"elapsed {time.monotonic() - begin:.0f}s", flush=True)
    order = {(item["pmid"] if isinstance(item, dict) else item): i for i, item in enumerate(items)}
    return sorted(results, key=lambda record: order[record["pmid"]])


def write_needs_user(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, NEEDS_USER_FIELDS, delimiter="\t", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def needs_user_row(entry: dict, status: str, note: str) -> dict:
    openalex = entry.get("openalex") or {}
    europepmc = (entry.get("links") or {}).get("europepmc") or {}
    return {"pmid": entry["pmid"], "doi": openalex.get("doi") or europepmc.get("doi") or "",
            "category": entry.get("category"), "status": status, "oa_status": openalex.get("oa_status") or "",
            "oa_url": openalex.get("oa_url") or "", "landing_url": openalex.get("landing_url") or "", "note": note}


NOTES = {
    "open_elsewhere": "Open access outside PMC; publisher sites often block scripts. Download in a browser or via institutional access, then register.",
    "closed": "Not open access. Needs institutional access or a user-supplied copy.",
    "lookup_failed": "Access lookups failed; rerun plan before deciding.",
}


def read_pmids(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
        values = data if isinstance(data, list) else list(data)
        pmids = [str(v.get("pmid") if isinstance(v, dict) else v) for v in values]
    except ValueError:
        pmids = [line.split("\t")[0].strip() for line in text.splitlines()]
    return list(dict.fromkeys(p for p in pmids if p.isdigit()))


def cmd_plan(args, factory, lookup) -> int:
    pmids = read_pmids(args.pmids)
    args.out.mkdir(parents=True, exist_ok=True)
    print(f"[fulltext-plan] {len(pmids)} PMIDs, access lookups only, up to {args.jobs} at a time", flush=True)
    pool = Pool(factory)
    entries = run_parallel(pmids, lambda pmid: plan_one(pmid, pool, lookup), args.jobs, "fulltext-plan",
                           lambda e: e["category"])
    counts = {category: sum(e["category"] == category for e in entries) for category in CATEGORIES}
    plan = {"created": now(), "pmids_file": str(args.pmids), "counts": counts, "entries": entries}
    (args.out / "fulltext_plan.json").write_text(json.dumps(plan, indent=1) + "\n", encoding="utf-8")
    write_needs_user(args.out / "needs_user.tsv", [needs_user_row(e, "not attempted", NOTES[e["category"]])
                                                 for e in entries if e["category"] in NOTES])
    print("[fulltext-plan] " + ", ".join(f"{k}={v}" for k, v in counts.items() if v), flush=True)
    fetchable = sum(counts[c] for c in FETCHABLE)
    print(f"[fulltext-plan] script-retrievable candidates: {counts['pmc_open_access']} open access in PMC; "
          f"{counts['pmc_restricted'] + counts['pmc_access_unknown']} in PMC without an open-access license "
          f"(PMC often still serves the text, e.g. author manuscripts; fetching them is quick); {fetchable} total", flush=True)
    print(f"[fulltext-plan] needing user or institutional access: {counts['open_elsewhere'] + counts['closed']} "
          f"(see {args.out / 'needs_user.tsv'})", flush=True)
    print("[fulltext-plan] decision needed: which categories or PMIDs to fetch, before any download", flush=True)
    return 1 if counts["lookup_failed"] else 0


def cmd_fetch(args, factory) -> int:
    plan_path = args.out / "fulltext_plan.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    by_pmid = {e["pmid"]: e for e in plan["entries"]}
    if args.pmid:
        missing = [p for p in args.pmid if p not in by_pmid]
        if missing:
            raise SystemExit(f"not in {plan_path}: {', '.join(missing)}; rerun plan with them")
        selected = [by_pmid[p] for p in args.pmid]
    else:
        categories = args.categories.split(",")
        selected = [e for e in plan["entries"] if e["category"] in categories]
    index_path = args.out / "fulltext_index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    if not args.refetch:
        skipped = [e["pmid"] for e in selected if index.get(e["pmid"], {}).get("status") == "retrieved"]
        selected = [e for e in selected if e["pmid"] not in skipped]
        if skipped:
            print(f"[fulltext] {len(skipped)} already retrieved, kept unchanged (use --refetch for a new snapshot)", flush=True)
    print(f"[fulltext] {len(selected)} PMIDs, routes pmc-efetch > europepmc > pmc-bioc, up to {args.jobs} at a time", flush=True)
    pool = Pool(factory)
    describe = lambda r: (f"retrieved via {r['provider']} ({r.get('words')} words)" if r["status"] == "retrieved"
                          else r["status"] + (f": {r.get('error')}" if r["status"] == "failed" else ""))
    records = run_parallel(selected, lambda e: fetch_one(e, pool, args.out), args.jobs, "fulltext", describe)
    for record in records:
        if index.get(record["pmid"], {}).get("status") == "retrieved":
            record["previous"] = index[record["pmid"]]
        index[record["pmid"]] = record
    index_path.write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")

    rows = [needs_user_row(e, "not attempted", NOTES[e["category"]]) for p, e in by_pmid.items()
            if e["category"] in NOTES and index.get(p, {}).get("status") != "retrieved"]
    rows += [needs_user_row(by_pmid[p], "unavailable", "No route served the full text (" +
                            ", ".join(r.get("confirmed_by") or []) +
                            "). Needs institutional access or a user-supplied copy.")
             for p, r in index.items() if r["status"] == "unavailable" and p in by_pmid]
    write_needs_user(args.out / "needs_user.tsv", rows)
    tally = {s: sum(r["status"] == s for r in records) for s in ("retrieved", "unavailable", "failed")}
    print(f"[fulltext] finished: retrieved={tally['retrieved']}, unavailable={tally['unavailable']}, "
          f"failed={tally['failed']}" + ("; rerun failed PMIDs later with --pmid" if tally["failed"] else "")
          + f"; index {index_path}; needs-user list {args.out / 'needs_user.tsv'}", flush=True)
    return 1 if tally["failed"] else 0


def cmd_register(args) -> int:
    source = args.file
    if not source.is_file():
        raise SystemExit(f"no such file: {source}")
    args.out.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    digest = sha256_bytes(data)
    target = args.out / f"{args.pmid}.user-supplied.{digest[:12]}{source.suffix.lower()}"
    if not target.exists():
        shutil.copy2(source, target)
    index_path = args.out / "fulltext_index.json"
    index = json.loads(index_path.read_text(encoding="utf-8")) if index_path.exists() else {}
    record = {"pmid": args.pmid, "status": "retrieved", "provider": "user-supplied", "retrieved_at": now(),
              "intake_origin": args.origin, "original_path": str(source.resolve()), "raw_path": str(target),
              "raw_sha256": digest, "identity_check": "pending: confirm title, authors, and DOI against the PubMed record",
              "license": args.license or "not checked", "redistribution": "not permitted unless the license allows it",
              "figures_reviewed": False, "supplements_reviewed": False}
    if index.get(args.pmid, {}).get("status") == "retrieved":
        record["previous"] = index[args.pmid]
    index[args.pmid] = record
    index_path.write_text(json.dumps(index, indent=1) + "\n", encoding="utf-8")
    needs_user = args.out / "needs_user.tsv"
    if needs_user.exists():
        with needs_user.open(encoding="utf-8") as handle:
            rows = [row for row in csv.DictReader(handle, delimiter="\t") if row["pmid"] != args.pmid]
        write_needs_user(needs_user, rows)
    print(f"[fulltext] registered PMID {args.pmid} from {args.origin}: {target} sha256 {digest[:12]}; identity check pending", flush=True)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=Path("sources/fulltext"), help="full-text folder (default sources/fulltext)")
    parser.add_argument("--wasp", type=Path, help="wasp-lit scripts/pubmed_extension.py (default: found under ~/.agents/skills)")
    parser.add_argument("--pubmed-wrapper", type=Path, default=DEFAULT_WRAPPER, help="installed pubmed_api.py")
    parser.add_argument("--jobs", type=int, default=3)
    commands = parser.add_subparsers(dest="command", required=True)
    plan = commands.add_parser("plan", help="access check only; no downloads")
    plan.add_argument("pmids", type=Path, help="JSON list of PMIDs or records with pmid, or one PMID per line")
    fetch = commands.add_parser("fetch", help="retrieve approved records")
    fetch.add_argument("--categories", default="pmc_open_access,pmc_restricted,pmc_access_unknown",
                       help=f"comma-separated plan categories (default: all PMC categories; fetchable: {', '.join(FETCHABLE)})")
    fetch.add_argument("--pmid", action="append", help="fetch these PMIDs instead of categories")
    fetch.add_argument("--refetch", action="store_true", help="fetch again and keep the earlier record as previous")
    register = commands.add_parser("register", help="record a user-supplied or institutionally retrieved file")
    register.add_argument("--pmid", required=True)
    register.add_argument("--file", type=Path, required=True)
    register.add_argument("--origin", required=True, help='for example "UTHSC library, institutional access"')
    register.add_argument("--license", help="license statement if known")
    return parser


def main(argv: list[str] | None = None, factory=None, lookup=openalex_lookup) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "register":
        return cmd_register(args)
    if factory is None:
        backend, _ = load_backend_class(find_wasp(args.wasp))
        factory = lambda: backend(args.pubmed_wrapper)
    return cmd_plan(args, factory, lookup) if args.command == "plan" else cmd_fetch(args, factory)


if __name__ == "__main__":
    sys.exit(main())
