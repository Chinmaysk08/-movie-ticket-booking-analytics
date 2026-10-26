"""
03_oracle_load.py -- load dataset v2 into the Oracle star schema
=================================================================

WHAT THIS SCRIPT DOES
---------------------
Reads `data/clean/bookings_clean.csv` and loads it into the seven tables
created by `src/02_create_schema.py`:

    DIM_CUSTOMER   1 row per customer
    DIM_MOVIE      1 row per movie
    DIM_THEATRE    1 row per multiplex
    DIM_DATE       1 row per calendar day in the design window
    DIM_PAYMENT    1 row per payment method x booking channel
    DIM_SHOW       1 row per show
    FACT_BOOKINGS  1 row per booking

It then queries Oracle back and reconciles the result against the clean CSV.
The script refuses to write a "success" report unless every check passes.

KEY DESIGN CHOICES
------------------
* Keys are assigned deterministically (sorted by the natural key), so a reload
  produces the same numbers.
* `date_key` is a smart key: YYYYMMDD. It is readable in query results and
  joins to DIM_DATE without a function call.
* Cancelled bookings are loaded. They are real events; every revenue and
  occupancy query filters `booking_status = 'Confirmed'`.
* Occupancy is not loaded. It is derived by `V_SHOW_PERFORMANCE` from confirmed
  seats and `seats_capacity`, so it cannot drift from its inputs.

RUN
---
    $env:PYTHONPATH = "D:\\chinmay\\movie-ticket-booking-analytics\\src"
    D:\\venvs\\cinema\\Scripts\\python.exe src\\03_oracle_load.py
"""

from datetime import datetime
from pathlib import Path

import pandas as pd

from db import get_conn

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean" / "bookings_clean.csv"
REPORT = ROOT / "reports" / "oracle_load_report.md"

START = "2025-10-01"
END = "2026-09-30"


def to_records(frame: pd.DataFrame, columns: list[str]) -> list[tuple]:
    """Convert a DataFrame slice to plain Python tuples for executemany."""
    records = []
    for row in frame[columns].itertuples(index=False, name=None):
        records.append(
            tuple(value.item() if hasattr(value, "item") else value for value in row)
        )
    return records


def fetch_scalar(cur, sql: str):
    cur.execute(sql)
    return cur.fetchone()[0]


