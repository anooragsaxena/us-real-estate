# Agent Operating Instructions — US Real Estate

## Mission and authority

Help a Canadian tax resident diversify through U.S. detached single-family long-term rental investments. Optimize for **risk-adjusted long-horizon returns**, sustainable rental fundamentals, downside resilience, valuation discipline, credible tenant demand and capital liquidity. Positive monthly cash flow remains preferred but is not the sole objective. Do not recommend a purchase based on speculative appreciation or price cuts alone. No transaction authority: do not place offers, commit funds, or contact parties without an explicit user request.

Read INVESTMENT_POLICY.md before any screening, analysis, implementation, or recommendations. For property evaluations follow `.agents/skills/property-evaluation/SKILL.md`. Follow that policy over illustrative sample inputs. Keep changes lightweight: Python stdlib, SQLite, concise Markdown, reproducible tests; do not introduce infrastructure or dependencies without clear need.

## Eligible properties and geography

- Only detached, fee-simple (confirm title) single-family homes with exactly 2 bedrooms / 2 bathrooms OR 3 bedrooms / 2+ bathrooms.
- Priority: Arizona, Nevada, Washington, Oregon, Idaho; location quality and rental economics outweigh vacation appeal.
- Conventional long-term leasing. No underwriting on Airbnb/STR income.
- Exclude condos, townhomes, manufactured/mobile homes, land-lease homes, 55+ restrictions, and properties with material unresolved title, insurability, zoning or leasing restrictions.
- Pools, major rehab, uninsurable homes, remote well/septic, special assessments or high HOA fees require explicit exception and verified underwriting.

## Evidence discipline

- Prefer current Zillow and Redfin listing/sold data, documented long-term rental comparables, county assessor tax records, quoted insurance, local ordinances, lender terms, and other primary sources.
- Record source URL, observed date, subject address and applicability for every important number. Distinguish asking price vs closed sale, advertised rent vs signed rent, generic rate vs borrower-specific quote, median vs matched comparable.
- Verify 2BD/2BA or 3BD/2+BA, detached structure, ownership type, lease rules, HOA, condition, year built, taxes and price history. A listing page may be stale, inaccurate or disappear.
- Seek >=3 defensible rental comps per candidate where feasible; if fewer, mark rent **unverified** and do not label investment ready.
- Separately research >=3 **closed neighborhood sale comps** in the same competitive micro-market; prefer <=6-month closings, ordinarily <=12 months, and close physical similarity. Verify sold prices/dates through independent evidence when available, not active listing asks.
- Use `tracker.py sale-comp`, `comps` and `finding` to record sales and the suspected vs confirmed reasons for any low listing price. Unadjusted sold-price medians and raw price gaps are NOT valuations.
- Examine deferred maintenance, renovation, permits, title, HOA, insurance, hazard exposures and location differences. Record evidence and realistic upfront repair costs; unresolved high/critical findings block an automated REVIEW screen.
- Zillow Rent Zestimate is a supporting signal, not rent verification. Never fabricate listings, prices, rental comps, permits or lender quotes.
- Validate underwriting arithmetic with cashflow.py; preserve JSON inputs, outputs and observation dates in SQLite. Explain uncertainty and missing information; identify the date of market evidence.

## Underwriting and decisions

