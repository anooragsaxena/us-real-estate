"""SQLite listing tracker; Python standard library only."""
import argparse
import json
import sqlite3
import sys
from dataclasses import asdict
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from cashflow import Inputs, underwrite
from comps import sale_comps_summary


ROOT = Path(__file__).resolve().parent
DEFAULT_DB = ROOT / "data" / "real_estate.sqlite"


def connect(db_path, initialize=False):
    if not initialize and not db_path.exists():
        raise ValueError("database not initialized; run: python3 tracker.py init")
    if initialize:
        db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    if initialize:
        conn.executescript((ROOT / "schema.sql").read_text(encoding="utf-8"))
        # Migrate older databases in place; rerunning init is safe.
        known = {r["name"] for r in conn.execute("PRAGMA table_info(listings)")}
        for col, sql_type in (("finished_sqft", "REAL"), ("year_built", "INTEGER")):
            if col not in known:
                conn.execute(f"ALTER TABLE listings ADD COLUMN {col} {sql_type}")
        sale_cols = {r["name"] for r in conn.execute("PRAGMA table_info(sale_comps)")}
        if "verification_url" not in sale_cols:
            conn.execute("ALTER TABLE sale_comps ADD COLUMN verification_url TEXT")
        conn.commit()
    return conn


def valid_date(value):
    date.fromisoformat(value)
    return value


def valid_url(url, source=None):
    parts = urlparse(url)
    host = (parts.hostname or "").lower()
    if parts.scheme != "https" or not host:
        raise ValueError("source URL must be a full HTTPS URL")
    if source:
        domain = "zillow.com" if source == "Zillow" else "redfin.com"
        if not (host == domain or host.endswith("." + domain)):
            raise ValueError(f"{source} listing URL must be on {domain}")
    return url


def eligible(beds, baths):
    return (beds == 2 and baths == 2) or (beds == 3 and baths >= 2)


