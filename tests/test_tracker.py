import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class TrackerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db_path = Path(self.tmp.name) / "tracker.sqlite"

    def run_cli(self, *args, expected_code=0):
        result = subprocess.run(
            [sys.executable, str(ROOT / "tracker.py"), "--db", str(self.db_path), *args],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, expected_code, result.stderr)
        return result.stdout if expected_code == 0 else result.stderr

    def test_add_observe_comps_assess_and_report(self):
        self.run_cli("init")
        self.run_cli(
            "add", "--source", "Zillow", "--url", "https://www.zillow.com/example-house",
            "--address", "123 Example St", "--city", "Tucson", "--state", "AZ",
            "--beds", "3", "--baths", "2", "--price", "225000",
            "--observed", "2026-10-19",
        )
        self.run_cli(
            "observe", "--listing-id", "1", "--price", "215000",
            "--observed", "2026-10-20",
        )
        for i in range(3):
            self.run_cli(
                "rent-comp", "--listing-id", "1", "--rent", str(1900 + i * 50),
                "--url", f"https://www.zillow.com/rent-example-{i}",
                "--address", f"{i} Comparable St", "--beds", "3", "--baths", "2",
                "--observed", "2026-10-19",
            )
        output = self.run_cli(
            "assess", "--listing-id", "1",
            "--input", str(ROOT / "examples" / "underwriting.json"),
        )
        self.assertIn("Rent comps recorded: 3", output)
        self.assertIn("Base cash flow", output)
        self.assertIn("Stress cash flow", output)
        self.assertIn("Tucson", self.run_cli("report"))
        record = json.loads(self.run_cli("show", "--listing-id", "1"))
        self.assertEqual(len(record["price_observations"]), 2)
        self.assertEqual(len(record["rental_comps"]), 3)
        self.assertEqual(len(record["assessments"]), 1)
        self.assertEqual(record["assessments"][0]["rent_comp_count"], 3)
        self.assertIn("monthly_cashflow_usd", json.loads(record["assessments"][0]["results_json"]))
        with sqlite3.connect(self.db_path) as c:
            self.assertEqual(c.execute("SELECT asking_price_usd FROM listings").fetchone()[0], 215000)
        snapshot = Path(self.tmp.name) / "snapshot.json"
        self.run_cli("export", "--output", str(snapshot))
        self.assertEqual(len(json.loads(snapshot.read_text())["rental_comps"]), 3)
        original_db = self.db_path
        self.db_path = Path(self.tmp.name) / "restored.sqlite"
        try:
            self.run_cli("init")
            self.run_cli("import", "--input", str(snapshot))
            restored = json.loads(self.run_cli("show", "--listing-id", "1"))
            self.assertEqual(len(restored["price_observations"]), 2)
            self.assertEqual(len(restored["assessments"]), 1)
            self.assertIn("WATCH", self.run_cli("report"))
        finally:
            self.db_path = original_db

    def test_property_filter_rejects_ineligible(self):
        self.run_cli("init")
        error = self.run_cli(
            "add", "--source", "Redfin", "--url", "https://www.redfin.com/invalid",
            "--address", "1 Sample", "--city", "Spokane", "--state", "WA",
            "--beds", "4", "--baths", "2", "--price", "200000",
            expected_code=2,
        )
        self.assertIn("only detached", error)
        with sqlite3.connect(self.db_path) as c:
            self.assertEqual(c.execute("SELECT count(*) FROM listings").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
