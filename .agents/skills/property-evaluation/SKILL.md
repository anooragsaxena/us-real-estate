---
name: property-evaluation
description: Research, screen, value and underwrite US detached single-family long-term rentals using verified neighborhood sale comps and rental comps. Use for identifying candidate listings, investigating apparent bargains, modeling repairs and financing, and documenting WATCH/REVIEW decisions and conservative 5/10-year scenario returns.
---

# Property Evaluation — Research and Underwriting Skill

## Required context

Read repository `INVESTMENT_POLICY.md` and `AGENTS.md` before any evaluation. This skill is the repeatable **method**, not an override of investment policy. Investor is a **Canadian tax resident**, seeking U.S. long-term rentals, with **$200/month preferred minimum** and **$250/month preferred target** pre-personal-income-tax cash flow *after* mortgage and all operating costs. Negative cash flow may be **researched** only as a value/total-return exception with a separately documented investor cash-support cap, not automatically approved. Only detached, fee-simple **2BD/2BA or 3BD/2+BA** homes in AZ, NV, WA, OR and ID. Do not underwrite using vacation/short-term rentals.

No autonomous purchases, bids, seller outreach or use of credentialed site scraping. Use public access or lawful/manual capture; respect Zillow/Redfin terms.

## Source hierarchy and evidentiary labels

