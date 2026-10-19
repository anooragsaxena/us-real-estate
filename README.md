# U.S. Real Estate Investment Research

A lightweight, evidence-driven tracker for evaluating U.S. detached single-family rental properties for a Canadian tax resident.

## Start here

- [Investment policy](INVESTMENT_POLICY.md): investment mandate, eligibility, underwriting thresholds, and decision rules.
- [AGENTS.md](AGENTS.md): operating instructions for Codex and other research/development agents.
- [Calculator](cashflow.py): auditable, standard-library Python underwriting calculations.
- [SQLite schema](schema.sql): property listings, price observations, rental comparables, and assessment history.
- [CLI](tracker.py): create a local database, record listings and comparables, underwrite properties, and review results.

## Requirements

Python 3.10+; no third-party Python packages.

## Quick start

    python3 tracker.py init
    python3 tracker.py add --source Zillow --url "https://www.zillow.com/example" --address "123 Example St" --city Tucson --state AZ --beds 3 --baths 2 --price 225000
    python3 tracker.py rent-comp --listing-id 1 --rent 1900 --url "https://www.zillow.com/rental-example" --address "Comparable address" --beds 3 --baths 2 --observed 2026-10-19
    python3 tracker.py assess --listing-id 1 --input examples/underwriting.json --scenario base
    python3 tracker.py report
    python3 tracker.py export
    python3 tracker.py --db data/other.sqlite init
    python3 tracker.py --db data/other.sqlite import --input data/research-export.json
    python3 -m unittest discover -s tests -v

The example is a fabricated demonstration, NOT a live listing or rent comp. Use real verified URLs and property details in actual research. The example JSON contains hypothetical financing and cost assumptions.

CLI uses data/real_estate.sqlite by default. Override with --db PATH before the command. Local DB files are gitignored; never commit personal financial or tenant information.

## Process

1. Identify qualified houses in AZ, NV, WA, OR, or ID; record original Zillow/Redfin URL, inspection date, facts, and listing price.
2. Record at least three nearby, comparable long-term rental advertisements or documented leases when available, and explain adjustments. Advertised asking rents are NOT achieved rents.
3. Supply property-specific financing, taxes, insurance, HOA, expenses, reserves, repair and closing estimates in an underwriting JSON file.
4. Run a base and downside assessment; compare with the investment policy. Reassess when listings, rates or rent evidence change.
5. Issue a BUY / WATCH / REJECT recommendation only after sources and assumptions have been verified. The calculator's screen result is NOT a purchase authorization.

## Sharing research across workspaces

The SQLite file remains local and gitignored, so a fresh Codex workspace will not automatically have your research data. Use the export/import commands above to move a complete JSON snapshot between initialized databases. The default export path is also ignored by git.

Because this GitHub repository is **public**, inspect any snapshot for private notes or financial information **before deliberately committing** one for other agents to read. No automatic publication or synchronization occurs.

No automated Zillow/Redfin scraping is implemented. Follow each site's terms and use permitted sources or manual capture.

All monetary values are USD unless explicitly labeled. This tool models pre-income-tax property economics; cross-border income-tax, estate-tax, FIRPTA and CAD/USD effects require separate professional review.
