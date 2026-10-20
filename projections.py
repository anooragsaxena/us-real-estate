"""Conservative nominal USD hold-period scenarios for U.S. single-family rentals.

No refi, no rate decline, no first-year appreciation in base/upside cases.
Every scenario is a stress assumption, NOT a forecast. Taxes and FX omitted.
Debt amortizes monthly; yearly cash flow subtracts management, vacancy,
maintenance, capex allowance, fixed operating costs and mortgage P&I.
Initial reserves remain committed then are released on exit; ongoing capex
provision is treated as an economic cost (spent over the hold), not added
back at exit. Deferred repairs must be separately modeled in upfront repairs.
"""
from dataclasses import dataclass
from math import isfinite
from cashflow import Inputs, underwrite, monthly_payment

@dataclass(frozen=True)
class Profile:
    name: str
    home_price_change: tuple[float, ...]  # annual sequential change; no automatic revaluation to comps
    rent_change: tuple[float, ...]        # each year vs preceding rent, starts at underwriting rent
    property_tax_inflation: float
    insurance_inflation: float
    hoa_inflation: float
    other_cost_inflation: float
    vacancy_floor: float
    one_time_insurance_shock: float = 0.0

# Deliberately restrained NOMINAL assumptions, not assertions of future data.
# First year base + upside have 0% appreciation; downside has outright price falls.
PROFILES = {
    "guarded_base": Profile(
        "guarded_base",
        (0, 0, .01, .015, .015, .015, .015, .015, .015, .015),
        (0, .01, .015, .015, .015, .015, .015, .015, .015, .015),
        .035, .055, .04, .04, .05,
    ),
    "downside": Profile(
        "downside",
        (-.06, -.04, -.02, 0, 0, 0, .005, .005, .005, .005),
        (-.05, 0, 0, .005, .005, .005, .005, .005, .005, .005),
        .05, .09, .06, .05, 1/12, .20,
    ),
    "limited_upside": Profile(
        "limited_upside",
        (0, 0, .015, .02, .02, .02, .02, .02, .02, .02),
        (0, .015, .02, .02, .02, .02, .02, .02, .02, .02),
        .03, .04, .03, .03, .05,
    ),
}
DEFAULT_HURDLE_NOMINAL = .08  # diagnostic reference ONLY, not a user-approved hurdle
DEFAULT_INFLATION_FOR_REAL_RETURN = .03  # illustration, not inflation forecast
DEFAULT_EXIT_SELLING_COST = .06
DEFAULT_HORIZONS = (5, 10)


def irr(cashflows):
    """Annual IRR for initial negative capital followed by yearly net flows."""
    if len(cashflows) < 2 or cashflows[0] >= 0:
        return None

    def npv(rate):
        return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cashflows))

    low, high = -.95, 5.0
    f_low, f_high = npv(low), npv(high)
    if not (isfinite(f_low) and isfinite(f_high)) or f_low * f_high > 0:
        return None
    for _ in range(150):
        middle = (low + high) / 2
        if npv(middle) > 0:
            low = middle
        else:
            high = middle
    return (low + high) / 2


