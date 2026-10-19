import unittest
from dataclasses import replace

from cashflow import Inputs, monthly_payment, underwrite


def scenario(**overrides):
    values = dict(
        purchase_price_usd=225000.0,
        monthly_rent_usd=1900.0,
        down_payment_fraction=0.30,
        annual_interest_rate=0.0775,
        loan_years=30,
        annual_property_tax_usd=1800.0,
        annual_insurance_usd=1800.0,
        monthly_hoa_usd=0.0,
        reserves_usd=25000.0,
        upfront_repairs_usd=5000.0,
    )
    values.update(overrides)
    return Inputs(**values)


class CashflowTests(unittest.TestCase):
    def test_amortization_known_value(self):
        self.assertAlmostEqual(monthly_payment(100000, 0.06, 30), 599.55, places=2)
        self.assertAlmostEqual(monthly_payment(120000, 0, 30), 333.333333333, places=5)
        self.assertEqual(monthly_payment(0, 0.08, 30), 0)

    def test_all_cash_and_zero_expenses(self):
        p = scenario(
            purchase_price_usd=200000, monthly_rent_usd=2000,
            down_payment_fraction=1.0, annual_interest_rate=0,
            annual_property_tax_usd=0, annual_insurance_usd=0,
            management_fraction=0, vacancy_fraction=0,
            maintenance_fraction=0, capex_fraction=0,
            upfront_repairs_usd=0, reserves_usd=0,
        )
        r = underwrite(p)
        self.assertEqual(r["loan_usd"], 0)
        self.assertEqual(r["monthly_noi_usd"], 2000)
        self.assertEqual(r["monthly_cashflow_usd"], 2000)
        self.assertIsNone(r["dscr"])
        self.assertIsNone(r["max_purchase_price_for_target_usd"])

    def test_noi_excludes_capex_but_cashflow_includes_it(self):
        p = scenario(
            purchase_price_usd=200000, monthly_rent_usd=2000,
            down_payment_fraction=1, annual_interest_rate=0,
            annual_property_tax_usd=1200, annual_insurance_usd=1200,
            management_fraction=0.10, vacancy_fraction=0.05,
            maintenance_fraction=0.05, capex_fraction=0.05,
        )
        r = underwrite(p)
        self.assertAlmostEqual(r["monthly_operating_expenses_usd"], 600)
        self.assertAlmostEqual(r["monthly_noi_usd"], 1400)
        self.assertAlmostEqual(r["monthly_capex_reserve_usd"], 100)
        self.assertAlmostEqual(r["monthly_cashflow_usd"], 1300)

    def test_target_rent_reproduces_target_cashflow(self):
        p = scenario()
        rent_needed = underwrite(p)["required_monthly_rent_for_target_usd"]
        r = underwrite(replace(p, monthly_rent_usd=rent_needed))
        self.assertAlmostEqual(r["monthly_cashflow_usd"], p.target_monthly_cashflow_usd, places=5)

    def test_maximum_price_is_a_math_ceiling_not_a_valuation(self):
        p = scenario()
        max_price = underwrite(p)["max_purchase_price_for_target_usd"]
        self.assertIsNotNone(max_price)
        self.assertGreater(max_price, 0)
        r = underwrite(replace(p, purchase_price_usd=max_price))
        self.assertAlmostEqual(r["monthly_cashflow_usd"], p.target_monthly_cashflow_usd, places=5)

    def test_combined_downside_scenario(self):
        p = scenario()
        r = underwrite(p)
        self.assertEqual(r["stress_rent_usd"], p.monthly_rent_usd * 0.90)
        self.assertGreaterEqual(r["stress_vacancy_fraction"], 1 / 12)
        self.assertLess(r["stress_monthly_cashflow_usd"], r["monthly_cashflow_usd"])

    def test_invalid_inputs_rejected(self):
        for p in (
            scenario(monthly_rent_usd=-1),
            scenario(down_payment_fraction=1.01),
            scenario(management_fraction=0.8, vacancy_fraction=0.3),
            scenario(loan_years=0),
            scenario(annual_interest_rate=float("nan")),
        ):
            with self.subTest(p=p), self.assertRaises(ValueError):
                underwrite(p)


if __name__ == "__main__":
    unittest.main()
