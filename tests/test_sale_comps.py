"""Neighborhood sale comp screening and end-to-end evidence-gate tests."""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from comps import sale_comps_summary


ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-10-19"


class SaleCompMathTests(unittest.TestCase):
    def setUp(self):
        self.subject = {"bedrooms": 3, "bathrooms": 2.0, "finished_sqft": 1400.0,
                        "asking_price_usd": 200000.0}

    def sample(self, id, price, **patch):
        r = dict(id=id, address=f"Comp {id}", bedrooms=3, bathrooms=2.0,
                 finished_sqft=1400.0, sold_price_usd=price,
                 sold_on="2026-08-15", sale_verified=1,
                 transaction_type="arm_length", distance_miles=0.5)
        r.update(patch)
        return r

    def test_three_closed_sales_descriptive_median(self):
        result = sale_comps_summary(
            self.subject,
            [self.sample(1, 210000), self.sample(2, 220000),
             self.sample(3, 230000)], as_of=TODAY,
        )
        self.assertEqual(result["screen_qualified_sale_comps"], 3)
        self.assertAlmostEqual(result["median_closed_price_usd_unadjusted"], 220000)
        self.assertAlmostEqual(result["median_closed_price_per_sqft_usd_unadjusted"], 220000/1400)
        self.assertAlmostEqual(result["ask_vs_median_pct"], -9.090909, places=5)
        self.assertIn("NOT fair market value", result["note"])

    def test_rejects_unverified_old_far_dissimilar_distressed(self):
        comps = [
            self.sample(1, 210000),
            self.sample(2, 240000, sale_verified=0),
            self.sample(3, 250000, sold_on="2025-01-01"),
            self.sample(4, 300000, distance_miles=9),
            self.sample(5, 200000, finished_sqft=2000),
            self.sample(6, 400000, transaction_type="distressed"),
            self.sample(7, 230000, bedrooms=2),
        ]
        result = sale_comps_summary(self.subject, comps, as_of=TODAY)
        self.assertEqual(result["screen_qualified_sale_comps"], 1)
        self.assertEqual(len(result["excluded"]), 6)
        self.assertEqual(result["median_closed_price_usd_unadjusted"], 210000)

    def test_missing_subject_size_never_qualified(self):
        subject = dict(self.subject, finished_sqft=None)
        result = sale_comps_summary(subject, [self.sample(1, 220000)], as_of=TODAY)
        self.assertEqual(result["screen_qualified_sale_comps"], 0)
        self.assertIsNone(result["median_closed_price_usd_unadjusted"])


class CliSaleEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "tracker.sqlite"

    def cli(self, *args, code=0):
        p = subprocess.run(
            [sys.executable, str(ROOT / "tracker.py"), "--db", str(self.db), *args],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(p.returncode, code, p.stderr)
        return p.stdout if code == 0 else p.stderr

    def test_neighborhood_comps_findings_and_snapshot(self):
        self.cli("init")
        self.cli("add", "--source", "Zillow", "--url", "https://www.zillow.com/test-example",
                 "--address", "100 Test St", "--city", "Tucson", "--state", "AZ",
                 "--beds", "3", "--baths", "2", "--sqft", "1400",
                 "--year-built", "1985", "--price", "200000", "--observed", TODAY)
        for i, price in enumerate([210000,220000,230000]):
            self.cli("sale-comp", "--listing-id", "1",
                     "--url", f"https://www.redfin.com/test-sold-{i}",
                     "--address", f"{i} Sold Example Rd",
                     "--price", str(price), "--sold-on", "2026-08-15",
                     "--beds", "3", "--baths", "2", "--sqft", "1400",
                     "--distance", "0.5", "--transaction", "arm_length", "--verified",
                     "--observed", TODAY)
        comp_report = self.cli("comps", "--listing-id", "1", "--as-of", TODAY)
        self.assertIn("Strict screen-qualified: 3", comp_report)
        self.assertIn("USD 220,000", comp_report)
        self.assertIn("-9.1%", comp_report)
        self.assertIn("descriptive ONLY", comp_report)
        for i in range(3):
            self.cli("rent-comp", "--listing-id", "1", "--rent", "3000",
                     "--url", f"https://www.zillow.com/test-rent-{i}",
                     "--address", f"{i} Rent Road", "--beds", "3", "--baths", "2",
                     "--observed", TODAY)

        inputs = json.loads((ROOT / "examples/underwriting.json").read_text())
        inputs.update(purchase_price_usd=200000, monthly_rent_usd=3000)
        scenario = Path(self.temp.name) / "scenario.json"
        scenario.write_text(json.dumps(inputs))
        self.assertIn("REVIEW", self.cli("assess","--listing-id","1","--input",str(scenario)))
        self.cli("finding", "--listing-id", "1",
                 "--category", "condition", "--severity", "high",
                 "--description", "Possible roof damage; only listing photos examined",
                 "--evidence", "suspected", "--observed", TODAY)
        self.assertIn("WATCH", self.cli("assess","--listing-id","1","--input",str(scenario)))
        doc = json.loads(self.cli("show", "--listing-id", "1"))
        self.assertEqual(len(doc["sale_comps"]), 3)
        self.assertEqual(len(doc["findings"]), 1)
        self.assertEqual(doc["assessments"][0]["screen_status"], "WATCH")
        self.assertEqual(doc["assessments"][1]["screen_status"], "REVIEW")
        self.assertEqual(
            json.loads(doc["assessments"][0]["results_json"])["sale_comparison"]["screen_qualified_sale_comps"], 3
        )
        snapshot = Path(self.temp.name) / "snapshot.json"
        self.cli("export", "--output", str(snapshot))
        backup = json.loads(snapshot.read_text())
        self.assertEqual(len(backup["sale_comps"]), 3)
        self.assertEqual(len(backup["findings"]), 1)

        restored_db = self.db
        self.db = Path(self.temp.name) / "restored.sqlite"
        self.cli("init")
        self.cli("import", "--input", str(snapshot))
        self.assertEqual(len(json.loads(self.cli("show","--listing-id","1"))["sale_comps"]), 3)
        self.db = restored_db

    def test_extended_radius_requires_reason(self):
        self.cli("init")
        err = self.cli("comps","--listing-id","1","--radius","3",code=2)
        self.assertIn("--radius-reason required",err)

    def test_older_database_migrates_in_place(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                "CREATE TABLE listings (id INTEGER PRIMARY KEY, source TEXT NOT NULL, "
                "url TEXT NOT NULL UNIQUE, address TEXT NOT NULL, city TEXT NOT NULL, "
                "state TEXT NOT NULL, zip_code TEXT, bedrooms INTEGER NOT NULL, "
                "bathrooms REAL NOT NULL, property_type TEXT NOT NULL DEFAULT 'detached_sfh', "
                "asking_price_usd REAL NOT NULL, listing_status TEXT NOT NULL DEFAULT 'active', "
                "observed_on TEXT NOT NULL, notes TEXT NOT NULL DEFAULT '')"
            )
        self.cli("init")
        with sqlite3.connect(self.db) as c:
            columns = {row[1] for row in c.execute("PRAGMA table_info(listings)")}
            self.assertIn("finished_sqft", columns)
            self.assertIn("year_built", columns)
            self.assertTrue(c.execute("SELECT name FROM sqlite_master WHERE name='sale_comps'").fetchone())


if __name__ == "__main__":
    unittest.main()