def project(p: Inputs, scenario="guarded_base", years=5,
            selling_cost_fraction=DEFAULT_EXIT_SELLING_COST,
            inflation_for_real_return=DEFAULT_INFLATION_FOR_REAL_RETURN,
            nominal_hurdle=DEFAULT_HURDLE_NOMINAL):
    """One fixed-mortgage hold; no cash-out refinance, new debt or market timing."""
    p.validate()
    if scenario not in PROFILES:
        raise ValueError("unknown projection scenario")
    if type(years) is not int or years not in DEFAULT_HORIZONS:
        raise ValueError("supported horizons are 5 and 10 years")
    for name, value in {
        "selling_cost_fraction": selling_cost_fraction,
        "inflation_for_real_return": inflation_for_real_return,
        "nominal_hurdle": nominal_hurdle,
    }.items():
        if not isinstance(value, (float, int)) or not isfinite(value) or not 0 <= value < 1:
            raise ValueError(f"{name} must be finite and between 0 and 1")
    cfg = PROFILES[scenario]
    base = underwrite(p)
    loan = base["loan_usd"]
    debt_payment = monthly_payment(loan, p.annual_interest_rate, p.loan_years)
    monthly_interest_rate = p.annual_interest_rate / 12
    price, rent = p.purchase_price_usd, p.monthly_rent_usd
    capital_committed = base["cash_needed_usd"]
    flows = [-capital_committed]
    annual_rows = []
    running_owner_support = 0.0
    for year in range(1, years + 1):
        price *= 1 + cfg.home_price_change[year-1]
        rent *= 1 + cfg.rent_change[year-1]
        effective_vacancy = max(p.vacancy_fraction, cfg.vacancy_floor)
        fixed_factor = year - 1
        taxes = p.annual_property_tax_usd * (1 + cfg.property_tax_inflation) ** fixed_factor
        insurance = p.annual_insurance_usd * (
            1 + cfg.one_time_insurance_shock
        ) * (1 + cfg.insurance_inflation) ** fixed_factor
        hoa = p.monthly_hoa_usd * 12 * (1 + cfg.hoa_inflation) ** fixed_factor
        other = p.monthly_other_usd * 12 * (1 + cfg.other_cost_inflation) ** fixed_factor
        gross = rent * 12
        vacancy = gross * effective_vacancy
        operating = gross * (p.management_fraction + p.maintenance_fraction) + vacancy
        operating += taxes + insurance + hoa + other
        capex = gross * p.capex_fraction
        noi = gross - operating
        principal_paid = 0.0
        interest_paid = 0.0
        for _ in range(12):
            if loan <= 1e-9:
                loan = 0.0
                break
            interest = loan * monthly_interest_rate
            principal = min(loan, max(0.0, debt_payment - interest))
            interest_paid += interest
            principal_paid += principal
            loan -= principal
        debt_service = principal_paid + interest_paid
        cash = noi - capex - debt_service
        if cash < 0:
            running_owner_support += -cash
        annual_rows.append({
            "year": year,
            "year_end_property_value_usd": price,
            "year_end_loan_balance_usd": loan,
            "gross_scheduled_rent_usd": gross,
            "effective_vacancy_fraction": effective_vacancy,
            "operating_expenses_usd": operating,
            "noi_usd": noi,
            "capex_allowance_usd": capex,
            "mortgage_principal_paid_usd": principal_paid,
            "mortgage_interest_paid_usd": interest_paid,
            "operating_cashflow_after_debt_usd": cash,
            "average_monthly_cashflow_usd": cash / 12,
        })
        flows.append(cash)

    sale_transaction_cost = price * selling_cost_fraction
    gross_equity_on_sale = price - loan
    exit_cash_proceeds = price - sale_transaction_cost - loan + p.reserves_usd
    flows[-1] += exit_cash_proceeds
    nominal_irr = irr(flows)
    real_irr = (
        (1 + nominal_irr) / (1 + inflation_for_real_return) - 1
        if nominal_irr is not None else None
    )
    npv_at_hurdle = sum(
        amount / (1 + nominal_hurdle) ** idx for idx, amount in enumerate(flows)
    )
    return {
        "scenario": scenario,
        "years": years,
        "mortgage_rate_assumed_fixed_no_refinance": p.annual_interest_rate,
        "scenario_appreciation_path": list(cfg.home_price_change[:years]),
        "scenario_rent_change_path": list(cfg.rent_change[:years]),
        "selling_cost_fraction": selling_cost_fraction,
        "inflation_assumption_for_real_returns": inflation_for_real_return,
        "illustrative_nominal_hurdle": nominal_hurdle,
        "initial_committed_cash_usd": capital_committed,
        "year_1_monthly_cashflow_usd": annual_rows[0]["average_monthly_cashflow_usd"],
        "year_1_home_value_change_pct": cfg.home_price_change[0] * 100,
        "cumulative_negative_cash_support_usd": running_owner_support,
        "first_24_months_cash_support_usd": sum(
            max(0, -y["operating_cashflow_after_debt_usd"]) for y in annual_rows[:2]
        ),
        "cumulative_principal_paid_usd": sum(y["mortgage_principal_paid_usd"] for y in annual_rows),
        "sale_property_value_usd": price,
        "selling_transaction_cost_usd": sale_transaction_cost,
        "outstanding_loan_at_sale_usd": loan,
        "net_sale_proceeds_including_returned_initial_reserves_usd": exit_cash_proceeds,
        "nominal_annual_irr": nominal_irr,
        "illustrative_real_annual_irr": real_irr,
        "npv_at_illustrative_hurdle_usd": npv_at_hurdle,
        "yearly_details": annual_rows,
        "annual_investor_cashflows_usd": flows,
        "warnings": [
            "Scenarios are assumptions, NOT probability-weighted forecasts.",
            "No refinancing or rate declines assumed. Fixed original loan APR.",
            "First-year appreciation zero in base/upside; downside falls.",
            "Rent may be subject to existing lease; replace advertised rent with in-place rent.",
            "Expense escalation does not include unplanned major repairs beyond allowance.",
            "Income taxes (US/Canada), currency effects and estate/FIRPTA excluded.",
            "Initial committed reserves assumed intact and released on sale.",
            "Sale prices start at acquisition cost, NOT unadjusted comps or speculative after-repair value.",
        ],
    }


def compare_scenarios(p, horizons=DEFAULT_HORIZONS, **kwargs):
    return {
        "assumptions": {
            "scenarios": list(PROFILES),
            "horizons_years": list(horizons),
            "no_refinance": True,
            "reference_not_policy_hurdle": kwargs.get("nominal_hurdle", DEFAULT_HURDLE_NOMINAL),
        },
        "outcomes": {
            profile: {str(years): project(p, profile, years, **kwargs) for years in horizons}
            for profile in PROFILES
        },
    }
