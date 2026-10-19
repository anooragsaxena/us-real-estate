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
             observed_on,notes) VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (a.source, a.url, a.address, a.city, a.state, a.zip,
             a.beds, a.baths, a.price, a.observed, a.notes),
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
    # This is an evidence screen, never investment or purchase authorization.
    status = (
        "REVIEW" if result["base_target_pass"]
        and result["stress_nonnegative"] and comp_count >= 3 else "WATCH"
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
                f" comps={r['rent_comp_count']}"
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
    for table in ("price_observations", "rental_comps", "assessments"):
        items = conn.execute(
            f"SELECT * FROM {table} WHERE listing_id=? ORDER BY id DESC",
            (a.listing_id,),
        ).fetchall()
        result[table] = [dict(item) for item in items]
    print(json.dumps(result, indent=2))


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
    assess = sub.add_parser("assess", help="save a scenario and its calculations")
    assess.add_argument("--listing-id", type=int, required=True)
    assess.add_argument("--input", type=Path, required=True)
    assess.add_argument("--scenario", default="base")
    assess.add_argument("--notes", default="")
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
            elif args.command == "assess":
                cmd_assess(conn, args)
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
