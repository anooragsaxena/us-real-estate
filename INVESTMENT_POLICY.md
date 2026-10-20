# Investment Policy — U.S. Single-Family Rentals

Version: 2.0 | Effective: 2026-10-19 | Currency: USD unless stated otherwise

## 1. Investment mandate

Acquire U.S. real estate for portfolio diversification through durable, long-term rental income, reasonable asset quality and potential long-run appreciation. Investor is a **Canadian tax resident**. Long-term capital resilience, conservative total returns and recurring rental economics take precedence over vacation use or STR revenue. Positive cash flow is preferred, but value-based exceptions may be considered only with verifiable acquisition advantages, a separately approved cash-support budget and rigorous downside protection. Do not assume appreciation or interest-rate declines to justify buying.

## 2. Property requirements

**Required**: Detached single-family home, legally rentable on a conventional long-term lease; 2 bedrooms / 2 bathrooms or 3 bedrooms / at least 2 bathrooms; title, land ownership, permitted use and ownership form confirmed. Markets: AZ, NV, WA, OR, ID. Prioritize neighborhoods with sustained tenant demand, employment access, safe/insurable structures and exit liquidity. Research priorities are revisable, not permanent market endorsements.

**Exclude by default**: condos, townhomes, manufactured/mobile homes, land leases, age-restricted communities, major-rehab projects, short-term-rental dependent cases, and restrictive HOA/municipal leasing rules. Treat high HOA fees, pools, well/septic, wildfire/flood risk, insurance gaps, assessments and aging roofs/HVAC as deal-specific red flags.

## 2A. Neighborhood comparable sales and property condition

Evaluate **closed neighborhood sales** separately from long-term rental comps. Prefer at least 3 independently verified, arm's-length sales in the same competitive micro-neighborhood (6 months preferred, up to 12 ordinarily acceptable). Start around 1 mile in urban/suburban neighborhoods; expand for rural homes with a documented reason. Match property type, beds/baths, finished area (screen ±20%), vintage, lot, garage, condition and externalities.

Report median closed-sale price and $/sq ft as **unadjusted descriptive figures, not fair market value**. A price below the neighborhood median is not automatically undervalued. Validate sale date, financing concessions and unusual/distressed transactions. Dollar adjustments require market evidence; do not apply mechanical dollars-per-square-foot or assume repair cost equals value discount.

Investigate the reasons for low pricing: renovation needs, roof/HVAC/foundation, unpermitted work, property restrictions, seller motivation, insurance, wildfire/flood exposure, location disadvantages, special assessments and sale concessions. Record suspected versus confirmed concerns, evidence URL, estimated repair cost and remediation status. Include immediate repairs and contingency in cash invested and underwriting. Open high/critical findings prevent automated REVIEW.

Without three screen-qualified closed sales the valuation remains unverified and the automated result remains WATCH, even when rent and cash flow appear attractive.

## 3. Financial objectives and capital

- **Income track (preferred):** seek +$200–$300/month pre-personal-income-tax cash flow; +$250/month target. Keep cash-on-cash yield and leveraged/unleveraged cost of capital in view.
- **Value / total-return track (exception, not automatic):** near-break-even or moderately negative cash flow may be *investigated*, not approved, where an evidence-supported below-market acquisition or actionable renovation/value creation thesis exists. There is **no blanket permission to run negative**. Require user-approved annual funding cap, 24-month cash shortfall coverage separate from lender-required reserves, no hidden loss funding, and a return hurdle benchmarked against liquid alternatives. Until the user supplies a funding cap and accepts a risk hurdle, value-track candidates cannot be labeled purchase-ready.
- Cash flow means scheduled rent less vacancy, operating costs, capital replacement reserve, and principal + interest mortgage payments. Include property manager fees even if self-managing is considered.
- **Do not buy solely to hit the cash-flow number**. Assess cash-on-cash yield, cap rate, DSCR, location, repair risk, tenant turnover and alternative uses for invested cash.
- Planning search budget: **$200K–$300K**, not a maximum or estimate of fair value. Starting capital goal previously discussed: roughly **$110K–$140K**, subject to actual down payment, lender terms, closing costs, repair costs, reserves, and USD/CAD.
- Default screening: 30% down, 30-year amortization, illustrative 7.75% annual rate, 4% closing, and scenario-specific property taxes, insurance, reserves, repairs and HOA. Never present these as quoted rates.
- Test financing at 25%, 30%, 35%+ down where appropriate and confirm foreign-national/DSCR mortgage eligibility, loan size minimums, documentation, prepayment terms and reserves.
- Maintain minimum six months of property carrying costs/liquidity unless actual lender requirements are greater; investor-level emergency savings should remain separate. Keep closing, repairs and reserve cash in invested-capital calculations.

## 4. Underwriting: mandatory line items

**Inputs**: offer/purchase price; rent supported by recent local comps; down payment; APR and amortization; property tax; insurance; HOA; management; vacancy; maintenance; capital expenditures reserve; owner-paid utilities/other recurring expenses; closing costs; initial repairs; retained reserves. Explicitly flag any estimate without evidence.

**Outputs**: scheduled/effective rent; operating expenses; net operating income (NOI, before capex reserve and financing); loan amount; principal+interest; pre-tax monthly cash flow; annual cap rate; DSCR; cash invested and cash-on-cash yield; rent needed to generate $250/month; and mathematical maximum price at that rent/assumptions. Max price holds entered annual taxes and insurance constant and must NOT be treated as appraised value.

