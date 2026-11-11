"""
05_export_powerbi.py -- export the Oracle star schema to CSV for Power BI
=========================================================================

WHY THIS EXISTS
---------------
Power BI Desktop is not installed on this machine, and the reviewer may not have
an Oracle client. Exporting the star schema to CSV means the dashboard can be
built from files, and the same files can be inspected without a database.

WHAT IT EXPORTS
---------------
    data/powerbi/dim_customer.csv
    data/powerbi/dim_movie.csv
    data/powerbi/dim_theatre.csv
    data/powerbi/dim_show.csv
    data/powerbi/dim_date.csv
    data/powerbi/dim_payment.csv
    data/powerbi/fact_bookings.csv
    data/powerbi/v_show_performance.csv   <- show-level KPIs, occupancy derived

The CSVs are regenerated artifacts and are git-ignored. Oracle remains the
source of truth.

DATE FORMAT
-----------
Power BI parses ISO dates reliably. `full_date` and `show_date` are written as
YYYY-MM-DD; `booking_datetime` keeps its time as YYYY-MM-DD HH:MM:SS.

RUN
---
    $env:PYTHONPATH = "D:\\chinmay\\movie-ticket-booking-analytics\\src"
    D:\\venvs\\cinema\\Scripts\\python.exe src\\05_export_powerbi.py
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from db import get_conn

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "powerbi"

# (object name, kind) -- kind decides the date format.
EXPORTS = [
    ("dim_customer", "table"),
    ("dim_movie", "table"),
    ("dim_theatre", "table"),
    ("dim_show", "table"),
    ("dim_date", "table"),
    ("dim_payment", "table"),
    ("fact_bookings", "table"),
    ("v_show_performance", "view"),
]

DATE_ONLY_COLUMNS = {"full_date", "show_date"}


def format_value(column: str, value):
    """Make Oracle values CSV-safe and Power BI-friendly."""
    if value is None:
        return ""
    if isinstance(value, datetime):
        if column in DATE_ONLY_COLUMNS:
            return value.strftime("%Y-%m-%d")
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if hasattr(value, "item"):  # numpy scalar
        return value.item()
    return value


def export_object(cur, name: str) -> int:
    cur.execute(f"select * from {name}")
    columns = [description[0].lower() for description in cur.description]
    rows = cur.fetchall()

    frame = pd.DataFrame(
        [[format_value(column, value) for column, value in zip(columns, row)]
         for row in rows],
        columns=columns,
    )

    path = OUT / f"{name}.csv"
    frame.to_csv(path, index=False, encoding="utf-8")
    return len(frame)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    con = get_conn()
    cur = con.cursor()
    try:
        print(f"Exporting to {OUT}")
        print()
        summary = []
        for name, kind in EXPORTS:
            count = export_object(cur, name)
            summary.append((name, kind, count))
            print(f"  {name:22s} {count:>7,} rows")
    finally:
        cur.close()
        con.close()

    # Re-read one file to prove the export is valid CSV, not just a write call.
    fact = pd.read_csv(OUT / "fact_bookings.csv")
    shows = pd.read_csv(OUT / "v_show_performance.csv")
    revenue = int(fact.loc[fact["booking_status"] == "Confirmed", "total_amount"].sum())
    occupancy = round(100 * shows["occupancy_rate"].mean(), 2)

    print()
    print("=" * 60)
    print("EXPORT VERIFICATION")
    print("=" * 60)
    print(f"  fact rows              : {len(fact):,}")
    print(f"  confirmed revenue      : INR {revenue:,}")
    print(f"  mean show occupancy    : {occupancy:.2f}%")

    if len(fact) != 10_000:
        raise SystemExit(f"Expected 10,000 fact rows, exported {len(fact):,}.")

    expected = json.loads((ROOT / "reports" / "generation_summary.json").read_text(encoding="utf-8"))
    expected_revenue = int(expected["revenue_confirmed_inr"])
    if revenue != expected_revenue:
        raise SystemExit(
            f"Expected revenue INR {expected_revenue:,}, exported {revenue:,}."
        )
    print(f"  revenue matches generator: INR {expected_revenue:,}")

    print()
    print("Export is consistent with the clean dataset.")


if __name__ == "__main__":
    main()