| Needed evidence | Preferred sources | Notes |
|---|---|---|
| Sale listing / photos / status / history | Zillow, Redfin; listing agent / MLS if available | Store direct URL and observed date; an ask is **not** a sold comp |
| Closed neighborhood comparables | Redfin sold filter, Zillow sold filter; verify sale/date in county recorder/assessor or MLS | Prioritize **closed** arm's-length transactions; note distressed/non-market transactions and concessions |
| Tax basis, lot, building area, legal description | County assessor, recorder, GIS, parcel maps | Determine whether assessed tax resets after purchase; cross-check beds, bath, permitted area |
| Renovation / deferred maintenance | Listing description and dated photographs; permit history, seller disclosure; contractor bids, licensed inspector | Photo hints are **suspicions**, not confirmed defects; budget repairs with evidence |
| Long-term rental comps | Zillow Rentals, Redfin Rentals, property-management listings and, ideally, executed leases / manager opinion | Asking rent != achieved rent; match same neighborhood, bedroom/bath, condition and size |
| Rates and closing | Actual foreign-national/DSCR lender term sheets, title/escrow estimates | Model minimum loan amount, down payment, DSCR, borrower reserves and prepayment penalties |
| Insurance / hazards / restrictions | Broker quotes, FEMA flood map, local wildfire/hazard data, HOA rules, city/county landlord rules | Verify availability of coverage; identify HOA limits and utility obligations |
| Cross-border tax | IRS, CRA, cross-border tax counsel | Calculate property economics pre-personal-income-tax; do not assert tax optimization |
| Macro baseline and market conditions | [Freddie Mac PMMS](https://www.freddiemac.com/), [BLS CPI](https://www.bls.gov/news.release/cpi.nr0.htm), [CBO](https://www.cbo.gov/publication/62105), [Realtor.com](https://www.realtor.com/research/september-2026-data/), FRED, local MLS | See [dated evidence and assumptions](../../../research/2026-10-19-macro-underwriting-baseline.md). National indicators do NOT predict one local home's appreciation. |

For methodology references, consult Fannie Mae's public [Comparable Sales](https://selling-guide.fanniemae.com/sel/b4-1.3-08/comparable-sales), [Adjustments](https://selling-guide.fanniemae.com/sel/b4-1.3-09/adjustments-comparable-sales) and [Sales Comparison Approach](https://selling-guide.fanniemae.com/sel/b4-1.3-07/sales-comparison-approach-section-appraisal-report). These are **research analogues**, not claims that our screen is a lender appraisal.

Every material number must have: source URL, observation date, units, and status (observed/estimated/verified). Note missing evidence, contradictions, stale prices and unsupported assumptions. Never invent a property, rental listing, verified sale price, repair quote or financing offer.

## Workflow (follow this order)

1. **Eligibility & snapshot** — Confirm active status, 2BD/2BA or 3BD/2+BA, detached site-built structure, ownership/land type, state, asking price and date. Record `tracker.py add`; photograph links and listing-agent claims are evidence, not warranties.
2. **Neighborhood closed-sale comps (distinct from rent comps)** — Begin in the same subdivision/micro-neighborhood, usually within ~1 mile in an urban/suburban area. Prefer closed sales in the **last 6 months**; accept to **12 months** when appropriate. Rural/lower-density markets may need ~3 miles or more with documented justification, not arbitrary ZIP-wide matching. Seek **at least 3 arm's-length closed sales** resembling bed/bath count, property type, above-grade finished area (initially ±20%), age, lot, garage, condition and external influences. Record distance, sold date, sqft, condition difference and original URL for each via `tracker.py sale-comp`. When asserting `--verified`, supply an independent `--verification-url` (county/MLS or corroborating records); leave unverified otherwise. Explain every outlier/rejected comp.
3. **Valuation cross-check** — Run `tracker.py comps --listing-id ID`. Report median **unadjusted** sold price, median $/finished sq ft and raw ask-to-median gap. Do **not** call either a fair value estimate: a low ask may reflect smaller square footage, older roof/HVAC, lot/site differences, inferior location, distressed terms or mistakes. Explain and evidence differences. Only make dollar adjustments where actual local sales data supports the adjustment; document direction, basis and effective date. If comps are insufficient, label valuation *unverified*.
4. **Investigate the apparent discount** — Look for dated listing reductions, time-on-market, withdrawn/relisted history, owner disclosures, public permits, visible water/roof/foundation damage, aging HVAC, unpermitted additions, tenant/eviction restrictions, insurance risks, easements, traffic/industrial exposure, flood/fire hazards, property taxes, HOA, liens and seller concessions. Log `tracker.py finding` with severity, `suspected` vs `confirmed`, evidence, cost estimate and `open/resolved` status. Do not claim a defect is confirmed from pictures.
5. **Rehabilitation economics** — Estimate *must-do before leasing*, deferred replacements and contingencies separately. Obtain contractor and inspector support before investment readiness. Put immediate repairs in `upfront_repairs_usd`, and ongoing replacements into the capex reserve; avoid double counting. The automated screen checks that currently identified, open condition repair estimates do not exceed budgeted upfront repairs; unknown defects remain due-diligence gaps. Adjust purchase price/offer if economically warranted, but do not infer seller will accept it.
6. **Rent comps** — Collect ideally >=3 current long-term rental comps close to the subject, matching 2/2 or 3/2+ and size/condition. Record `tracker.py rent-comp`; choose conservative achievable rent with explanation; Zillow Rent Zestimate is supplementary only.
7. **Underwrite** — Create a JSON scenario from `examples/underwriting.json`; replace all placeholders with property-specific estimates and cite assumptions in a dated assessment. Run `tracker.py assess`. Validate rent, taxes after transfer, insurance quote, management, vacancy, maintenance, capex, HOA, financing, repair contingency, lender min loan and owner cash reserves.
8. **Stress and long-term total return** — Test 10% rent haircut + >=1 month/year vacancy, insurance/repair increases and actual adjustable-rate resets (if applicable). Run `tracker.py project --listing-id ID --input PATH --rent-source TYPE`; it saves 5/10-year guarded base, downside and limited upside projections. Use **actual in-place lease rent**, if occupied; asking rent estimates are NOT proof of current receipts. Default profiles contain **0% appreciation in years 1 and 2 for base and limited upside**, declining prices in downside, conservative rent growth, expense inflation and **no automatic interest-rate reduction or refinancing**. Run origination-rate sensitivities **6%, 7%, 7.75%, 8.5%** only where lender quotes plausibly support them. 8% NPV comparison and 3% inflation are configurable analytical placeholders, not approved investor return requirements or forecasts.
9. **Compare economics and risk** — Document current and downside monthly cash flow, DSCR, cap rate, cash-on-cash, 5/10-year nominal/real IRR, cumulative mortgage principal, acquisition/exit costs, owner cash calls over 24 months and over each hold, and local-comp value. Cash flow **remains the preferred track**. If a negative-cash-flow value thesis appears credible, leave CLI result **WATCH** and explicitly request investor-set funding cap/return hurdle before considering exception; do not promote by using projected appreciation to rescue a weak property. Confirm tax/FX before committing capital. Separately label valuation uncertainty.
10. **Decide and preserve** — Record a WATCH / REVIEW screen with reasons and required verification; neither is purchase authorization. Escalate to appraisal, physical inspection, title/HOA, actual lender quotes, independent insurance and cross-border tax counsel before an offer. Keep versioned projections and sources in SQLite via `show` and `export` and commit only non-sensitive dated case notes.


## Sale comp safeguards / decision rules

- Closed prices **only** enter the sold-comp median. Active/pending asks may be discussed as supply/competition but never mixed into the closed-price median.
- Do not call a lower raw ask **undervalued** until location, age, size, condition, repairs, financing constraints and sale concessions have been reconciled. A raw percentage gap is descriptive, not a discount to intrinsic or appraised value.
- Three recorded sales is a **quantity** threshold, not proof of credibility. Assess similarity, verification and recency manually. A severe unresolved finding blocks advancing an automated screen.
- Repair/inspection omissions and generic insurance/tax estimates should be explicit gating gaps, even when software returns REVIEW. No automated screening status means purchase approval.
- Fannie Mae guidance expects market-supported adjustments, not arbitrary dollar-per-sq-ft or dollar-for-dollar renovation costs. Our simple tracker deliberately **does not auto-adjust sale prices**.

## Projection integrity checks

- A price cut on the listing does not establish closed-sale fair value. No speculative instant markup from acquisition cost to Zillow Zestimate or raw comp median.
- Do not count annual mortgage principal as profit *in addition* to exit equity; the mortgage amortization is already reflected in the loan balance.
- Treat the **annual capex allowance as an economic cost**, not a cash balance automatically returned at sale. Initial liquidity reserves are committed at entry and modeled returned intact on exit; if actually drawn down to fund shortfalls, revise the return assumptions.
- Interest-rate sensitivity must be alternate financing **at purchase**, not an implicit future refinance.
- Present first-year appreciation as 0% in guarded base/limited upside, as a **prudence choice**; the real market could move either way. Never assert certainty about macro outcomes.
- Track dated inflation, deficit, rate and local housing supply evidence; no blanket claim that deficit trends imply a particular future mortgage rate.
- All projected IRRs are **pre-tax USD**. The Canadian investor's real after-tax, CAD-denominated realized return is not represented until modeled separately.
- A favorable nominal IRR in the optimistic scenario is **not** sufficient justification for a negative monthly cash-flow investment.

## Minimum report template

`As-of date | Zillow/Redfin property URL | eligibility/status | ask and history | neighborhood sold comps table (date, distance, area, price, condition, source) | raw price gap and limitations | why priced lower (evidence/unknowns) | estimated immediate rehab | rent comp table | assumptions & financing | cash flow base/downside, DSCR, cash-on-cash | cash-flow-compatible max price vs comp context | 5/10-year guarded/downside/limited-upside nominal and real IRRs, fixed-rate debt schedule and 24-month funding | critical risks | WATCH/REVIEW/REJECT with rationale | next verification steps`.

Never put 'bargain', 'below market', 'market correction opportunity', 'cash-flow positive', or 'ready to buy' in a conclusion without evidence supporting that exact statement.