Default screening allowances when no evidence exists: management 8% of scheduled rent, vacancy 5%, maintenance 6%, capital replacement reserve 5%, closing 4%. These are placeholders that require property/market verification; do NOT default property taxes, insurance, HOA, or achievable rental income to zero without explicitly validating zero as correct.

Calculate cash flow using monthly debt service on an amortizing loan, not interest-only. Annualized cash-on-cash return = 12 x monthly cash flow / (down payment + closing + immediate repairs + initial reserves). These reserves remain cash assets but are counted as committed capital.

## 4A. Long-horizon, high-rate realism (mandatory for value-track analysis)

Use `projections.py` / `tracker.py project` to calculate **5- and 10-year nominal and inflation-adjusted IRR**, yearly after-debt cash flow, accumulated mortgage principal, property valuation path, exit sale costs, net sale proceeds, and **first 24-month and full-hold owner funding requirements**. Model 3 named pathways: guarded base, downside and limited upside. Write specific nominal assumptions alongside each model.

**Non-negotiable projection rules:**
- Base and limited-upside models assume **0% home-price appreciation in years 1 and 2**, not 3% in year 1. Downside incorporates multi-year outright price declines. This is a prudence rule, **not a claim that every ZIP code must fall**.
- Rent growth is modest, and may lag **property tax, insurance, HOA and maintenance pressure**. Evidence from executed leases/rent comps overrides generic growth assumptions.
- The mortgage **stays at its modeled origination rate** for the whole hold. No assumed 3% return, refi, or future cash-out; 6–7% is a *rate sensitivity only if plausible at origination*, not a forecast of financing relief. The placeholder 7.75% loan should be replaced with a foreign-national lender quote.
- Use realistic transaction costs at purchase and exit; initial rehabilitation and capital reserves count as committed cash. **Do not count mortgage paydown twice**; debt balance is deducted from exit proceeds, and yearly cash flow already deducts full P&I.
- Future property value **starts at acquisition price**, not an unadjusted sold-comps median or assumed instant renovation profit. Any explicit value-add uplift needs actual cost, documentation and independent comp-based justification—never injected as a generic growth rate.
- Report both nominal and real returns. The default **8% nominal discount-rate comparison is illustrative only, NOT an adopted investor hurdle**; the default 3% inflation is also illustrative. Compare with risk-adjusted after-tax alternative investments and re-evaluate these assumptions with up-to-date macro evidence.
- Forecast returns are **before** U.S./Canadian personal taxes and CAD/USD fluctuations; before purchase these need case-specific analysis. `projections.py` is for scenario bounding, not investment approval, and does not calculate probabilities.
- Determine investor liquidity to withstand the first 24 months of negative cash flow, in addition to lender reserves. Require written justification and explicit approval for an exception, even when nominal projected IRR appears positive.

See [dated research baseline](research/2026-10-19-macro-underwriting-baseline.md). Revisit when mortgage rates, inventory, local closed-sale prices, local rent absorption, inflation or fiscal evidence materially changes.

## 5. Downside discipline and decision gates

The preferred **income track** still seeks at least +$200/month, targeting +$250/month, with nonnegative monthly downside cash flow. Stress rent down 10% and vacancy to at least 8.33% annually, alongside additional repair, tax and insurance increases. Fixed-rate loans have no assumed refinancing; consider an origination-rate shock before signing and +1.5 percentage-point resets only for genuine variable/reset mortgages.

On the **value / total-return exception track**, an income-screen WATCH is **not an automatic rejection**, but neither does the model convert WATCH to REVIEW merely from projected appreciation. Require three credible closed-sale comps, three rent comps, documented value thesis, condition and rehabilitation verification, lender feasibility, actual lease terms, 5/10-year IRR scenarios, an explicit user-set negative-cash-support limit and an after-tax/currency risk review before human advancement. Leave the automated status WATCH until these are fulfilled and the investor approves the exception.

- **REJECT**: fails property rules, legal/insurance feasibility, or has unsupportable economics.
- **WATCH**: possibly interesting but current price economics fail or important inputs missing; calculate required discount without labeling it a fair-value discount.
- **REVIEW**: automated **income-track** base/downside economics pass with at least 3 recorded rent comps and 3 screen-qualified neighborhood closed-sale comps, no unfunded identified repairs or open high/critical findings; deeper verification is still required. Value-track candidates remain WATCH pending a separate documented, investor-approved exception.
- **DUE DILIGENCE**: verified rent comps, financing/insurance/tax estimates, base and downside pass; still requires inspection, attorney/accountant and investor approval.

Missing mandatory numbers => no investment-ready result. Record adverse findings even where numerics pass. Decisions can change as evidence evolves.

## 6. Evidence, tax and governance

Capture as-of date and URL for asking/sold price, rents, taxes, insurance, lender assumptions, and any regulatory claim. Prefer >=3 comparable long-term rentals, cross-check Zillow and Redfin, and identify listing age and condition differences. Advertised rents and estimates are not signed lease evidence. Refresh sources before action.

Model operating cash flow **before U.S. and Canadian personal income taxes**. Obtain cross-border professional review for U.S. election/net taxation of rent, Canadian worldwide-income reporting and currency translation, T1135 thresholds, foreign tax credits, depreciation/CCA divergence, ownership structure, potential FIRPTA on sale and estate exposure. Treat currency and taxes as separate investment risks. No offer or capital commitment without affirmative owner approval.

## 7. Review cadence

Update candidates when sale prices change or monthly during active searching; refresh rent comps, mortgage rates and market observations at least quarterly, and before underwriting a potential purchase. Document what changed, source dates, principal uncertainties and next actions.
