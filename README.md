# U.S. Real Estate Investment Research

A lightweight, evidence-driven tracker for evaluating U.S. detached single-family rental properties for a Canadian tax resident.

## Start here

- [Investment policy](INVESTMENT_POLICY.md): investment mandate, eligibility, underwriting thresholds, and decision rules.
- [AGENTS.md](AGENTS.md): operating instructions for Codex and other research/development agents.
- [Property-evaluation skill](.agents/skills/property-evaluation/SKILL.md): complete repeatable Zillow/Redfin research, neighborhood sale comps and rehabilitation investigation.
- [Calculator](cashflow.py): auditable, standard-library Python underwriting calculations.
- [SQLite schema](schema.sql): property listings, price observations, neighborhood sold comps, rental comps, property findings, and assessment history.
- [CLI](tracker.py): create a local database, record listings and comparables, underwrite properties, and review results.

## Requirements

Python 3.10+; no third-party Python packages.

## Quick start

    python3 tracker.py init
    python3 tracker.py add --source Zillow --url "https://www.zillow.com/example" --address "123 Example St" --city Tucson --state AZ --beds 3 --baths 2 --sqft 1400 --price 225000
    python3 tracker.py rent-comp --listing-id 1 --rent 1900 --url "https://www.zillow.com/rental-example" --address "Comparable address" --beds 3 --baths 2 --observed 2026-10-19
    python3 tracker.py sale-comp --listing-id 1 --url "https://www.redfin.com/example-closed" --address "Sold comp" --price 230000 --sold-on 2026-09-01 --beds 3 --baths 2 --sqft 1400 --distance 0.5 --observed 2026-10-19
    python3 tracker.py comps --listing-id 1
    python3 tracker.py finding --listing-id 1 --category condition --severity medium --description "Possible aging HVAC: inspect" --observed 2026-10-19
    python3 tracker.py assess --listing-id 1 --input examples/underwriting.json --scenario base
    python3 tracker.py report
    python3 tracker.py export
    python3 tracker.py --db data/other.sqlite init
    python3 tracker.py --db data/other.sqlite import --input data/research-export.json
    python3 -m unittest discover -s tests -v

The example is a fabricated demonstration, NOT a live listing or rent comp. Use real verified URLs and property details in actual research. The example JSON contains hypothetical financing and cost assumptions.

CLI uses data/real_estate.sqlite by default. Override with --db PATH before the command. Local DB files are gitignored; never commit personal financial or tenant information.

## Process

1. Screen qualifying Zillow/Redfin detached homes; record address, current ask, date, bedrooms, bathrooms, finished area and original URL.
2. Record **at least 3 recent, nearby CLOSED-sale neighborhood comps** and assess size, condition, location and sale terms. Use `sale-comp` and `comps`; mark `--verified --transaction arm_length` only after independently verifying actual sold details. Raw sold-price median is descriptive, not appraised value.
3. Investigate why a home looks cheaper: deferred roof/HVAC work, renovations, legal/permit limitations, hazards, location disadvantage or distress. Use `finding` with `suspected/confirmed` status and evidence; include justified upfront repairs in underwriting.
4. Record at least 3 comparable long-term rental listings or actual leases, explaining differences. Advertised rents are not achieved rents.
5. Supply documented financing, property tax, insurance, HOA, management, vacancy, capex, repairs and reserves in an underwriting JSON; run base and downside with `assess`.
6. Record WATCH or REVIEW with uncertainty and next verification steps. **REVIEW requires both rental and neighborhood sale comps plus passing cash flow and no unresolved high/critical flags.** The CLI never authorizes a purchase.

The quick-start addresses and comp data are fabricated demonstrations, not live listings or verified sales. For a real evaluation, use original Zillow/Redfin links and confirm closed sales independently.

## Sharing research across workspaces

The SQLite file remains local and gitignored, so a fresh Codex workspace will not automatically have your research data. Use the export/import commands above to move a complete JSON snapshot between initialized databases. The default export path is also ignored by git.

Because this GitHub repository is **public**, inspect any snapshot for private notes or financial information **before deliberately committing** one for other agents to read. No automatic publication or synchronization occurs.

Rerun `python3 tracker.py init` against an older local SQLite database to add the new property-area fields, sold-comps and findings tables. Existing export/import snapshots remain compatible.

No automated Zillow/Redfin scraping is implemented. Follow each site's terms and use permitted sources or manual capture.

All monetary values are USD unless explicitly labeled. This tool models pre-income-tax property economics; cross-border income-tax, estate-tax, FIRPTA and CAD/USD effects require separate professional review.