def cmd_add(conn, a):
    if not eligible(a.beds, a.baths):
        raise ValueError("only detached 2BD/2BA or 3BD/2+BA homes are eligible")
    valid_url(a.url, a.source)
    valid_date(a.observed)
    if a.price <= 0:
        raise ValueError("price must be positive")
    with conn:
        cur = conn.execute(
            """INSERT INTO listings
            (source,url,address,city,state,zip_code,bedrooms,bathrooms,asking_price_usd,
             finished_sqft,year_built,observed_on,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (a.source, a.url, a.address, a.city, a.state, a.zip,
             a.beds, a.baths, a.price, a.sqft, a.year_built, a.observed, a.notes),
        )
        listing_id = cur.lastrowid
        conn.execute(
            """INSERT INTO price_observations
            (listing_id,observed_on,asking_price_usd,listing_status,source_url,notes)
            VALUES (?,?,?,'active',?,?)""",
            (listing_id, a.observed, a.price, a.url, a.notes),
        )
    print(f"Added listing #{listing_id}")


def cmd_observe(conn, a):
    valid_date(a.observed)
    row = conn.execute("SELECT url FROM listings WHERE id=?", (a.listing_id,)).fetchone()
    if row is None:
        raise ValueError("listing not found")
    if a.price <= 0:
        raise ValueError("price must be positive")
    with conn:
        conn.execute(
            """UPDATE listings SET asking_price_usd=?, listing_status=?, observed_on=?
               WHERE id=?""",
            (a.price, a.status, a.observed, a.listing_id),
        )
        conn.execute(
            """INSERT INTO price_observations
               (listing_id,observed_on,asking_price_usd,listing_status,source_url,notes)
               VALUES (?,?,?,?,?,?)""",
            (a.listing_id, a.observed, a.price, a.status, row["url"], a.notes),
        )
    print(f"Recorded price observation for #{a.listing_id}")


def cmd_rent_comp(conn, a):
    valid_date(a.observed)
    valid_url(a.url)
    if a.rent <= 0 or a.beds <= 0 or a.baths <= 0:
        raise ValueError("rent, bedrooms and bathrooms must be positive")
    with conn:
        cur = conn.execute(
            """INSERT INTO rental_comps
               (listing_id,address,bedrooms,bathrooms,asking_rent_usd,source_url,
                observed_on,notes) VALUES (?,?,?,?,?,?,?,?)""",
            (a.listing_id, a.address, a.beds, a.baths, a.rent, a.url,
             a.observed, a.notes),
        )
    print(f"Added rental comparable #{cur.lastrowid} for listing #{a.listing_id}")



def cmd_sale_comp(conn, a):
    """Save a CLOSED arm's-length sale candidate; never an active ask."""
    valid_date(a.sold_on)
    valid_date(a.observed)
    valid_url(a.url)
    if a.verified and not a.verification_url:
        raise ValueError("--verified requires independent --verification-url")
    if a.verification_url:
        valid_url(a.verification_url)
    if (a.price <= 0 or a.sqft <= 0 or a.beds <= 0 or a.baths <= 0
            or a.distance < 0 or a.sold_on > a.observed):
        raise ValueError("closed sale price, date, size, bedrooms/baths and distance must be valid")
    with conn:
        cur = conn.execute(
            """INSERT INTO sale_comps
               (listing_id,address,sold_price_usd,sold_on,bedrooms,bathrooms,
                finished_sqft,year_built,distance_miles,source_url,observed_on,
                sale_verified,verification_url,transaction_type,condition_relation,notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (a.listing_id, a.address, a.price, a.sold_on, a.beds, a.baths,
             a.sqft, a.year_built, a.distance, a.url, a.observed,
             int(a.verified), a.verification_url, a.transaction, a.condition, a.notes),
        )
    print(f"Saved closed sale comp #{cur.lastrowid} for listing #{a.listing_id}")


def cmd_finding(conn, a):
    valid_date(a.observed)
    if a.url:
        valid_url(a.url)
    if a.cost is not None and a.cost < 0:
        raise ValueError("cost cannot be negative")
    with conn:
        cur = conn.execute(
            """INSERT INTO findings
               (listing_id,category,severity,evidence_status,resolution,
                description,estimated_cost_usd,evidence_url,observed_on,notes)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (a.listing_id, a.category, a.severity, a.evidence, a.resolution,
             a.description, a.cost, a.url, a.observed, a.notes),
        )
    print(f"Saved finding #{cur.lastrowid} for listing #{a.listing_id}")


def get_sale_summary(conn, listing_id, as_of=None, radius=1.0):
    subject = conn.execute("SELECT * FROM listings WHERE id=?", (listing_id,)).fetchone()
    if subject is None:
        raise ValueError("listing not found")
    comps = conn.execute("SELECT * FROM sale_comps WHERE listing_id=? ORDER BY sold_on DESC",
                         (listing_id,)).fetchall()
    return sale_comps_summary(subject, comps, as_of=as_of, radius_miles=radius)


def cmd_comps(conn, a):
    if a.radius > 1.0 and not a.radius_reason.strip():
        raise ValueError("--radius-reason required when comparing beyond 1 mile")
    summary = get_sale_summary(conn, a.listing_id, as_of=a.as_of, radius=a.radius)
    print("Closed sales recorded:", summary["total_sale_comps"])
    print("Strict screen-qualified:", summary["screen_qualified_sale_comps"])
    print("Radius (miles):", summary["radius_miles"])
    if summary["median_closed_price_usd_unadjusted"] is not None:
        print(f"Median closed price (unadjusted): USD {summary['median_closed_price_usd_unadjusted']:,.0f}")
        print(f"Median sold price/sqft (unadjusted): USD {summary['median_closed_price_per_sqft_usd_unadjusted']:,.0f}")
        print(f"Ask vs median: {summary['ask_vs_median_pct']:+.1f}% (descriptive ONLY)")
    else:
        print("No qualified neighborhood closed-sale comparisons available.")
    for bad in summary["excluded"]:
        print("EXCLUDE #" + str(bad["id"]) + ": " + ", ".join(bad["reasons"]))
    print(summary["note"])


def cmd_assess(conn, a):
    row = conn.execute("SELECT * FROM listings WHERE id=?", (a.listing_id,)).fetchone()
    if row is None:
        raise ValueError("listing not found")
    if not eligible(row["bedrooms"], row["bathrooms"]):
        raise ValueError("listing does not meet property eligibility")
    raw = json.loads(a.input.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("underwriting input must be a JSON object")
    p = Inputs(**raw)
    result = underwrite(p)
    comp_count = conn.execute(
        "SELECT COUNT(*) FROM rental_comps WHERE listing_id=?", (a.listing_id,)
    ).fetchone()[0]
    if a.radius > 1.0 and not a.radius_reason.strip():
        raise ValueError("--radius-reason required for comps beyond 1 mile")
    sale_summary = get_sale_summary(conn, a.listing_id, radius=a.radius)
    severe_count = conn.execute(
        """SELECT COUNT(*) FROM findings WHERE listing_id=? AND resolution='open'
           AND severity IN ('high','critical')""", (a.listing_id,)
    ).fetchone()[0]
    estimated_repairs = conn.execute(
        """SELECT COALESCE(SUM(estimated_cost_usd), 0) FROM findings
           WHERE listing_id=? AND resolution='open' AND category='condition'""",
        (a.listing_id,)
    ).fetchone()[0]
    repair_gap = max(0.0, estimated_repairs - p.upfront_repairs_usd)
    sale_summary["expanded_radius_reason"] = a.radius_reason
    result["sale_comparison"] = sale_summary
    result["unresolved_high_or_critical_findings"] = severe_count
    result["known_open_condition_repair_estimate_usd"] = estimated_repairs
    result["unfunded_condition_repair_estimate_usd"] = repair_gap
    # Evidence gate, never investment or purchase authorization.
    status = (
        "REVIEW" if result["base_target_pass"] and result["stress_nonnegative"]
        and comp_count >= 3 and sale_summary["screen_qualified_sale_comps"] >= 3
        and severe_count == 0 and repair_gap == 0 else "WATCH"
    )
    with conn:
        cur = conn.execute(
            """INSERT INTO assessments
               (listing_id,scenario,inputs_json,results_json,rent_comp_count,
                screen_status,notes) VALUES (?,?,?,?,?,?,?)""",
            (a.listing_id, a.scenario, json.dumps(asdict(p), sort_keys=True),
             json.dumps(result, sort_keys=True), comp_count, status, a.notes),
        )
    max_p = result["max_purchase_price_for_target_usd"]
    print(f"Assessment #{cur.lastrowid} | {status} | {a.scenario}")
    print(f"Asking: ${row['asking_price_usd']:,.0f}; modeled purchase/offer: ${p.purchase_price_usd:,.0f}")
    print(f"Rent comps recorded: {comp_count} (comparability NOT automatically verified)")
    print(f"Neighborhood sold comps screen-qualified: {sale_summary['screen_qualified_sale_comps']} (NOT an appraisal)")
    print(f"Open high/critical findings: {severe_count}")
    print(f"Unfunded estimated condition repairs: USD {repair_gap:,.0f}")
    if sale_summary["median_closed_price_usd_unadjusted"] is not None:
        print(f"Raw ask vs sale-comp median: {sale_summary['ask_vs_median_pct']:+.1f}% (NOT fair-value discount)")
    print(f"Base cash flow: ${result['monthly_cashflow_usd']:,.2f}/mo")
    print(f"Stress cash flow: ${result['stress_monthly_cashflow_usd']:,.2f}/mo")
    print(f"Cash needed: ${result['cash_needed_usd']:,.0f}; annual CoC: {result['annual_cash_on_cash_pct']:.2f}%" if result["annual_cash_on_cash_pct"] is not None else "Cash-on-cash: undefined")
    print(f"Rent required for target: ${result['required_monthly_rent_for_target_usd']:,.0f}/mo")
    print(f"Screening max price at fixed taxes/costs: ${max_p:,.0f}" if max_p is not None else "Max price: not defined for all-cash financing")
    print("Pre-income-tax illustration; source quality, financing and inspection require review.")


def cmd_report(conn):
    rows = conn.execute(
        """SELECT l.id,l.city,l.state,l.bedrooms,l.bathrooms,l.asking_price_usd,
           l.observed_on,l.listing_status,a.screen_status,a.results_json,
           a.rent_comp_count,a.assessed_at
           FROM listings l
           LEFT JOIN assessments a ON a.id=(
               SELECT MAX(a2.id) FROM assessments a2 WHERE a2.listing_id=l.id
           )
           ORDER BY l.state,l.city,l.id"""
    ).fetchall()
    if not rows:
        print("No listings yet.")
        return
    for r in rows:
        if r["results_json"]:
            metrics = json.loads(r["results_json"])
            suffix = (
                f"{r['screen_status']} cashflow=${metrics['monthly_cashflow_usd']:,.0f}/mo"
                f" stress=${metrics['stress_monthly_cashflow_usd']:,.0f}/mo"
                f" rent_comps={r['rent_comp_count']}"
                f" sale_comps={metrics.get('sale_comparison', {}).get('screen_qualified_sale_comps', 0)}"
            )
        else:
            suffix = "NOT ASSESSED"
        print(
            f"#{r['id']} {r['city']}, {r['state']} "
            f"{r['bedrooms']}BD/{r['bathrooms']:g}BA "
            f"asking=${r['asking_price_usd']:,.0f} "
            f"({r['observed_on']}, {r['listing_status']}) | {suffix}"
        )


def cmd_show(conn, a):
    row = conn.execute("SELECT * FROM listings WHERE id=?", (a.listing_id,)).fetchone()
    if row is None:
        raise ValueError("listing not found")
    result = {"listing": dict(row)}
    for table in ("price_observations", "rental_comps", "sale_comps", "findings", "assessments"):
        items = conn.execute(
            f"SELECT * FROM {table} WHERE listing_id=? ORDER BY id DESC",
            (a.listing_id,),
        ).fetchall()
        result[table] = [dict(item) for item in items]
    print(json.dumps(result, indent=2))


TABLES = ("listings", "price_observations", "rental_comps", "sale_comps", "findings", "assessments")


def cmd_export(conn, a):
    """Create an optional portable JSON snapshot; review before sharing."""
    payload = {"format_version": 1, "exported_on": date.today().isoformat()}
    for table in TABLES:
        payload[table] = [dict(row) for row in conn.execute(f"SELECT * FROM {table} ORDER BY id")]
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Exported snapshot to {a.output}. Review for private information before committing.")


def cmd_import(conn, a):
    """Restore into an empty, already initialized SQLite DB."""
    payload = json.loads(a.input.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("format_version") != 1:
        raise ValueError("unsupported or invalid snapshot format")
    if any(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0] for table in TABLES):
        raise ValueError("import requires an empty database to avoid data loss or duplicates")
    with conn:
        for table in TABLES:
            allowed = {r["name"] for r in conn.execute(f"PRAGMA table_info({table})")}
            for item in payload.get(table, []):
                if not isinstance(item, dict) or not item or set(item) - allowed:
                    raise ValueError(f"invalid fields in snapshot table {table}")
                columns = list(item)
                placeholders = ",".join("?" for _ in columns)
                names = ",".join(columns)
                conn.execute(
                    f"INSERT INTO {table} ({names}) VALUES ({placeholders})",
                    tuple(item[c] for c in columns),
                )
    print(f"Imported snapshot from {a.input}")


def build_parser():
    parser = argparse.ArgumentParser(description="US single-family rental investment tracker")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("init", help="initialize SQLite database")
    add = sub.add_parser("add", help="add Zillow/Redfin sale listing")
    for key in ("source", "url", "address", "city", "state"):
        add.add_argument("--" + key, required=True)
    add.add_argument("--zip", default="")
    add.add_argument("--beds", type=int, required=True)
    add.add_argument("--baths", type=float, required=True)
    add.add_argument("--price", type=float, required=True)
    add.add_argument("--sqft", type=float, help="finished area (required for qualified sale-comp analysis)")
    add.add_argument("--year-built", type=int)
    add.add_argument("--observed", default=date.today().isoformat())
    add.add_argument("--notes", default="")
    observe = sub.add_parser("observe", help="save another price/status observation")
    observe.add_argument("--listing-id", type=int, required=True)
    observe.add_argument("--price", type=float, required=True)
    observe.add_argument("--status", choices=["active","pending","sold","off_market","unknown"], default="active")
    observe.add_argument("--observed", default=date.today().isoformat())
    observe.add_argument("--notes", default="")
    comp = sub.add_parser("rent-comp", help="attach an advertised rental comparable")
    comp.add_argument("--listing-id", type=int, required=True)
    comp.add_argument("--rent", type=float, required=True)
    comp.add_argument("--url", required=True)
    comp.add_argument("--address", required=True)
    comp.add_argument("--beds", type=int, required=True)
    comp.add_argument("--baths", type=float, required=True)
    comp.add_argument("--observed", default=date.today().isoformat())
    comp.add_argument("--notes", default="")
    sale = sub.add_parser("sale-comp", help="add a closed-sale neighborhood comparable")
    sale.add_argument("--listing-id", type=int, required=True)
    sale.add_argument("--url", required=True)
    sale.add_argument("--address", required=True)
    sale.add_argument("--price", type=float, required=True, help="verified CLOSED sale price")
    sale.add_argument("--sold-on", required=True, help="actual YYYY-MM-DD close date")
    sale.add_argument("--beds", type=int, required=True)
    sale.add_argument("--baths", type=float, required=True)
    sale.add_argument("--sqft", type=float, required=True)
    sale.add_argument("--year-built", type=int)
    sale.add_argument("--distance", type=float, required=True, help="straight-line miles from subject")
    sale.add_argument("--transaction", choices=["unknown", "arm_length", "distressed"], default="unknown")
    sale.add_argument("--condition", choices=["unknown","similar","better","worse"], default="unknown")
    sale.add_argument("--verified", action="store_true", help="closed price/date verified against independent evidence")
    sale.add_argument("--verification-url", help="independent source for verified closing price and date")
    sale.add_argument("--observed", default=date.today().isoformat())
    sale.add_argument("--notes", default="")
    finding = sub.add_parser("finding", help="log an evidence-supported risk or repair concern")
    finding.add_argument("--listing-id", type=int, required=True)
    finding.add_argument("--category", choices=["condition","location","title","insurance","leasing","market","other"], required=True)
    finding.add_argument("--severity", choices=["low","medium","high","critical"], required=True)
    finding.add_argument("--evidence", choices=["suspected","confirmed"], default="suspected")
    finding.add_argument("--resolution", choices=["open","resolved"], default="open")
    finding.add_argument("--description", required=True)
    finding.add_argument("--cost", type=float, help="estimated remediation cost USD")
    finding.add_argument("--url", help="supporting evidence URL")
    finding.add_argument("--observed", default=date.today().isoformat())
    finding.add_argument("--notes", default="")
    comps = sub.add_parser("comps", help="summarize closed neighborhood sale comps")
    comps.add_argument("--listing-id", type=int, required=True)
    comps.add_argument("--as-of", default=date.today().isoformat())
    comps.add_argument("--radius", type=float, default=1.0)
    comps.add_argument("--radius-reason", default="")
    assess = sub.add_parser("assess", help="save a scenario and its calculations")
    assess.add_argument("--listing-id", type=int, required=True)
    assess.add_argument("--input", type=Path, required=True)
    assess.add_argument("--scenario", default="base")
    assess.add_argument("--radius", type=float, default=1.0)
    assess.add_argument("--radius-reason", default="")
    assess.add_argument("--notes", default="")
    export = sub.add_parser("export", help="write a portable JSON snapshot (may contain financial assumptions)")
    export.add_argument("--output", type=Path, default=ROOT / "data" / "research-export.json")
    restore = sub.add_parser("import", help="restore JSON into an empty initialized database")
    restore.add_argument("--input", type=Path, required=True)
    sub.add_parser("report", help="show most recent assessment for each property")
    show = sub.add_parser("show", help="show property, comp and assessment history")
    show.add_argument("--listing-id", type=int, required=True)
    return parser


def main(argv=None):
    p = build_parser()
    args = p.parse_args(argv)
    try:
        conn = connect(args.db, initialize=args.command == "init")
        try:
            if args.command == "init":
                print(f"SQLite database ready: {args.db}")
            elif args.command == "add":
                if args.source not in ("Zillow", "Redfin") or args.state not in ("AZ","NV","WA","OR","ID"):
                    raise ValueError("source/state not supported")
                cmd_add(conn, args)
            elif args.command == "observe":
                cmd_observe(conn, args)
            elif args.command == "rent-comp":
                cmd_rent_comp(conn, args)
            elif args.command == "sale-comp":
                cmd_sale_comp(conn, args)
            elif args.command == "finding":
                cmd_finding(conn, args)
            elif args.command == "comps":
                cmd_comps(conn, args)
            elif args.command == "assess":
                cmd_assess(conn, args)
            elif args.command == "export":
                cmd_export(conn, args)
            elif args.command == "import":
                cmd_import(conn, args)
            elif args.command == "report":
                cmd_report(conn)
            elif args.command == "show":
                cmd_show(conn, args)
        finally:
            conn.close()
    except (ValueError, TypeError, sqlite3.Error, OSError, json.JSONDecodeError) as exc:
        p.exit(2, f"Error: {exc}\n")


if __name__ == "__main__":
    main()
