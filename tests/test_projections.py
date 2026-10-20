"""Conservative 5/10-year return model and CLI database regression tests."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from cashflow import Inputs, underwrite
from projections import (
    PROFILES, compare_scenarios, irr, project
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "underwriting.json"


class ProjectionMathTests(unittest.TestCase):
    def setUp(self):
        self.p = Inputs(**json.loads(EXAMPLE.read_text(encoding="utf-8")))

    def test_first_year_zero_appreciation_no_refinancing(self):
        for name in ("guarded_base", "limited_upside"):
            for years in (5, 10):
                with self.subTest(name=name, years=years):
                    r = project(self.p, name, years)
                    self.assertEqual(r["year_1_home_value_change_pct"], 0)
                    self.assertEqual(r["yearly_details"][0]["year_end_property_value_usd"],
                                     self.p.purchase_price_usd)
                    self.assertEqual(r["mortgage_rate_assumed_fixed_no_refinance"],
                                     self.p.annual_interest_rate)
                    self.assertEqual(len(r["yearly_details"]), years)
        self.assertEqual(PROFILES["guarded_base"].home_price_change[1], 0)
        self.assertLess(project(self.p, "downside", 5)["year_1_home_value_change_pct"], 0)

    def test_year_one_cashflow_reconciles_with_original_model(self):
        projection = project(self.p, "guarded_base", 5)
        original = underwrite(self.p)
        self.assertAlmostEqual(
            projection["year_1_monthly_cashflow_usd"],
            original["monthly_cashflow_usd"], places=6
        )

    def test_balance_principal_and_sales_accounting(self):
        r = project(self.p, "guarded_base", 5)
        principal = r["cumulative_principal_paid_usd"]
        self.assertAlmostEqual(
            r["outstanding_loan_at_sale_usd"] + principal, underwrite(self.p)["loan_usd"], places=5
        )
        self.assertAlmostEqual(
            r["net_sale_proceeds_including_returned_initial_reserves_usd"],
            r["sale_property_value_usd"] - r["selling_transaction_cost_usd"]
            - r["outstanding_loan_at_sale_usd"] + self.p.reserves_usd,
            places=6
        )
        self.assertAlmostEqual(
            r["annual_investor_cashflows_usd"][0],
            -underwrite(self.p)["cash_needed_usd"]
        )
        self.assertEqual(len(r["annual_investor_cashflows_usd"]), 6)

    def test_downside_has_more_negative_cash_exposure(self):
        base = project(self.p, "guarded_base", 5)
        bad = project(self.p, "downside", 5)
        self.assertLess(bad["sale_property_value_usd"], base["sale_property_value_usd"])
        self.assertGreaterEqual(bad["first_24_months_cash_support_usd"],
                                base["first_24_months_cash_support_usd"])
        self.assertLess(bad["year_1_monthly_cashflow_usd"], base["year_1_monthly_cashflow_usd"])
        self.assertEqual(bad["year_1_home_value_change_pct"], -6)

    def test_irr_on_known_cashflows_and_hurdle(self):
        self.assertAlmostEqual(irr([-100,110]), 0.1, places=10)
        self.assertAlmostEqual(irr([-100,0,121]), 0.1, places=10)
        self.assertIsNone(irr([100,10]))
        r=project(self.p,"guarded_base",5,nominal_hurdle=.08)
        self.assertAlmostEqual(
            sum(c / 1.08 ** i for i,c in enumerate(r["annual_investor_cashflows_usd"])),
            r["npv_at_illustrative_hurdle_usd"], places=5
        )

    def test_reject_bad_inputs_and_no_magic_rate_reduction(self):
        for kw in (
            {"years": 4}, {"scenario": "optimistic_refi"},
            {"selling_cost_fraction": -0.1}, {"inflation_for_real_return": 1.5}
        ):
            with self.assertRaises(ValueError):
                project(self.p, **kw)
        higher = Inputs(**{**vars(self.p), "annual_interest_rate": .09})
        self.assertLess(project(higher,"guarded_base",5)["year_1_monthly_cashflow_usd"],
                        project(self.p,"guarded_base",5)["year_1_monthly_cashflow_usd"])
        all_outcomes=compare_scenarios(self.p)
        self.assertEqual(set(all_outcomes["outcomes"]), set(PROFILES))
        self.assertEqual(set(all_outcomes["outcomes"]["downside"]), {"5","10"})


class ProjectionCliTests(unittest.TestCase):
    def test_project_sqlite_snapshot_roundtrip(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td)/"property.sqlite"
            case = ROOT/"research"/"cases"/"2026-10-19_4222-Union-Hill-Ct.json"
            fixture = json.loads(case.read_text())
            args_path = Path(td)/"underwriting.json"
            args_path.write_text(json.dumps(fixture["underwriting_inputs"]))
            def run(*argv):
                p=subprocess.run(
                    [sys.executable,str(ROOT/"tracker.py"),"--db",str(db),*argv],
                    cwd=ROOT,capture_output=True,text=True
                )
                self.assertEqual(p.returncode,0,p.stderr)
                return p.stdout
            run("init")
            item=fixture["listing"]
            run("add","--source","Zillow","--url",item["url"],
                "--address",item["address"],"--city",item["city"],"--state",item["state"],
                "--beds","3","--baths","2","--sqft","1099",
                "--price",str(item["asking_price_usd"]))
            out=run("project","--listing-id","1","--input",str(args_path),
                    "--rent-source","advertised_comps")
            self.assertIn("guarded_base",out)
            self.assertIn("downside",out)
            self.assertIn("10Y",out)
            show=json.loads(run("show","--listing-id","1"))
            self.assertEqual(len(show["projections"]),1)
            latest=json.loads(show["projections"][0]["results_json"])
            self.assertEqual(latest["rent_evidence_type"],"advertised_comps")
            self.assertLess(latest["outcomes"]["guarded_base"]["5"]["year_1_monthly_cashflow_usd"], 0)
            snapshot = Path(td)/"snapshot.json"
            run("export","--output",str(snapshot))
            snap=json.loads(snapshot.read_text())
            self.assertEqual(len(snap["projections"]),1)
            restored=db
            db=Path(td)/"copy.sqlite"
            run("init")
            run("import","--input",str(snapshot))
            restored_show=json.loads(run("show","--listing-id","1"))
            self.assertEqual(len(restored_show["projections"]),1)
            db=restored


if __name__ == "__main__":
    unittest.main()
