# Zillow case study — 2030 Pacific Ave, Kingman, AZ 86401

**Observed:** 2026-10-19 · **CLI screen:** WATCH (does **not** satisfy investment policy) · **Currency:** USD

## Listing and eligibility

- [Zillow sale listing](https://www.zillow.com/homedetails/2030-Pacific-Ave-Kingman-AZ-86401/8378256_zpid/): active as observed, **$219,900**, 3 bed / 2 bath, detached single-family, 1,324 sq ft, built 1987, reported no HOA, public water/sewer.
- [Redfin cross-check](https://www.redfin.com/AZ/Kingman/2030-Pacific-Ave-86401/home/119051389): property type/size consistent, but indexed ask of $224,900 is older than Zillow's July 27 $219,900 reduction. Do **not** blend mismatched price dates.
- Zillow reports annual 2026 tax of **$744** and a Rent Zestimate of **$1,457/month**. Neither replaces an updated assessor estimate or a property manager's rent opinion.
- Source-verified structure and bed/bath **pass** the basic screen. Legal title, lease permissions, insurability, inspection, permit compliance and post-transfer taxes are unverified.

## Long-term rental evidence

Three Zillow *asking-rent* observations, all Kingman 86401, 3BD/2BA detached houses:

| Address | Size | Asking rent | Source |
|---|---:|---:|---|
| 2032 Louise Ave | 1,272 sq ft | $1,550 | [Zillow](https://www.zillow.com/homedetails/2032-Louise-Ave-Kingman-AZ-86401/240274179_zpid/) |
| 2803 Fairgrounds Blvd | 1,377 sq ft | $1,500 | [Zillow](https://www.zillow.com/homedetails/2803-Fairgrounds-Blvd-Kingman-AZ-86401/8378264_zpid/) |
| 2804 Simms Ave | 1,159 sq ft | $1,550 | [Zillow](https://www.zillow.com/homedetails/2804-Simms-Ave-Kingman-AZ-86401/8374070_zpid/) |

The base-case **$1,500/month** rent is lower than the $1,550 comp median and a little higher than Zillow's $1,457 model. These are preliminary ZIP-level matches; distances, finishes, lease length, date freshness and achieved rents require verification.

## Underwriting assumptions

- $219,900 acquisition at asking; **30% down**; 30-year amortization; **7.75% fixed APR scenario**, not an actual foreign-national quote.
- 2026 listed taxes **$744/year**; insurance **$1,800/year estimate**; no HOA reported (not independently confirmed).
- Management **8%**, vacancy **5%**, maintenance **6%**, capex reserve **5%** of gross scheduled rent.
- Closing **4%**, immediate repairs **$5,000 placeholder**, initial reserves **$25,000**.
- No personal income taxes, exchange-rate effects, legal fees beyond assumed closing costs, rental licensing costs, owner-paid utilities or extraordinary repairs.

## Calculator results (cashflow.py; validated by GitHub Actions)

| Metric | Result |
|---|---:|
| Mortgage principal | $153,930 |
| Monthly mortgage P&I | **$1,102.77** |
| Monthly NOI (before capex/debt) | **$1,003.00** |
| Monthly capex reserve | $75.00 |
| Monthly cash flow | **-$174.77** |
| Stress cash flow: 10% rent haircut and 1/12 vacancy | **-$333.77** |
| DSCR | **0.91** |
| Annual NOI cap rate | **5.47%** |
| Initial cash committed | **$104,766** |
| Annual cash-on-cash return | **-2.00%** |
| Monthly rent required to net +$250 | **$2,058.91** |
| Mathematical purchase-price ceiling at $1,500 rent to net +$250 | **$135,197.50** |

At asking price, neither baseline $200/month nor targeted $250/month positive cash flow is met. The $135K *mathematical* ceiling is approximately 38.5% below asking and is **not** fair-market value or a recommended offer. A mortgage near $94.6K at that price could also be below some foreign-national loan minimums.

## Decision / next steps

**No buy recommendation.** The automated CLI returns WATCH because this site-built eligible listing has recorded comps but fails financial gates. In the investment shortlist, **do not advance it for due diligence** without a major verified change in price, achieved rent, loan terms or expenses.

Before reconsideration: verify actual listing status, leases/rents with local managers, current property-tax treatment post-transfer, foreign-national loan eligibility/minimum amount, independent insurance quote and property condition (roof/HVAC/wood-burning stove). Treat price reductions as negotiating evidence, not proof of undervaluation.

### Reproducibility

- [Dated input fixture](cases/2026-10-19_2030-Pacific-Ave.json)
- [CLI/SQLite end-to-end regression test](../tests/test_real_zillow_case.py) verifies listing insertion, three rental comps, assessment, export and WATCH classification.
- Run: `python3 -m unittest discover -s tests -v`

This research note and fixture contain public property information and hypothetical financing assumptions. No personal financial account information or live Zillow scraping is used.
