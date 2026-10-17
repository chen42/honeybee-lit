"""Synthetic full-text planner tests; fake backends stand in for wasp-lit routes."""

import csv
import hashlib
import importlib.util
import io
import json
from contextlib import redirect_stdout
from pathlib import Path
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "fetch_fulltext.py"
SPEC = importlib.util.spec_from_file_location("honeybee_fetch_fulltext", SCRIPT)
FT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(FT)

LINKS = {
    "1": {"candidate_pmcids": ["11"], "europepmc": {"isOpenAccess": "Y", "doi": "10.1/a"}},
    "2": {"candidate_pmcids": ["22"], "europepmc": {"isOpenAccess": "N", "doi": "10.1/b"}},
    "3": {"candidate_pmcids": [], "europepmc": {"status": "not found"}},
    "4": {"candidate_pmcids": [], "europepmc": {"status": "not found"}},
}
OPENALEX = {"3": {"status": "ok", "is_oa": True, "oa_status": "hybrid", "doi": "10.1/c", "oa_url": "https://pub/c.pdf"},
            "4": {"status": "ok", "is_oa": False, "oa_status": "closed", "doi": "10.1/d"}}


class FakeBackend:
    def links(self, pmid):
        if pmid == "9":
            raise RuntimeError("elink failed api_key=SECRET")
        return json.loads(json.dumps(LINKS[pmid]))

    def fulltext(self, pmid, links):
        if pmid == "1":
            return {"status": "retrieved", "provider": "pmc-efetch", "attempts": [{"provider": "pmc-efetch", "status": "retrieved"}],
                    "document": {"raw": "<article>body</article>", "pmcid": "PMC11", "license": "CC BY",
                                 "passages": [{"tag": "p", "text": "Fish pressed the lever."}]}}
        # Restricted PMC article: efetch errors, Europe PMC 500, BioC rate-limited.
        return {"status": "failed", "attempts": [
            {"provider": "pmc-efetch", "status": "error", "error": "HTTP Error 502"},
            {"provider": "europepmc", "status": "error", "error": "HTTP Error 500: Internal Server Error"},
            {"provider": "pmc-bioc", "status": "error", "error": "HTTP Error 429"}]}


class FullTextChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.out = self.root / "ft"

    def run_main(self, *argv, pmids=("1", "2", "3", "4")):
        path = self.root / "pmids.json"
        path.write_text(json.dumps(list(pmids)))
        argv = [a if a != "PMIDS" else str(path) for a in argv]
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = FT.main(["--out", str(self.out), "--jobs", "2", *argv], factory=FakeBackend,
                           lookup=lambda pmid: OPENALEX.get(pmid, {"status": "error"}))
        return code, buffer.getvalue()

    def needs_user(self):
        with (self.out / "needs_user.tsv").open() as handle:
            return {row["pmid"]: row for row in csv.DictReader(handle, delimiter="\t")}

    def test_classify(self):
        self.assertEqual(FT.classify(None, None), "lookup_failed")
        self.assertEqual(FT.classify(LINKS["1"], None), "pmc_open_access")
        self.assertEqual(FT.classify(LINKS["2"], None), "pmc_restricted")
        self.assertEqual(FT.classify({"candidate_pmcids": ["5"], "europepmc": {"status": "error"}}, None), "pmc_access_unknown")
        self.assertEqual(FT.classify(LINKS["3"], OPENALEX["3"]), "open_elsewhere")
        self.assertEqual(FT.classify(LINKS["4"], OPENALEX["4"]), "closed")
        self.assertEqual(FT.classify(LINKS["4"], {"status": "error"}), "lookup_failed")

    def test_plan_downloads_nothing_and_asks(self):
        code, output = self.run_main("plan", "PMIDS")
        self.assertEqual(code, 0)
        plan = json.loads((self.out / "fulltext_plan.json").read_text())
        self.assertEqual(plan["counts"]["pmc_open_access"], 1)
        self.assertEqual(plan["counts"]["closed"], 1)
        self.assertFalse((self.out / "fulltext_index.json").exists())
        self.assertEqual(set(self.needs_user()), {"3", "4"})
        self.assertEqual(self.needs_user()["3"]["oa_url"], "https://pub/c.pdf")
        self.assertIn("decision needed", output)

    def test_lookup_failure_is_visible_and_redacted(self):
        code, _ = self.run_main("plan", "PMIDS", pmids=("1", "9"))
        self.assertEqual(code, 1)
        entry = json.loads((self.out / "fulltext_plan.json").read_text())["entries"][1]
        self.assertEqual(entry["category"], "lookup_failed")
        self.assertNotIn("SECRET", entry["links_error"])

    def test_fetch_saves_raw_and_passages_with_hashes(self):
        self.run_main("plan", "PMIDS")
        code, output = self.run_main("fetch")
        self.assertEqual(code, 0)
        record = json.loads((self.out / "fulltext_index.json").read_text())["1"]
        self.assertEqual(record["status"], "retrieved")
        raw = Path(record["raw_path"]).read_bytes()
        self.assertEqual(raw, b"<article>body</article>")
        self.assertEqual(record["raw_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertEqual(record["words"], 4)
        self.assertFalse(record["figures_reviewed"])
        self.assertNotIn("raw", json.loads(Path(record["parsed_path"]).read_text()))
        self.assertIn("retrieved via pmc-efetch", output)

    def test_europepmc_500_on_non_open_access_is_absence(self):
        self.run_main("plan", "PMIDS")
        code, _ = self.run_main("fetch", "--categories", "pmc_restricted")
        record = json.loads((self.out / "fulltext_index.json").read_text())["2"]
        self.assertEqual(code, 0)
        self.assertEqual(record["status"], "unavailable")
        self.assertEqual(self.needs_user()["2"]["status"], "unavailable")
        self.assertIn("europepmc", self.needs_user()["2"]["note"])

    def test_bioc_no_result_is_absence(self):
        result = FT.reclassify({"status": "failed", "attempts": [
            {"provider": "pmc-bioc", "status": "error", "error": "Failed to parse JSON response. Body: [Error] : No result can be found."}]}, {})
        self.assertEqual(result["status"], "unavailable")

    def test_errors_without_confirmed_absence_stay_failed(self):
        result = FT.reclassify({"status": "failed", "attempts": [
            {"provider": "europepmc", "status": "error", "error": "HTTP Error 500"}]}, {"isOpenAccess": "Y"})
        self.assertEqual(result["status"], "failed")

    def test_already_retrieved_is_not_overwritten(self):
        self.run_main("plan", "PMIDS")
        self.run_main("fetch")
        _, output = self.run_main("fetch")
        self.assertIn("1 already retrieved", output)

    def test_bioc_skipped_for_non_open_access_and_raw_kept(self):
        fake = self.root / "pubmed_extension.py"
        fake.write_text(
            "class BackendError(RuntimeError):\n    pass\n"
            "class PubmedBackend:\n"
            "    providers = ('pmc-efetch', 'europepmc', 'pmc-bioc')\n"
            "    def __init__(self, wrapper):\n        self.called = []\n"
            "    def fulltext(self, pmid, links):\n"
            "        return {'attempts': [self.provider_document(n, pmid, links['candidate_pmcids']) for n in self.providers]}\n"
            "    def provider_document(self, name, pmid, pmcids):\n"
            "        self.called.append(name)\n"
            "        if name == 'pmc-efetch' and pmid == '1':\n"
            "            return self.jats_attempt(name, '<article/>', pmid, pmcids, 'u')\n"
            "        return {'provider': name, 'status': 'unavailable'}\n"
            "    def jats_attempt(self, name, raw, pmid, pmcids, url):\n"
            "        return {'provider': name, 'status': 'retrieved', 'document': {}}\n")
        backend_class, _ = FT.load_backend_class(fake)
        backend = backend_class("wrapper")
        result = backend.fulltext("2", LINKS["2"])
        self.assertEqual(backend.called, ["pmc-efetch", "europepmc"])
        self.assertEqual(result["attempts"][2]["status"], "skipped")
        backend.called = []
        result = backend.fulltext("1", LINKS["1"])
        self.assertIn("pmc-bioc", backend.called)
        self.assertEqual(result["attempts"][0]["document"]["raw"], "<article/>")

    def test_register_copies_hashes_and_clears_needs_user(self):
        self.run_main("plan", "PMIDS")
        pdf = self.root / "paper.pdf"
        pdf.write_bytes(b"%PDF-1.7 synthetic")
        code, output = self.run_main("register", "--pmid", "4", "--file", str(pdf), "--origin", "UTHSC library")
        self.assertEqual(code, 0)
        record = json.loads((self.out / "fulltext_index.json").read_text())["4"]
        self.assertEqual(record["provider"], "user-supplied")
        self.assertEqual(Path(record["raw_path"]).read_bytes(), pdf.read_bytes())
        self.assertTrue(record["identity_check"].startswith("pending"))
        self.assertTrue(pdf.exists())
        self.assertNotIn("4", self.needs_user())
        self.assertIn("identity check pending", output)


if __name__ == "__main__":
    unittest.main()
