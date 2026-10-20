---
name: property-evaluation
description: Research, screen, value and underwrite US detached single-family long-term rentals using verified neighborhood sale comps and rental comps. Use for identifying candidate listings, investigating apparent bargains, modeling repairs and financing, and documenting WATCH/REVIEW decisions.
---

# Property Evaluation — Research and Underwriting Skill

## Required context

Read repository `INVESTMENT_POLICY.md` and `AGENTS.md` before any evaluation. This skill is the repeatable **method**, not an override of investment policy. Investor is a **Canadian tax resident**, seeking U.S. long-term rentals, with **$200/month minimum** and **$250/month target** pre-personal-income-tax cash flow *after* mortgage and all operating costs. Only detached, fee-simple **2BD/2BA or 3BD/2+BA** homes in AZ, NV, WA, OR and ID. Do not underwrite using vacation/short-term rentals.

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
8. **Stress & decision** — Test combined 10% rent cut and >=1 month/year vacancy, plus adverse insurance/repair scenarios and rate reset where applicable. Document base cash flow, stressed cash flow, DSCR, cap rate, invested cash, cash-on-cash yield, and mathematical break-even price. Compare **valuation evidence** and **cash-flow price ceiling** as separate constraints; neither is an automatic offer price. Record WATCH / REVIEW screen, explicit reasons and what must change. Escalate to real appraisal/inspection/agent/lender/tax counsel before a transaction.
9. **Preserve work** — Use `tracker.py show`, `report` and `export` to save reproducible evidence. Keep live data local; commit only public non-sensitive dated case notes and fixtures with source links if needed. An export can contain private financial notes and is not automatically published.

## Sale comp safeguards / decision rules

- Closed prices **only** enter the sold-comp median. Active/pending asks may be discussed as supply/competition but never mixed into the closed-price median.
- Do not call a lower raw ask **undervalued** until location, age, size, condition, repairs, financing constraints and sale concessions have been reconciled. A raw percentage gap is descriptive, not a discount to intrinsic or appraised value.
- Three recorded sales is a **quantity** threshold, not proof of credibility. Assess similarity, verification and recency manually. A severe unresolved finding blocks advancing an automated screen.
- Repair/inspection omissions and generic insurance/tax estimates should be explicit gating gaps, even when software returns REVIEW. No automated screening status means purchase approval.
- Fannie Mae guidance expects market-supported adjustments, not arbitrary dollar-per-sq-ft or dollar-for-dollar renovation costs. Our simple tracker deliberately **does not auto-adjust sale prices**.

## Minimum report template

`As-of date | Zillow/Redfin property URL | eligibility/status | ask and history | neighborhood sold comps table (date, distance, area, price, condition, source) | raw price gap and limitations | why priced lower (evidence/unknowns) | estimated immediate rehab | rent comp table | assumptions & financing | cash flow base/downside, DSCR, cash-on-cash | cash-flow-compatible max price vs comp context | critical risks | WATCH/REVIEW/REJECT with rationale | next verification steps`.

Never put 'bargain', 'below market', 'market correction opportunity', 'cash-flow positive', or 'ready to buy' in a conclusion without evidence supporting that exact statement.
