"""Synthetic package-checker tests; no literature or live review is tested."""

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_skill.py"
SPEC = importlib.util.spec_from_file_location("honeybee_check_skill", SCRIPT)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "honeybee-lit"
        self.root.mkdir()
        self.skill = self.root / "SKILL.md"
        self.skill.write_text(
            "---\nname: honeybee-lit\ndescription: Review scientific literature.\nmetadata:\n  version: \"test\"\n---\n\n# Honeybee lit\n",
            encoding="utf-8",
        )
        (self.root / "README.md").write_text("# Synthetic fixture\n", encoding="utf-8")

    def append(self, text):
        with self.skill.open("a", encoding="utf-8") as handle:
            handle.write(text)

    def errors(self):
        return CHECKER.check_skill(self.root)

    def test_minimal_package_passes(self):
        self.assertEqual(self.errors(), [])

    def test_missing_local_link_fails(self):
        self.append("\n[Missing](references/not-present.md)\n")
        self.assertTrue(any("missing local target" in error for error in self.errors()))

    def test_valid_local_link_and_anchor_pass(self):
        self.append("\n[Readme](README.md#synthetic-fixture)\n")
        self.assertEqual(self.errors(), [])

    def test_link_outside_package_fails(self):
        self.append("\n[Outside](../outside.md)\n")
        self.assertTrue(any("escapes package" in error for error in self.errors()))

    def test_invalid_name_fails(self):
        self.skill.write_text(self.skill.read_text().replace("name: honeybee-lit", "name: Honeybee--Lit"))
        self.assertTrue(any("invalid or missing name" in error for error in self.errors()))

    def test_wrong_directory_name_fails(self):
        self.skill.write_text(self.skill.read_text().replace("name: honeybee-lit", "name: another-skill"))
        self.assertTrue(any("match the package directory" in error for error in self.errors()))

    def test_missing_description_fails(self):
        self.skill.write_text(self.skill.read_text().replace("description: Review scientific literature.", "description: ''"))
        self.assertTrue(any("description" in error for error in self.errors()))

    def test_duplicate_frontmatter_field_fails(self):
        self.skill.write_text(self.skill.read_text().replace("name: honeybee-lit", "name: honeybee-lit\nname: honeybee-lit"))
        self.assertTrue(any("duplicate top-level field" in error for error in self.errors()))

    def test_unclosed_code_fence_fails(self):
        self.append("\n```text\nSynthetic example\n")
        self.assertTrue(any("unclosed code fence" in error for error in self.errors()))

    def test_protected_text_is_not_rewritten_or_flagged(self):
        self.append("\n> Verbatim source \u2014 preserve it.\n\n```text\n[not-a-link](absent.md) \u2014\n```\n\nInline `\u2014` and numeric 1\u20132.\n")
        self.assertEqual(self.errors(), [])

    def test_rhetorical_dash_and_curly_quote_fail(self):
        self.append("\nEditable prose \u2014 with \u201ctypographic quotes\u201d.\n")
        self.assertTrue(any("editable prose" in error for error in self.errors()))

    def test_inline_code_local_link_not_flagged(self):
        self.append("\nLiteral `[example](missing.md)` in backticks is protected.\n")
        self.assertEqual(self.errors(), [])

    def test_local_link_outside_inline_code_still_fails(self):
        self.append("\n[Missing](references/not-present.md) outside backticks.\n")
        self.assertTrue(any("missing local target" in error for error in self.errors()))

    def test_cli_from_another_directory(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.root)],
            cwd=self.temp.name,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("not validated", result.stdout)


if __name__ == "__main__":
    unittest.main()