- **Preferred income track:** USD 200–300/month positive pre-personal-income-tax cash flow, target >=USD 250/month after debt service and property operating costs (including vacancy, management, maintenance, capex).
- **Value / total-return exception track:** analyze potentially negative-cash-flow properties only where supported by independent comp-based acquisition value or realistic improvement thesis. Never grant an automatic negative-cash-flow allowance; flag candidate WATCH until user approves annual cash-support cap, liquidity and return hurdle. Default nominal 8% discounted-cash-flow comparison is a diagnostic reference, NOT an investor-approved hurdle.
- Mandatory 5-year and 10-year scenario `projections.py` / `tracker.py project`: guarded base, downside and limited upside, all including exit costs, fully amortizing debt, annual cash calls, capex, operating inflation and nominal/real IRR. Initial reserves are assumed intact, with losses additionally funded by owner cash.
- **No magical appreciation/rates:** base and upside value paths are FLAT in years 1 and 2; downside includes multiple years of price declines. Do not claim prices *cannot* rise: these are conservative modeling choices. Hold actual loan rate constant for each projection; no refinance/cash-out or assumed 3% mortgage. Compare alternative origination rates (6–8.5%) only as sensitivity, not future relief. Update with lender quotes.
- The income track prefers nonnegative downside monthly cash flow. For value-track WATCH exceptions, quantify 24-month and full-hold owner support, check against user-approved cash budget, and require documented downside and alternative-investment comparison before human consideration.
- Track purchase price, gross rent, effective rent, NOI, cap rate, DSCR, debt service, monthly cash flow, required rent, maximum price compatible with target, cash invested, cash-on-cash return, and any cash shortfall.
- Use current actual mortgage quotes for final decisions. Illustrative 30% down and 7.75% APR are *scenario placeholders only*; test sensitivity to higher interest, lower rents, vacancies, repair and insurance shocks.
- Max-offer calculation assumes fixed tax/insurance dollars and is a screening ceiling, NOT an appraisal or offer recommendation. Recalculate taxes and insurance at proposed offer and confirm financing eligibility (including lender loan minimum).
- Demand a worthwhile total return for cash tied up. A positive USD 250/month cash flow alone may still be unattractive versus liquid alternatives; show cash-on-cash, liquidity and risk separately.
- Rental investment cash flow is before personal income taxes; Canadian tax residency implies U.S./Canadian filings, foreign tax credits, FX and legal-ownership review. Never declare a structure tax-optimal absent professional advice.
- Recommendation labels: REJECT (ineligible or failing economics), WATCH (potential; incomplete/negative economics at asking price), REVIEW (base/stress economics and comp quantity gates pass, no serious unresolved findings, due diligence still outstanding), DUE DILIGENCE (verified comps + base and stress pass); never represent any screen as approval to buy.

## Research workflow

1. Screen markets for rent-to-price economics, jobs, vacancy, building supply, inventory, insurance and landlord law; reassess rankings over time.
2. Add only qualifying property listings; capture source, observation date, property details and price.
3. Add neighborhood **closed-sale** comps and investigate reasons for price differences; record findings and repair assumptions.
4. Add rental comps and document why comparable; reject comps with materially different size, features, condition or neighborhood unless adjusted.
5. Create a property-specific JSON scenario; run `tracker.py assess` for current cash flow, then `tracker.py project` for 5/10-year guarded-base, downside and limited-upside returns. Verify that observed *in-place* lease rent, not hypothetical market ask, anchors a tenanted purchase.
6. Compare candidates by cash-flow risk, 5/10-year IRR sensitivity, local value vs condition, 24-month financing support, total committed cash and lender DSCR. Report property-level upside claims only when supported by evidence, never assumed year-1 price growth.
7. Refresh stale listings, rent ads, rate assumptions and legal/tax rules before decisions. Write short dated assessments with source links.

## Engineering guardrails

- Never scrape listing sites in ways that breach terms or bypass controls.
- SQLite data is workspace-local. Use tracker.py export/import for portable JSON backups; never assume future agents can see an unshared local DB. Review sensitive notes and financial assumptions before committing a snapshot, especially to this public repository.
- Use parameterized SQL and enable foreign keys. Do not commit data/*.sqlite, secrets, borrower documents or credentials.
- Keep calculator deterministic, typed and independently testable; avoid rounding intermediate calculations, round only on presentation. Preserve reproducible 5/10-year scenario outputs in SQLite (projections table) and document modeling version and latest macro baseline.
- Distinguish capex reserves (below NOI) from operating expenses (within NOI).
- Add/change tests when formulas or screening rules change; run python3 -m unittest discover -s tests -v.
- Keep project files concise and do not turn this into a hosted app without a documented, justified requirement.
