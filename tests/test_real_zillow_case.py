"""Reproducible Zillow case through the real CLI and SQLite tracker.

The fixture is a dated research snapshot, not a live listing feed.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_PATH = ROOT / "research" / "cases" / "2026-10-19_2030-Pacific-Ave.json"


class ZillowCaseTest(unittest.TestCase):
    def test_zillow_sale_rent_comps_and_underwriting_end_to_end(self):
        case = json.loads(CASE_PATH.read_text(encoding="utf-8"))
        listing = case["listing"]
        self.assertEqual((listing["bedrooms"], listing["bathrooms"]), (3, 2))
        self.assertEqual(listing["property_type"], "detached_sfh")
        self.assertEqual(len(case["rental_comps"]), 3)

        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "test.sqlite"
            inputs = Path(folder) / "inputs.json"
            export = Path(folder) / "snapshot.json"
            inputs.write_text(json.dumps(case["underwriting_inputs"]), encoding="utf-8")

            def run(*args):
                done = subprocess.run(
                    [sys.executable, str(ROOT / "tracker.py"), "--db", str(db), *args],
                    cwd=ROOT, capture_output=True, text=True, check=True,
                )
                return done.stdout

            run("init")
            run(
                "add", "--source", listing["source"],
                "--url", listing["url"], "--address", listing["address"],
                "--city", listing["city"], "--state", listing["state"],
                "--zip", listing["zip_code"], "--beds", str(listing["bedrooms"]),
                "--baths", str(listing["bathrooms"]),
                "--price", str(listing["asking_price_usd"]),
                "--observed", case["observed_on"], "--notes", listing["notes"],
            )
            for c in case["rental_comps"]:
                run(
                    "rent-comp", "--listing-id", "1", "--rent", str(c["asking_rent_usd"]),
                    "--url", c["source_url"], "--address", c["address"],
                    "--beds", str(c["bedrooms"]), "--baths", str(c["bathrooms"]),
                    "--observed", case["observed_on"], "--notes", c["notes"],
                )
            assessed = run("assess", "--listing-id", "1", "--input", str(inputs), "--scenario", "base")
            self.assertIn("WATCH", assessed)
            self.assertIn("Rent comps recorded: 3", assessed)
            self.assertIn("WATCH", run("report"))
            run("export", "--output", str(export))
            snapshot = json.loads(export.read_text(encoding="utf-8"))
            self.assertEqual(len(snapshot["listings"]), 1)
            self.assertEqual(len(snapshot["rental_comps"]), 3)
            self.assertEqual(len(snapshot["assessments"]), 1)
            assessment = snapshot["assessments"][0]
            result = json.loads(assessment["results_json"])
            self.assertEqual(assessment["screen_status"], "WATCH")
            self.assertAlmostEqual(result["monthly_cashflow_usd"], -174.769, places=1)
            self.assertAlmostEqual(result["stress_monthly_cashflow_usd"], -333.769, places=1)
            self.assertAlmostEqual(result["required_monthly_rent_for_target_usd"], 2058.912, places=1)
            self.assertAlmostEqual(result["max_purchase_price_for_target_usd"], 135197.498, places=1)
            self.assertEqual(assessment["rent_comp_count"], 3)


if __name__ == "__main__":
    unittest.main()