def main() -> None:
    if not CLEAN.exists():
        raise SystemExit(f"Clean file not found: {CLEAN}")

    print("=" * 70)
    print("ORACLE LOAD -- dataset v2")
    print("=" * 70)
    print(f"Source: {CLEAN}")

    df = pd.read_csv(CLEAN, dtype={"phone": "string"})
    df["show_date_dt"] = pd.to_datetime(df["show_date"]).dt.date
    df["booking_dt"] = pd.to_datetime(df["booking_datetime"]).dt.to_pydatetime()
    print(f"Rows  : {len(df):,}")
    print(f"Cols  : {len(df.columns) - 2} (plus 2 temporary date columns)")

    # ------------------------------------------------------------------
    # 1. Build dimensions
    # ------------------------------------------------------------------
    customers = (
        df.sort_values("customer_id")
        .drop_duplicates("customer_id")
        [["customer_id", "customer_name", "customer_email", "phone", "age",
          "age_group", "gender", "city", "customer_type"]]
        .reset_index(drop=True)
    )
    customers.insert(0, "customer_key", range(1, len(customers) + 1))

    movies = (
        df.sort_values("movie_title")
        .drop_duplicates("movie_title")
        [["movie_title", "genre", "language", "rating"]]
        .reset_index(drop=True)
    )
    movies.insert(0, "movie_key", range(1, len(movies) + 1))

    screen_capacity = (
        df[["theatre_name", "city", "screen", "seats_capacity"]]
        .drop_duplicates()
        .sort_values(["theatre_name", "screen"])
    )
    theatres = (
        screen_capacity.groupby(["theatre_name", "city"], as_index=False)
        .agg(screens_in_sample=("screen", "nunique"),
             total_capacity=("seats_capacity", "sum"))
        .sort_values("theatre_name")
        .reset_index(drop=True)
    )
    theatres.insert(0, "theatre_key", range(1, len(theatres) + 1))

    payments = (
        df[["payment_method", "booking_channel"]]
        .drop_duplicates()
        .sort_values(["payment_method", "booking_channel"])
        .reset_index(drop=True)
    )
    payments.insert(0, "payment_key", range(1, len(payments) + 1))

    shows = (
        df.sort_values("show_id")
        .drop_duplicates("show_id")
        [["show_id", "movie_title", "theatre_name", "screen", "format",
          "seats_capacity", "show_date_dt", "show_time"]]
        .reset_index(drop=True)
    )
    shows = shows.merge(movies[["movie_key", "movie_title"]], on="movie_title", how="left")
    shows = shows.merge(theatres[["theatre_key", "theatre_name"]], on="theatre_name", how="left")
    shows.insert(0, "show_key", range(1, len(shows) + 1))

    if shows[["movie_key", "theatre_key"]].isna().any().any():
        raise SystemExit("A show could not be mapped to a movie or theatre key.")

    # Full calendar for the design window: 365 rows, including days with no show.
    calendar = pd.date_range(START, END, freq="D")
    dates = pd.DataFrame({
        "date_key": [int(day.strftime("%Y%m%d")) for day in calendar],
        "full_date": [day.date() for day in calendar],
        "day_of_month": [day.day for day in calendar],
        "day_of_week": [day.isoweekday() for day in calendar],
        "day_name": [day.day_name() for day in calendar],
        "month_number": [day.month for day in calendar],
        "month_name": [day.month_name() for day in calendar],
        "quarter": [day.quarter for day in calendar],
        "year": [day.year for day in calendar],
        "is_weekend": ["Y" if day.weekday() >= 5 else "N" for day in calendar],
    })

    print()
    print("Dimension sizes")
    print(f"  customers : {len(customers):>6,}")
    print(f"  movies    : {len(movies):>6,}")
    print(f"  theatres  : {len(theatres):>6,}")
    print(f"  dates     : {len(dates):>6,}")
    print(f"  payments  : {len(payments):>6,}")
    print(f"  shows     : {len(shows):>6,}")

    # ------------------------------------------------------------------
    # 2. Build the fact rows and check every foreign key resolves
    # ------------------------------------------------------------------
    customer_map = dict(zip(customers["customer_id"], customers["customer_key"]))
    show_map = dict(zip(shows["show_id"], shows["show_key"]))
    payment_map = {
        (row.payment_method, row.booking_channel): row.payment_key
        for row in payments.itertuples(index=False)
    }

    fact = pd.DataFrame({
        "booking_id": df["booking_id"],
        "customer_key": df["customer_id"].map(customer_map),
        "show_key": df["show_id"].map(show_map),
        "date_key": df["show_date"].str.replace("-", "", regex=False).astype(int),
        "payment_key": [
            payment_map.get((method, channel))
            for method, channel in zip(df["payment_method"], df["booking_channel"])
        ],
        "ticket_type": df["ticket_type"],
        "seats": df["seats"],
        "ticket_price": df["ticket_price"],
        "convenience_fee": df["convenience_fee"],
        "promo_code": df["promo_code"],
        "discount_amount": df["discount_amount"],
        "total_amount": df["total_amount"],
        "booking_status": df["booking_status"],
        "booking_datetime": df["booking_dt"],
    })

    for column in ["customer_key", "show_key", "payment_key", "date_key"]:
        missing = int(fact[column].isna().sum())
        if missing:
            raise SystemExit(f"{missing} fact rows have no {column}; aborting load.")

    print(f"  fact rows : {len(fact):>6,}")

    # ------------------------------------------------------------------
    # 3. Insert
    # ------------------------------------------------------------------
    con = get_conn()
    cur = con.cursor()
    try:
        existing = fetch_scalar(cur, "select count(*) from fact_bookings")
        if existing:
            raise SystemExit(
                f"fact_bookings already contains {existing:,} rows. "
                "Run src/02_create_schema.py first to rebuild the empty schema."
            )

        insert_specs = [
            ("dim_customer",
             "insert into dim_customer (customer_key, customer_id, customer_name, "
             "customer_email, phone, age, age_group, gender, city, customer_type) "
             "values (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)",
             customers,
             ["customer_key", "customer_id", "customer_name", "customer_email",
              "phone", "age", "age_group", "gender", "city", "customer_type"]),
            ("dim_movie",
             "insert into dim_movie (movie_key, movie_title, genre, language, rating) "
             "values (:1,:2,:3,:4,:5)",
             movies,
             ["movie_key", "movie_title", "genre", "language", "rating"]),
            ("dim_theatre",
             "insert into dim_theatre (theatre_key, theatre_name, city, "
             "screens_in_sample, total_capacity) values (:1,:2,:3,:4,:5)",
             theatres,
             ["theatre_key", "theatre_name", "city", "screens_in_sample", "total_capacity"]),
            ("dim_date",
             "insert into dim_date (date_key, full_date, day_of_month, day_of_week, "
             "day_name, month_number, month_name, quarter, year, is_weekend) "
             "values (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10)",
             dates,
             ["date_key", "full_date", "day_of_month", "day_of_week", "day_name",
              "month_number", "month_name", "quarter", "year", "is_weekend"]),
            ("dim_payment",
             "insert into dim_payment (payment_key, payment_method, booking_channel) "
             "values (:1,:2,:3)",
             payments,
             ["payment_key", "payment_method", "booking_channel"]),
            ("dim_show",
             "insert into dim_show (show_key, show_id, movie_key, theatre_key, screen, "
             "format, seats_capacity, show_date, show_time) "
             "values (:1,:2,:3,:4,:5,:6,:7,:8,:9)",
             shows,
             ["show_key", "show_id", "movie_key", "theatre_key", "screen", "format",
              "seats_capacity", "show_date_dt", "show_time"]),
        ]

        print()
        print("Loading")
        for table, sql, frame, columns in insert_specs:
            cur.executemany(sql, to_records(frame, columns))
            print(f"  {table:14s} {cur.rowcount:>6,} rows")

        cur.executemany(
            "insert into fact_bookings (booking_id, customer_key, show_key, date_key, "
            "payment_key, ticket_type, seats, ticket_price, convenience_fee, promo_code, "
            "discount_amount, total_amount, booking_status, booking_datetime) "
            "values (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14)",
            to_records(fact, ["booking_id", "customer_key", "show_key", "date_key",
                              "payment_key", "ticket_type", "seats", "ticket_price",
                              "convenience_fee", "promo_code", "discount_amount",
                              "total_amount", "booking_status", "booking_datetime"]),
        )
        print(f"  {'fact_bookings':14s} {cur.rowcount:>6,} rows")

        con.commit()
        print()
        print("Committed.")
    except Exception:
        con.rollback()
        raise
    finally:
        cur.close()
        con.close()

    # ------------------------------------------------------------------
    # 4. Reconcile Oracle against the clean CSV
    # ------------------------------------------------------------------
    confirmed = df[df["booking_status"] == "Confirmed"]
    pandas_kpi = {
        "bookings": len(df),
        "confirmed_bookings": len(confirmed),
        "confirmed_tickets": int(confirmed["seats"].sum()),
        "confirmed_revenue": int(confirmed["total_amount"].sum()),
        "cancellation_rate_pct": round(100 * (df["booking_status"] == "Cancelled").mean(), 2),
        "mean_occupancy_pct": round(
            100 * df.groupby("show_id")["show_occupancy_rate"].first().mean(), 2
        ),
    }
    pandas_counts = {
        "DIM_CUSTOMER": len(customers),
        "DIM_MOVIE": len(movies),
        "DIM_THEATRE": len(theatres),
        "DIM_DATE": len(dates),
        "DIM_PAYMENT": len(payments),
        "DIM_SHOW": len(shows),
        "FACT_BOOKINGS": len(fact),
    }

    con = get_conn()
    cur = con.cursor()
    try:
        oracle_counts = {}
        for table in pandas_counts:
            oracle_counts[table] = fetch_scalar(cur, f"select count(*) from {table}")

        oracle_kpi = {
            "bookings": fetch_scalar(cur, "select count(*) from fact_bookings"),
            "confirmed_bookings": fetch_scalar(
                cur, "select count(*) from fact_bookings where booking_status = 'Confirmed'"
            ),
            "confirmed_tickets": fetch_scalar(
                cur, "select sum(seats) from fact_bookings where booking_status = 'Confirmed'"
            ),
            "confirmed_revenue": fetch_scalar(
                cur, "select sum(total_amount) from fact_bookings where booking_status = 'Confirmed'"
            ),
            "cancellation_rate_pct": fetch_scalar(
                cur,
                "select round(100 * sum(case when booking_status = 'Cancelled' then 1 else 0 end)"
                " / count(*), 2) from fact_bookings",
            ),
            "mean_occupancy_pct": fetch_scalar(
                cur, "select round(100 * avg(occupancy_rate), 2) from v_show_performance"
            ),
        }

        formula_failures = fetch_scalar(
            cur,
            "select count(*) from fact_bookings "
            "where total_amount != ticket_price * seats + convenience_fee - discount_amount",
        )
        orphan_bookings = fetch_scalar(
            cur,
            "select count(*) from fact_bookings f "
            "left join dim_customer c on c.customer_key = f.customer_key "
            "left join dim_show s on s.show_key = f.show_key "
            "left join dim_date d on d.date_key = f.date_key "
            "left join dim_payment p on p.payment_key = f.payment_key "
            "where c.customer_key is null or s.show_key is null "
            "or d.date_key is null or p.payment_key is null",
        )
        out_of_calendar = fetch_scalar(
            cur,
            "select count(*) from dim_show s "
            "left join dim_date d on d.full_date = s.show_date "
            "where d.date_key is null",
        )
        shows_over_capacity = fetch_scalar(
            cur,
            "select count(*) from v_show_performance where confirmed_seats > seats_capacity",
        )
        shows_outside_window = fetch_scalar(
            cur,
            "select count(*) from dim_show "
            "where show_date < date '2025-10-01' or show_date > date '2026-09-30'",
        )
    finally:
        cur.close()
        con.close()

    # ------------------------------------------------------------------
    # 5. Build the check table
    # ------------------------------------------------------------------
    checks = []
    for table, expected in pandas_counts.items():
        actual = oracle_counts[table]
        checks.append((f"{table} row count", expected, actual, actual == expected))

    for key, expected in pandas_kpi.items():
        actual = oracle_kpi[key]
        if isinstance(expected, float):
            passed = abs(actual - expected) <= 0.01
        else:
            passed = actual == expected
        checks.append((f"KPI: {key}", expected, actual, passed))

    checks.extend([
        ("Revenue formula failures", 0, formula_failures, formula_failures == 0),
        ("Fact rows with a missing dimension", 0, orphan_bookings, orphan_bookings == 0),
        ("Shows outside the date dimension", 0, out_of_calendar, out_of_calendar == 0),
        ("Shows with seats above capacity", 0, shows_over_capacity, shows_over_capacity == 0),
        ("Shows outside the design window", 0, shows_outside_window, shows_outside_window == 0),
    ])

    print()
    print("=" * 70)
    print("RECONCILIATION")
    print("=" * 70)
    for name, expected, actual, passed in checks:
        flag = "PASS" if passed else "FAIL"
        print(f"  [{flag}] {name:42s} pandas={expected!s:>12} oracle={actual!s:>12}")

    failed = [name for name, _, _, passed in checks if not passed]
    if failed:
        raise SystemExit(f"Reconciliation failed {len(failed)} check(s): {failed}")

    # ------------------------------------------------------------------
    # 6. Write the load report from measured values
    # ------------------------------------------------------------------
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Oracle Load Report — dataset v2",
        "",
        f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}",
        f"Source: `{CLEAN.relative_to(ROOT)}`",
        f"Schema: `sql/01_schema.sql` (Oracle 26ai Free, FREEPDB1)",
        "",
        "Every number below was read back from Oracle after the commit and compared",
        "with the clean CSV. The loader would have stopped before writing this report",
        "if any check failed.",
        "",
        "## Row counts",
        "",
        "| Table | Rows | Matches CSV |",
        "|---|---:|---|",
    ]
    for table, expected in pandas_counts.items():
        lines.append(f"| `{table}` | {oracle_counts[table]:,} | ✅ |")

    lines += [
        "",
        "## KPI reconciliation",
        "",
        "| KPI | Pandas (clean CSV) | Oracle | Match |",
        "|---|---:|---:|---|",
    ]
    for key, expected in pandas_kpi.items():
        actual = oracle_kpi[key]
        if isinstance(expected, float):
            expected_text = f"{expected:,.2f}"
            actual_text = f"{actual:,.2f}"
        else:
            expected_text = f"{expected:,}"
            actual_text = f"{actual:,}"
        lines.append(f"| `{key}` | {expected_text} | {actual_text} | ✅ |")

    lines += [
        "",
        "## Integrity checks",
        "",
        "| Check | Expected | Actual | Result |",
        "|---|---:|---:|---|",
    ]
    for name, expected, actual, passed in checks[-5:]:
        lines.append(f"| {name} | {expected} | {actual} | {'✅' if passed else '❌'} |")

    lines += [
        "",
        "## Notes",
        "",
        "- **79 screens, not 80.** The generator designs 16 multiplexes × 5 screens,",
        "  but one screen (Screen 3 at Deccan Mall Cinemas - Baner) has no bookings",
        "  in the 10,000-row sample. `DIM_THEATRE.screens_in_sample` records what the",
        "  sample contains; it is not a claim about the multiplex's real layout.",
        "- **18 payment combinations, not 20.** Kiosk does not appear with NetBanking",
        "  or Wallet in this dataset.",
        "- **365 calendar rows.** `DIM_DATE` covers the full design window",
        "  (2025-10-01 → 2026-09-30), including days with no show, so time-series",
        "  queries do not silently skip empty dates.",
        "- **Cancelled bookings are retained.** They are excluded from revenue and",
        "  occupancy by filtering `booking_status = 'Confirmed'`.",
        "- **Occupancy is derived.** `V_SHOW_PERFORMANCE` computes confirmed seats ÷",
        "  `seats_capacity`; the value is never stored, so it cannot drift.",
        "",
        "## Reproduce",
        "",
        "```powershell",
        '$env:PYTHONPATH = "D:\\chinmay\\movie-ticket-booking-analytics\\src"',
        "D:\\venvs\\cinema\\Scripts\\python.exe src\\02_create_schema.py",
        "D:\\venvs\\cinema\\Scripts\\python.exe src\\03_oracle_load.py",
        "```",
        "",
    ]
    REPORT.write_text("\n".join(lines), encoding="utf-8")

    print()
    print(f"Report written: {REPORT}")
    print("ALL RECONCILIATION CHECKS PASSED")


if __name__ == "__main__":
    main()
