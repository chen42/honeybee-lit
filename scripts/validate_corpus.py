#!/usr/bin/env python3
"""Mechanical checks for a review workspace, not for scientific support.

Checks, as requested by the options:

1. Manifest integrity: every listed file exists and matches its SHA-256;
   a manifest that lists itself is reported.
2. Citation membership: identifiers cited in synthesis, note, or claim files
   resolve to the registered corpus; unresolved citation placeholders fail.
3. Screening ledger: allowed decisions, required fields, counts generated
   from explicit decisions, and excluded records cited as evidence.

Passing these checks does not show that a passage supports a claim, that a
source was read completely, or that a design supports an interpretation.
The script reads files only; it never repairs or rewrites them.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import re

PMID_LABELED = re.compile(r"(?:PMID|pubmed\.ncbi\.nlm\.nih\.gov/)\s*:?\s*(\d{1,9})", re.I)
BARE_NUMBER = re.compile(r"(?<![\w./-])(\d{7,9})(?![\w./])")
DOI = re.compile(r"\b(10\.\d{4,9}/[^\s\"'<>|\]]+)", re.I)
PLACEHOLDERS = [
    (re.compile(r"\b\d{5,9}-like\b"), "identifier marked '-like'"),
    (re.compile(r"\b\d{5,9}\s*\(\?\)"), "identifier marked '(?)'"),
    (re.compile(r"PMID\s*:?\s*(?:\?|TBD|X{2,}|N/?A\b)", re.I), "unfilled PMID"),
    (re.compile(r"\?\?"), "'??' marker"),
]
REVIEW_QUERY = re.compile(r"\[REVIEW QUERY:")
DECISIONS = {"advance", "include", "exclude", "uncertain"}
STAGES = {"title_abstract", "full_text", "abstract_bounded"}
LEDGER_FIELDS = ("record_id", "stage", "decision", "reviewer_id", "timestamp")
ID_KEYS = ("pmid", "doi", "source_id", "record_id", "id")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def norm(identifier: str) -> str:
    identifier = identifier.strip().rstrip(".,;:)")
    return identifier.lower() if identifier.lower().startswith("10.") else identifier


def read_rows(path: Path) -> list[dict]:
    """Read a JSON array/object, JSONL, or TSV file into row dictionaries."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in text.splitlines() if line.strip()]
    if path.suffix == ".tsv":
        # csv keeps every value a string, so identifiers such as NA stay literal.
        return list(csv.DictReader(text.splitlines(), delimiter="\t"))
    if path.suffix == ".txt":
        return [{"id": line.strip()} for line in text.splitlines() if line.strip()]
    data = json.loads(text)
    if isinstance(data, dict):
        rows = data.get("files") or data.get("records")
        if isinstance(rows, list):
            return rows
        return [dict(value, id=key) if isinstance(value, dict) else {"id": key} for key, value in data.items()]
    return [row if isinstance(row, dict) else {"id": str(row)} for row in data]


def corpus_records(paths: list[Path]) -> list[set[str]]:
    """One identifier set per registered record (PMID, DOI, local IDs)."""
    records: list[set[str]] = []
    for path in paths:
        for row in read_rows(path):
            ids = {norm(str(row[key])) for key in ID_KEYS if row.get(key) not in (None, "")}
            if ids:
                records.append(ids)
    return records


