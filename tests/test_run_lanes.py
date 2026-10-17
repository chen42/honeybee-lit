"""Synthetic lane-runner tests; fake commands stand in for retrieval tools."""

import json
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import time
import unittest

sys.dont_write_bytecode = True
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_lanes.py"
PY = shlex.quote(sys.executable)

# A fake tool: query "fail" exits 1 with a URL containing a key, "slow" sleeps,
# "apierror" writes an error object, anything else writes three IDs.
FAKE_TOOL = """
import json, sys, time
out, query = sys.argv[1], sys.argv[2]
if query == "fail":
    print("Network error fetching https://x/esearch.fcgi?email=a%40b&api_key=SECRET123&term=q")
    sys.exit(1)
if query == "slow":
    time.sleep(30)
json.dump({"error": "bad"} if query == "apierror" else ["1", "2", "3"], open(out, "w"))
"""


class LaneRunner(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.tool = self.root / "tool.py"
        self.tool.write_text(FAKE_TOOL, encoding="utf-8")

    def run_lanes(self, queries, *extra):
        lanes = self.root / "lanes.tsv"
        lanes.write_text("lane\tquery\n" + "".join(f"L{i}\t{q}\n" for i, q in enumerate(queries, 1)), encoding="utf-8")
        command = f"{PY} {shlex.quote(str(self.tool))} {{out}} {{query}}"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(lanes), "--command", command, "--out-dir", str(self.root / "searches"), *extra],
            capture_output=True, text=True, check=False, timeout=60)
        summary = json.loads((self.root / "searches" / "lanes_summary.json").read_text())
        return result, {lane["lane"]: lane for lane in summary["lanes"]}, summary

    def test_all_lanes_ok(self):
        result, lanes, _ = self.run_lanes(["a", "b"])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual({lane["status"] for lane in lanes.values()}, {"ok"})
        self.assertEqual(lanes["L1"]["returned"], 3)
        self.assertIn("[search] 2/2 lanes", result.stdout)

    def test_failure_is_isolated_and_log_redacted(self):
        result, lanes, _ = self.run_lanes(["fail", "b"])
        self.assertEqual(result.returncode, 1)
        self.assertEqual(lanes["L1"]["status"], "failed")
        self.assertEqual(lanes["L2"]["status"], "ok")
        log = Path(lanes["L1"]["log"]).read_text()
        self.assertNotIn("SECRET123", log + result.stdout + lanes["L1"]["error"])
        self.assertIn("api_key=REDACTED", log)
        self.assertIn("rerun only those lanes", result.stdout)

    def test_api_error_object_is_not_zero_hits(self):
        _, lanes, _ = self.run_lanes(["apierror"])
        self.assertEqual(lanes["L1"]["status"], "failed")
        self.assertIsNone(lanes["L1"]["returned"])

    def test_timeout_does_not_block_other_lanes(self):
        start = time.monotonic()
        result, lanes, _ = self.run_lanes(["slow", "a", "b"], "--timeout", "2", "--jobs", "3")
        self.assertLess(time.monotonic() - start, 20)
        self.assertEqual(lanes["L1"]["status"], "timeout")
        self.assertEqual(lanes["L2"]["status"], "ok")
        self.assertEqual(result.returncode, 1)

    def test_lanes_run_concurrently(self):
        slow_ok = self.root / "slow_ok.py"
        slow_ok.write_text("import json,sys,time\ntime.sleep(1.5)\njson.dump([1], open(sys.argv[1],'w'))\n")
        self.tool = slow_ok
        start = time.monotonic()
        result, lanes, _ = self.run_lanes(["a", "b", "c"], "--jobs", "3")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertLess(time.monotonic() - start, 4.0)

    def test_failed_preflight_launches_nothing(self):
        result, lanes, summary = self.run_lanes(["a", "b"], "--preflight", f"{PY} -c 'import sys; sys.exit(3)'")
        self.assertEqual(result.returncode, 2)
        self.assertEqual(summary["preflight"]["status"], "failed")
        self.assertEqual({lane["status"] for lane in lanes.values()}, {"not run"})
        self.assertFalse((self.root / "searches" / "L1_results.json").exists())

    def test_hung_preflight_times_out(self):
        start = time.monotonic()
        result, _, summary = self.run_lanes(["a"], "--preflight", f"{PY} -c 'import time; time.sleep(30)'", "--preflight-timeout", "1")
        self.assertLess(time.monotonic() - start, 15)
        self.assertEqual(result.returncode, 2)
        self.assertIn("timed out", summary["preflight"]["detail"])


if __name__ == "__main__":
    unittest.main()
