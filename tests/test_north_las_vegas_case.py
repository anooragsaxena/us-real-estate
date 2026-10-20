"""North Las Vegas research case: real sourced URLs + deterministic CLI regression.

Does not scrape websites or claim actual lease rent. All values are dated
research observations and hypothetical financing. No sale is marked verified
absent documentary confirmation of distance and arm's-length terms.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CASE_PATH = ROOT / "research" / "cases" / "2026-10-19_4222-Union-Hill-Ct.json"


class NorthLasVegasTest(unittest.TestCase):
    def test_property_sale_and_rental_screen(self):
        case = json.loads(CASE_PATH.read_text(encoding="utf-8"))
        listing = case["listing"]
        self.assertEqual((listing["bedrooms"], listing["bathrooms"]), (3, 2))
        self.assertEqual(listing["property_type"], "detached_sfh")
        self.assertIsNone(listing["current_contract_rent_usd"])

        with tempfile.TemporaryDirectory() as folder:
            db = Path(folder) / "research.sqlite"
            inputs_file = Path(folder) / "underwriting.json"
            export_file = Path(folder) / "snapshot.json"
            inputs_file.write_text(json.dumps(case["underwriting_inputs"]), encoding="utf-8")

            def run(*args):
                process = subprocess.run(
                    [sys.executable, str(ROOT / "tracker.py"),
                     "--db", str(db), *args],
                    cwd=ROOT, capture_output=True, text=True,
                )
                self.assertEqual(process.returncode, 0, process.stderr)
                return process.stdout

            run("init")
            run(
                "add", "--source", listing["source"], "--url", listing["url"],
                "--address", listing["address"], "--city", listing["city"],
                "--state", listing["state"], "--zip", listing["zip_code"],
                "--beds", str(listing["bedrooms"]), "--baths", str(listing["bathrooms"]),
                "--sqft", str(listing["finished_sqft"]),
                "--year-built", str(listing["year_built"]),
                "--price", str(listing["asking_price_usd"]),
                "--observed", case["as_of"],
                "--notes", "Six-year tenant disclosed; actual lease terms and collected rent unknown.",
            )

            for comp in case["rental_comps"]:
                run(
                    "rent-comp", "--listing-id", "1",
                    "--rent", str(comp["asking_rent_usd"]),
                    "--url", comp["source_url"], "--address", comp["address"],
                    "--beds", str(comp["bedrooms"]), "--baths", str(comp["bathrooms"]),
                    "--observed", comp["observed_on"], "--notes", comp["notes"],
                )

            # Only this comp has independently sourced distance. Neither
            # recorder-confirmed closing nor arm's-length status is asserted.
            comp = case["sale_comps_preliminary"][0]
            run(
                "sale-comp", "--listing-id", "1", "--url", comp["source_url"],
                "--address", comp["address"], "--price", str(comp["sold_price_usd"]),
                "--sold-on", comp["sold_on"], "--beds", str(comp["bedrooms"]),
                "--baths", str(comp["bathrooms"]), "--sqft", str(comp["finished_sqft"]),
                "--distance", str(comp["distance_miles"]), "--transaction", "unknown",
                "--observed", case["as_of"],
                "--notes", "Preliminary neighborhood sale; not recorder or arm's-length verified.",
            )
            for item in case["assumptions_and_flags"]:
                run(
                    "finding", "--listing-id", "1",
                    "--category", item["category"],
                    "--severity", item["severity"],
                    "--evidence", item["evidence_status"],
                    "--description", item["description"],
                    "--url", item["source_url"], "--observed", case["as_of"],
                )

            cli_output = run(
                "assess", "--listing-id", "1", "--input", str(inputs_file),
                "--scenario", "base-market-rent-not-actual-lease",
            )
            self.assertIn("WATCH", cli_output)
            self.assertIn("Rent comps recorded: 3", cli_output)
            self.assertIn("Neighborhood sold comps screen-qualified: 0", cli_output)
            self.assertIn("Open high/critical findings: 1", cli_output)
            self.assertIn("WATCH", run("report"))
            run("export", "--output", str(export_file))
            snapshot = json.loads(export_file.read_text(encoding="utf-8"))
            self.assertEqual(len(snapshot["listings"]), 1)
            self.assertEqual(len(snapshot["rental_comps"]), 3)
            self.assertEqual(len(snapshot["sale_comps"]), 1)
            self.assertEqual(len(snapshot["findings"]), 3)
            self.assertEqual(len(snapshot["assessments"]), 1)
            assessment = snapshot["assessments"][0]
            self.assertEqual(assessment["screen_status"], "WATCH")
            result = json.loads(assessment["results_json"])
            self.assertAlmostEqual(result["monthly_debt_service_usd"], 1629.27619, places=2)
            self.assertAlmostEqual(result["monthly_noi_usd"], 1067.5, places=2)
            self.assertAlmostEqual(result["monthly_cashflow_usd"], -649.27619, places=2)
            self.assertAlmostEqual(result["stress_monthly_cashflow_usd"], -834.77619, places=2)
            self.assertAlmostEqual(result["required_monthly_rent_for_target_usd"], 2933.25815, places=2)
            self.assertAlmostEqual(result["max_purchase_price_for_target_usd"], 145566.62722, places=2)
            self.assertAlmostEqual(result["cash_needed_usd"], 140461.92, places=2)
            self.assertEqual(result["sale_comparison"]["screen_qualified_sale_comps"], 0)
            self.assertEqual(result["unresolved_high_or_critical_findings"], 1)


if __name__ == "__main__":
    unittest.main()