def check_manifest(manifest: Path, root: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    notes: list[str] = []
    rows = read_rows(manifest)
    for index, row in enumerate(rows, 1):
        listed, expected = row.get("path"), (row.get("sha256") or "").lower()
        if not listed or not expected:
            errors.append(f"{manifest}: entry {index} lacks path or sha256")
            continue
        target = (root / listed).resolve()
        if target == manifest.resolve():
            errors.append(f"{manifest}: lists itself ({listed}); record the finalized manifest hash elsewhere")
        elif not target.is_file():
            errors.append(f"{manifest}: missing file {listed}")
        elif sha256(target) != expected:
            errors.append(f"{manifest}: hash mismatch for {listed}")
    notes.append(f"{manifest}: {len(rows)} entries checked")
    return errors, notes


def cited(text: str, bare: bool) -> dict[str, int]:
    """Map each cited identifier to the first line where it appears."""
    found: dict[str, int] = {}
    for number, line in enumerate(text.splitlines(), 1):
        candidates = [m[1] for m in PMID_LABELED.finditer(line)] + [m[1] for m in DOI.finditer(line)]
        if bare:
            candidates += [m[1] for m in BARE_NUMBER.finditer(line)]
        for candidate in candidates:
            found.setdefault(norm(candidate), number)
    return found


def read_ledger(path: Path) -> tuple[dict[tuple[str, str], dict], list[str]]:
    """Return the latest row per (record, stage); rows are an append-only log."""
    errors: list[str] = []
    latest: dict[tuple[str, str], dict] = {}
    for index, row in enumerate(read_rows(path), 1):
        where = f"{path}: row {index}"
        missing = [field for field in LEDGER_FIELDS if not str(row.get(field) or "").strip()]
        if missing:
            errors.append(f"{where}: missing {', '.join(missing)}")
            continue
        if row["decision"] not in DECISIONS:
            errors.append(f"{where}: decision {row['decision']!r} not in {sorted(DECISIONS)}")
        if row["stage"] not in STAGES:
            errors.append(f"{where}: stage {row['stage']!r} not in {sorted(STAGES)}")
        if row["decision"] == "exclude" and not str(row.get("primary_reason_id") or "").strip():
            errors.append(f"{where}: exclusion without primary_reason_id")
        latest[(norm(str(row["record_id"])), row["stage"])] = row
    return latest, errors


def final_decisions(latest: dict[tuple[str, str], dict]) -> dict[str, tuple[str, str]]:
    """Latest decision at the most advanced stage reached by each record."""
    order = {"title_abstract": 0, "abstract_bounded": 1, "full_text": 2}
    result: dict[str, tuple[str, str]] = {}
    for (record, stage), row in latest.items():
        if record not in result or order[stage] >= order[result[record][0]]:
            result[record] = (stage, row["decision"])
    return result


def validate(args: argparse.Namespace) -> tuple[list[str], list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    notes: list[str] = []
    root = args.root.resolve()
    for manifest in args.manifest:
        found_errors, found_notes = check_manifest(manifest, root)
        errors += found_errors
        notes += found_notes

    records = corpus_records(args.corpus)
    ids = set().union(*records)
    if args.corpus:
        notes.append(f"corpus: {len(records)} registered records, {len(ids)} identifiers (PMIDs, DOIs, and local IDs)")

    decisions: dict[str, tuple[str, str]] = {}
    if args.screening:
        latest, ledger_errors = read_ledger(args.screening)
        errors += ledger_errors
        decisions = final_decisions(latest)
        tally: dict[str, int] = {}
        for stage, decision in decisions.values():
            tally[f"{stage}:{decision}"] = tally.get(f"{stage}:{decision}", 0) + 1
        notes.append("screening (latest decision per record): " + (", ".join(f"{k}={v}" for k, v in sorted(tally.items())) or "none"))
        if ids:
            pending = [record for record in records if not record & set(decisions)]
            notes.append(f"corpus records without any screening decision (pending, not excluded): {len(pending)}")
            unknown = set(decisions) - ids
            for record in sorted(unknown):
                errors.append(f"{args.screening}: decision for {record}, which is not in the corpus")

    for strict, files in ((True, args.claims), (False, args.check)):
        for path in files:
            text = path.read_text(encoding="utf-8")
            for number, line in enumerate(text.splitlines(), 1):
                for pattern, label in PLACEHOLDERS:
                    if pattern.search(line):
                        errors.append(f"{path}:{number}: unresolved citation placeholder ({label})")
            queries = len(REVIEW_QUERY.findall(text))
            if queries:
                notes.append(f"{path}: {queries} open [REVIEW QUERY] item(s)")
            if not ids:
                continue
            for identifier, number in sorted(cited(text, not args.no_bare_ids).items(), key=lambda item: item[1]):
                if identifier not in ids:
                    errors.append(f"{path}:{number}: {identifier} is not in the registered corpus")
                elif decisions.get(identifier, ("", ""))[1] == "exclude":
                    message = f"{path}:{number}: {identifier} is cited but its latest screening decision is exclude"
                    (errors if strict else warnings).append(message)
    return errors, warnings, notes


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="workspace root that manifest paths are relative to (default: current directory)")
    parser.add_argument("--manifest", type=Path, action="append", default=[], help="JSON/JSONL/TSV manifest with path and sha256 fields")
    parser.add_argument("--corpus", type=Path, action="append", default=[], help="retrieved or explicitly registered sources (JSON/JSONL/TSV/TXT with pmid, doi, source_id, or record_id)")
    parser.add_argument("--screening", type=Path, help="append-only screening ledger (TSV or JSONL)")
    parser.add_argument("--claims", type=Path, action="append", default=[], help="claim-evidence maps: citing an excluded record is an error")
    parser.add_argument("--check", type=Path, action="append", default=[], help="syntheses or notes: citing an excluded record is a warning")
    parser.add_argument("--no-bare-ids", action="store_true", help="do not treat bare 7-9 digit numbers as candidate PMIDs")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not (args.manifest or args.corpus or args.screening or args.claims or args.check):
        parser.error("nothing to check; pass at least one of --manifest, --corpus, --screening, --claims, --check")
    if (args.claims or args.check) and not args.corpus:
        print("NOTE: no --corpus given; only placeholders were checked in cited files")

    errors, warnings, notes = validate(args)
    for note in notes:
        print(f"NOTE: {note}")
    for warning in warnings:
        print(f"WARN: {warning}")
    for error in errors:
        print(f"FAIL: {error}")
    print(f"{len(errors)} failure(s), {len(warnings)} warning(s). Mechanical checks only; claim support and complete reading were not validated.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
