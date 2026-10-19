# Agent Operating Instructions — US Real Estate

## Mission and authority

Help a Canadian tax resident diversify through U.S. detached single-family long-term rental investments. Optimize for sustainable positive **monthly cash flow**, downside resilience, good neighborhoods, tenant demand, and reasonable liquidity. Do not recommend a purchase based on speculative appreciation or price cuts alone. No transaction authority: do not place offers, commit funds, or contact parties without an explicit user request.

Read INVESTMENT_POLICY.md before any screening, analysis, implementation, or recommendations. Follow that policy over illustrative sample inputs. Keep changes lightweight: Python stdlib, SQLite, concise Markdown, reproducible tests; do not introduce infrastructure or dependencies without clear need.

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
- Zillow Rent Zestimate is a supporting signal, not rent verification. Never fabricate listings, prices, rental comps, permits or lender quotes.
- Validate underwriting arithmetic with cashflow.py; preserve JSON inputs, outputs and observation dates in SQLite. Explain uncertainty and missing information; identify the date of market evidence.

## Underwriting and decisions

- Cash-flow goal: USD 200–300/month, base target >=USD 250/month **after debt service and property operating costs including vacancy, management, maintenance and capex reserve**, before personal income tax.
- Require nonnegative downside scenario for progression to deep due diligence, or flag as an explicit exception, never silent acceptance.
- Track purchase price, gross rent, effective rent, NOI, cap rate, DSCR, debt service, monthly cash flow, required rent, maximum price compatible with target, cash invested, cash-on-cash return, and any cash shortfall.
- Use current actual mortgage quotes for final decisions. Illustrative 30% down and 7.75% APR are *scenario placeholders only*; test sensitivity to higher interest, lower rents, vacancies, repair and insurance shocks.
- Max-offer calculation assumes fixed tax/insurance dollars and is a screening ceiling, NOT an appraisal or offer recommendation. Recalculate taxes and insurance at proposed offer and confirm financing eligibility (including lender loan minimum).
- Demand a worthwhile total return for cash tied up. A positive USD 250/month cash flow alone may still be unattractive versus liquid alternatives; show cash-on-cash, liquidity and risk separately.
- Rental investment cash flow is before personal income taxes; Canadian tax residency implies U.S./Canadian filings, foreign tax credits, FX and legal-ownership review. Never declare a structure tax-optimal absent professional advice.
- Recommendation labels: REJECT (ineligible or failing economics), WATCH (potential; incomplete/negative economics at asking price), REVIEW (base economics pass but due diligence outstanding), DUE DILIGENCE (verified comps + base and stress pass); never represent any screen as approval to buy.

## Research workflow

1. Screen markets for rent-to-price economics, jobs, vacancy, building supply, inventory, insurance and landlord law; reassess rankings over time.
2. Add only qualifying property listings; capture source, observation date, property details and price.
3. Add rental comps and document why comparable; reject comps with materially different size, features, condition or neighborhood unless adjusted.
4. Create a property-specific JSON scenario, run tracker.py assess, review monthly cash flow and stress results, then save findings.
5. Compare candidate scenarios by risk-adjusted yield, cash required and robustness. Report both disqualifiers and unknowns.
6. Refresh stale listings, rent ads, rate assumptions and legal/tax rules before decisions. Write short dated assessments with source links.

## Engineering guardrails

- Never scrape listing sites in ways that breach terms or bypass controls.
- Use parameterized SQL and enable foreign keys. Do not commit data/*.sqlite, secrets, borrower documents or credentials.
- Keep calculator deterministic, typed and independently testable; avoid rounding intermediate calculations, round only on presentation.
- Distinguish capex reserves (below NOI) from operating expenses (within NOI).
- Add/change tests when formulas or screening rules change; run python3 -m unittest discover -s tests -v.
- Keep project files concise and do not turn this into a hosted app without a documented, justified requirement.
