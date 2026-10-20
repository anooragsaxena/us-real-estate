"""Descriptive closed-sale comparable screening, NOT a property valuation.

Requires independently verified closed transactions and strict basic similarity.
Never inserts or infers renovation-adjusted market values.
"""
from datetime import date
from statistics import median


def sale_comps_summary(subject, comps, *, as_of=None, radius_miles=1.0):
    if as_of is None:
        as_of = date.today()
    if isinstance(as_of, str):
        as_of = date.fromisoformat(as_of)
    if radius_miles <= 0:
        raise ValueError("radius must be positive")
    subject_area = subject["finished_sqft"]
    accepted = []
    excluded = []
    for comp in comps:
        reasons = []
        sold = date.fromisoformat(comp["sold_on"])
        days = (as_of - sold).days
        if not (0 <= days <= 365):
            reasons.append("outside trailing 12 months")
        if not comp["sale_verified"]:
            reasons.append("closed sale not cross-verified")
        if comp["transaction_type"] != "arm_length":
            reasons.append("arm's-length status not verified")
        if comp["distance_miles"] > radius_miles:
            reasons.append("outside study radius")
        if comp["bedrooms"] != subject["bedrooms"] or abs(comp["bathrooms"] - subject["bathrooms"]) > 0.5:
            reasons.append("bed/bath mismatch")
        if not subject_area or not (0.8 * subject_area <= comp["finished_sqft"] <= 1.2 * subject_area):
            reasons.append("finished area missing/outside 20% range")
        if reasons:
            excluded.append({"id": comp["id"], "address": comp["address"], "reasons": reasons})
        else:
            accepted.append(comp)
    sold_prices = [r["sold_price_usd"] for r in accepted]
    ppsf = [r["sold_price_usd"] / r["finished_sqft"] for r in accepted]
    median_price = median(sold_prices) if sold_prices else None
    ask = subject["asking_price_usd"]
    return {
        "total_sale_comps": len(comps),
        "screen_qualified_sale_comps": len(accepted),
        "accepted_ids": [r["id"] for r in accepted],
        "excluded": excluded,
        "radius_miles": radius_miles,
        "as_of": as_of.isoformat(),
        "median_closed_price_usd_unadjusted": median_price,
        "median_closed_price_per_sqft_usd_unadjusted": median(ppsf) if ppsf else None,
        "ask_minus_median_usd": ask - median_price if median_price is not None else None,
        "ask_vs_median_pct": 100 * (ask / median_price - 1) if median_price else None,
        "note": "Descriptive, unadjusted sale-price comparison only; NOT fair market value, valuation adjustment or recommended offer.",
    }
