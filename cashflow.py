"""Deterministic USD underwriting of a long-term single-family rental.

All rates and fractions are decimal numbers: APR 0.0775 means 7.75%.
NOI excludes capex reserves and financing. Cash flow deducts both.
All calculations are pre-personal-income-tax and ignore appreciation.
"""
from dataclasses import dataclass, replace
from math import isfinite


@dataclass(frozen=True)
class Inputs:
    purchase_price_usd: float
    monthly_rent_usd: float
    down_payment_fraction: float
    annual_interest_rate: float
    loan_years: int
    annual_property_tax_usd: float
    annual_insurance_usd: float
    monthly_hoa_usd: float = 0.0
    monthly_other_usd: float = 0.0
    management_fraction: float = 0.08
    vacancy_fraction: float = 0.05
    maintenance_fraction: float = 0.06
    capex_fraction: float = 0.05
    closing_cost_fraction: float = 0.04
    upfront_repairs_usd: float = 0.0
    reserves_usd: float = 25000.0
    target_monthly_cashflow_usd: float = 250.0

    def validate(self):
        for name, value in vars(self).items():
            if not isinstance(value, (int, float)) or not isfinite(value):
                raise ValueError(f"{name} must be a finite number")
            if value < 0:
                raise ValueError(f"{name} cannot be negative")
        if self.purchase_price_usd <= 0 or self.monthly_rent_usd <= 0:
            raise ValueError("purchase price and rent must be positive")
        if not isinstance(self.loan_years, int) or self.loan_years <= 0:
            raise ValueError("loan_years must be a positive integer")
        for name in (
            "down_payment_fraction", "management_fraction", "vacancy_fraction",
            "maintenance_fraction", "capex_fraction", "closing_cost_fraction"
        ):
            if getattr(self, name) > 1:
                raise ValueError(f"{name} must be between 0 and 1")
        if (self.management_fraction + self.vacancy_fraction
                + self.maintenance_fraction + self.capex_fraction) >= 1:
            raise ValueError("combined variable allowances must be below 100%")


def monthly_payment(principal, annual_rate, years):
    """Principal-and-interest payment; supports 0% interest and all-cash."""
    if principal < 0 or annual_rate < 0 or years <= 0:
        raise ValueError("invalid mortgage terms")
    if principal == 0:
        return 0.0
    n = years * 12
    r = annual_rate / 12
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** (-n))


def _case(p):
    loan = p.purchase_price_usd * (1 - p.down_payment_fraction)
    debt_monthly = monthly_payment(loan, p.annual_interest_rate, p.loan_years)
    vacant_usd = p.monthly_rent_usd * p.vacancy_fraction
    manager_usd = p.monthly_rent_usd * p.management_fraction
    maintenance_usd = p.monthly_rent_usd * p.maintenance_fraction
    capex_usd = p.monthly_rent_usd * p.capex_fraction
    fixed_usd = (p.annual_property_tax_usd + p.annual_insurance_usd) / 12
    fixed_usd += p.monthly_hoa_usd + p.monthly_other_usd
    op_ex_usd = vacant_usd + manager_usd + maintenance_usd + fixed_usd
    noi_usd = p.monthly_rent_usd - op_ex_usd
    cf_usd = noi_usd - capex_usd - debt_monthly
    cash_needed = (
        p.purchase_price_usd * p.down_payment_fraction
        + p.purchase_price_usd * p.closing_cost_fraction
        + p.upfront_repairs_usd + p.reserves_usd
    )
    return {
        "loan_usd": loan,
        "monthly_debt_service_usd": debt_monthly,
        "monthly_effective_rent_usd": p.monthly_rent_usd - vacant_usd,
        "monthly_operating_expenses_usd": op_ex_usd,
        "monthly_noi_usd": noi_usd,
        "monthly_capex_reserve_usd": capex_usd,
        "monthly_cashflow_usd": cf_usd,
        "annual_cap_rate_pct": 100 * noi_usd * 12 / p.purchase_price_usd,
        "dscr": noi_usd / debt_monthly if debt_monthly else None,
        "cash_needed_usd": cash_needed,
        "annual_cash_on_cash_pct": 100 * cf_usd * 12 / cash_needed if cash_needed else None,
    }


def underwrite(p):
    """Return a base and conservative rent/vacancy stress scenario.

    Max price assumes entered fixed taxes/insurance/HOA/other costs stay unchanged.
    It is a financing screen, not a market valuation or suggested offer.
    """
    p.validate()
    base = _case(p)
    stress = _case(replace(
        p, monthly_rent_usd=p.monthly_rent_usd * 0.90,
        vacancy_fraction=max(p.vacancy_fraction, 1 / 12)
    ))
    variable_share = (
        p.vacancy_fraction + p.management_fraction
        + p.maintenance_fraction + p.capex_fraction
    )
    fixed_monthly = (
        (p.annual_property_tax_usd + p.annual_insurance_usd) / 12
        + p.monthly_hoa_usd + p.monthly_other_usd
    )
    required_rent = (
        p.target_monthly_cashflow_usd + fixed_monthly
        + base["monthly_debt_service_usd"]
    ) / (1 - variable_share)
    cash_available_for_debt = (
        p.monthly_rent_usd * (1 - variable_share)
        - fixed_monthly - p.target_monthly_cashflow_usd
    )
    payment_per_dollar = monthly_payment(1.0, p.annual_interest_rate, p.loan_years)
    max_price = (
        max(0.0, cash_available_for_debt / (payment_per_dollar * (1 - p.down_payment_fraction)))
        if p.down_payment_fraction < 1 else None
    )
    return {
        **base,
        "stress_monthly_cashflow_usd": stress["monthly_cashflow_usd"],
        "stress_vacancy_fraction": max(p.vacancy_fraction, 1 / 12),
        "stress_rent_usd": p.monthly_rent_usd * 0.90,
        "required_monthly_rent_for_target_usd": required_rent,
        "max_purchase_price_for_target_usd": max_price,
        "target_monthly_cashflow_usd": p.target_monthly_cashflow_usd,
        "base_target_pass": base["monthly_cashflow_usd"] >= 200,
        "stress_nonnegative": stress["monthly_cashflow_usd"] >= 0,
    }
