"""Synthetic corpus-validator tests; no literature or live review is tested."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_corpus.py"
SPEC = importlib.util.spec_from_file_location("honeybee_validate_corpus", SCRIPT)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)

LEDGER_HEADER = "record_id\tstage\tdecision\tprimary_reason_id\tpassage_locator\treviewer_id\ttimestamp\n"


class CorpusChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.corpus = self.write("sources/abstracts.json", json.dumps([
            {"pmid": "11553778", "doi": "10.1073/pnas.191327798"},
            {"pmid": "35229935", "doi": None},
        ]))

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def run_checks(self, *argv):
        args = ["--root", str(self.root), "--corpus", str(self.corpus), *map(str, argv)]
        return VALIDATOR.validate(VALIDATOR.build_parser().parse_args(args))

    def manifest(self, entries):
        return self.write("sources/manifest.json", json.dumps(entries))

    def test_matching_manifest_passes(self):
        digest = hashlib.sha256(self.corpus.read_bytes()).hexdigest()
        manifest = self.manifest([{"path": "sources/abstracts.json", "sha256": digest}])
        errors, _, _ = self.run_checks("--manifest", manifest)
        self.assertEqual(errors, [])

    def test_hash_mismatch_and_missing_file_fail(self):
        manifest = self.manifest([
            {"path": "sources/abstracts.json", "sha256": "0" * 64},
            {"path": "sources/absent.json", "sha256": "0" * 64},
        ])
        errors, _, _ = self.run_checks("--manifest", manifest)
        self.assertTrue(any("hash mismatch" in error for error in errors))
        self.assertTrue(any("missing file" in error for error in errors))

    def test_manifest_listing_itself_fails(self):
        manifest = self.manifest([{"path": "sources/manifest.json", "sha256": "0" * 64}])
        errors, _, _ = self.run_checks("--manifest", manifest)
        self.assertTrue(any("lists itself" in error for error in errors))

    def test_in_corpus_citations_pass(self):
        note = self.write("notes/synthesis.md", "CPP in zebrafish (PMID 11553778; doi:10.1073/PNAS.191327798).\n| 35229935 | ethanol |\n")
        errors, _, _ = self.run_checks("--check", note)
        self.assertEqual(errors, [])

    def test_out_of_corpus_citation_fails(self):
        note = self.write("notes/synthesis.md", "| 22419037 | comparator |\nSee PMID: 99999.\n")
        errors, _, _ = self.run_checks("--check", note)
        self.assertTrue(any("22419037 is not in the registered corpus" in error for error in errors))
        self.assertTrue(any("99999 is not in the registered corpus" in error for error in errors))

    def test_bare_numbers_can_be_ignored(self):
        note = self.write("notes/synthesis.md", "Sample of 12345678 reads.\n")
        errors, _, _ = self.run_checks("--check", note, "--no-bare-ids")
        self.assertEqual(errors, [])

    def test_placeholders_fail(self):
        note = self.write("notes/synthesis.md", "42036732-like\n26993913 (?)\nTwo-choice??\nPMID: TBD\n")
        errors, _, _ = self.run_checks("--check", note)
        self.assertEqual(sum("placeholder" in error for error in errors), 4)

    def test_review_query_is_reported_not_failed(self):
        note = self.write("notes/synthesis.md", "Dose [REVIEW QUERY: not in abstract].\n")
        errors, _, notes = self.run_checks("--check", note)
        self.assertEqual(errors, [])
        self.assertTrue(any("REVIEW QUERY" in item for item in notes))

    def test_excluded_record_cited_in_claims_fails_and_in_notes_warns(self):
        ledger = self.write("records/screening.tsv", LEDGER_HEADER
                            + "11553778\ttitle_abstract\texclude\tC2\tabstract s2\tcoordinator\t2026-10-17T10:00-05:00\n")
        claims = self.write("notes/claims.md", "PMID 11553778\n")
        errors, warnings, _ = self.run_checks("--screening", ledger, "--claims", claims, "--check", claims)
        self.assertTrue(any("latest screening decision is exclude" in error for error in errors))
        self.assertTrue(any("latest screening decision is exclude" in warning for warning in warnings))

    def test_ledger_uses_latest_row_and_most_advanced_stage(self):
        ledger = self.write("records/screening.tsv", LEDGER_HEADER
                            + "11553778\ttitle_abstract\tuncertain\t\t\tcoordinator\tt1\n"
                            + "11553778\ttitle_abstract\tadvance\t\tresults\tcoordinator\tt2\n"
                            + "11553778\tfull_text\tinclude\t\tmethods p3\tcoordinator\tt3\n")
        errors, _, notes = self.run_checks("--screening", ledger)
        self.assertEqual(errors, [])
        self.assertTrue(any("full_text:include=1" in item for item in notes))
        self.assertTrue(any("pending, not excluded): 1" in item for item in notes))

    def test_ledger_rejects_bad_rows(self):
        ledger = self.write("records/screening.tsv", LEDGER_HEADER
                            + "11553778\ttitle_abstract\texclude\t\t\tcoordinator\tt1\n"
                            + "35229935\ttitle_abstract\tskip\t\t\tcoordinator\tt1\n"
                            + "35229935\ttitle_abstract\tadvance\t\t\t\tt1\n"
                            + "77777777\ttitle_abstract\tadvance\t\t\tcoordinator\tt1\n")
        errors, _, _ = self.run_checks("--screening", ledger)
        self.assertTrue(any("without primary_reason_id" in error for error in errors))
        self.assertTrue(any("'skip' not in" in error for error in errors))
        self.assertTrue(any("missing reviewer_id" in error for error in errors))
        self.assertTrue(any("77777777, which is not in the corpus" in error for error in errors))

    def test_jsonl_ledger_and_tsv_corpus(self):
        self.corpus = self.write("sources/records.tsv", "pmid\ttitle\nNA\tLiteral gene symbol record\n11553778\tCPP\n")
        ledger = self.write("records/screening.jsonl", json.dumps({
            "record_id": "NA", "stage": "title_abstract", "decision": "advance",
            "reviewer_id": "coordinator", "timestamp": "t1"}) + "\n")
        errors, _, _ = self.run_checks("--screening", ledger)
        self.assertEqual(errors, [])

    def test_entries_wrapper_is_read_as_records(self):
        self.corpus = self.write("sources/fulltext_plan.json", json.dumps(
            {"created": "t", "counts": {}, "entries": [{"pmid": "11553778"}, {"pmid": "35229935"}]}))
        ledger = self.write("records/screening.tsv", LEDGER_HEADER
                            + "11553778\ttitle_abstract\tadvance\t\t\tcoordinator\tt1\n")
        errors, _, notes = self.run_checks("--screening", ledger)
        self.assertEqual(errors, [])
        self.assertTrue(any("2 registered records" in item for item in notes))
        self.assertTrue(any("pending, not excluded): 1" in item for item in notes))

    def test_cli_exit_codes(self):
        bad = self.write("notes/synthesis.md", "PMID 22419037\n")
        result = subprocess.run([sys.executable, str(SCRIPT), "--corpus", str(self.corpus), "--check", str(bad)],
                                cwd=self.temp.name, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("claim support and complete reading were not validated", result.stdout)
        good = self.write("notes/ok.md", "PMID 11553778\n")
        result = subprocess.run([sys.executable, str(SCRIPT), "--corpus", str(self.corpus), "--check", str(good)],
                                cwd=self.temp.name, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
