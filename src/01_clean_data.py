"""
01_clean_data.py -- Movie Ticket Booking Analytics, dataset v2
==============================================================

WHAT THIS SCRIPT DOES
---------------------
Reads the raw booking file, repairs every defect that
`notebooks/01_data_understanding.ipynb` found, derives the reporting fields,
runs 19 validation checks, and writes a new clean file.

It never edits the raw file. The raw file's SHA256 is recorded before and after
so we can prove it was not touched.

CLEANING PRINCIPLES
-------------------
1. Repair, don't delete. Every defect can be recovered from evidence already in
   the file (another booking of the same show, movie or customer). Dropping
   rows would lose real revenue and shrink the dataset below 10,000 bookings.
2. Repair inputs before checking derived rules. A bad show_time must be fixed
   before asking "was the booking made before the show started?".
3. Every repair is logged with before/after counts.
4. If any validation fails, the script stops. It does not write a file that
   only looks correct.

OUTPUTS
-------
    data/clean/bookings_clean.csv   <- 10,000 rows x 33 columns
    reports/cleaning_log.txt        <- every step + the validation table

RUN
---
    $env:PYTHONPATH = "D:\\chinmay\\movie-ticket-booking-analytics\\src"
    D:\\venvs\\cinema\\Scripts\\python.exe src\\01_clean_data.py
"""

import hashlib
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# 0. Paths, constants and logging
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "bookings_raw.csv"
CLEAN = ROOT / "data" / "clean" / "bookings_clean.csv"
LOG = ROOT / "reports" / "cleaning_log.txt"

START = pd.Timestamp("2025-10-01")
END = pd.Timestamp("2026-09-30")

VALID_TIMES = ("09:00", "12:15", "15:30", "18:45", "21:30", "23:45")
VALID_CITIES = {
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad",
    "Chennai", "Pune", "Kolkata", "Ahmedabad",
}
CITY_MAP = {"Bangalore": "Bengaluru", "Banglore": "Bengaluru"}

# Promo code -> discount rate. The four rates are unique, so a discount amount
# identifies the promo that produced it.
PROMO_RATES = {
    "FIRSTBUY5": 0.05,
    "WEEKEND10": 0.10,
    "STUDENT15": 0.15,
    "FAMILY20": 0.20,
}

TARGET_REVENUE = 10_787_567
TARGET_ROWS = 10_000

log_lines = []


def log(message: str = "") -> None:
    """Print a line and keep it for the log file."""
    print(message)
    if message:
        log_lines.append(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}")
    else:
        log_lines.append("")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# 1. Read the raw file
# ---------------------------------------------------------------------------
log("=" * 78)
log("CLEANING RUN -- dataset v2")
log("=" * 78)
log(f"Raw file : {RAW}")
log(f"Raw SHA256: {sha256(RAW)}")

raw_hash_before = sha256(RAW)

# phone is an identifier, not a quantity. Reading it as text prevents pandas
# from turning 8069729672 into 8.069730e+09 and losing the exact digits.
raw = pd.read_csv(RAW, dtype={"phone": "string"})
df = raw.copy()

log(f"Rows read : {len(df):,}")
log(f"Columns   : {len(df.columns)}")

# ---------------------------------------------------------------------------
# 2. Deduplicate
# ---------------------------------------------------------------------------
before = len(df)
df = df.drop_duplicates(subset="booking_id", keep="first").reset_index(drop=True)
log("")
log("STEP 1 -- Remove duplicate bookings")
log(f"  before : {before:,} rows")
log(f"  after  : {len(df):,} rows")
log(f"  removed: {before - len(df):,} rows with a repeated booking_id")

# ---------------------------------------------------------------------------
# 3. Normalise city labels
# ---------------------------------------------------------------------------
labels_before = df["city"].nunique()
normalised = df["city"].str.strip().str.title().replace(CITY_MAP)
rows_changed = int((df["city"] != normalised).sum())
df["city"] = normalised

log("")
log("STEP 2 -- Normalise city labels")
log(f"  distinct labels before: {labels_before}")
log(f"  distinct labels after : {df['city'].nunique()}")
log(f"  rows changed          : {rows_changed}")

# ---------------------------------------------------------------------------
# 4. Repair non-positive ticket prices
# ---------------------------------------------------------------------------
bad_price = df["ticket_price"] <= 0
n_bad_price = int(bad_price.sum())

recovered = (
    df.loc[bad_price, "total_amount"]
    - df.loc[bad_price, "convenience_fee"]
    + df.loc[bad_price, "discount_amount"]
) / df.loc[bad_price, "seats"]

if not np.allclose(recovered, recovered.round()):
    raise ValueError(
        "Price recovery produced a non-integer price. The revenue formula "
        "assumption no longer holds; inspect the rows before continuing."
    )

df.loc[bad_price, "ticket_price"] = recovered.round().astype("int64")

log("")
log("STEP 3 -- Recover non-positive ticket prices")
log(f"  rows repaired: {n_bad_price}")
log("  formula      : ticket_price = (total - fee + discount) / seats")
log(f"  new range    : {int(df['ticket_price'].min())} to {int(df['ticket_price'].max())}")

# ---------------------------------------------------------------------------
# 5. Repair show dates and times
# ---------------------------------------------------------------------------
# Both fields belong to the show, not the booking. Other bookings of the same
# show_id still hold the correct value, so the mode is the repair value.
df["show_date_dt"] = pd.to_datetime(df["show_date"], errors="coerce")
valid_time = df["show_time"].isin(VALID_TIMES)
valid_date = df["show_date_dt"].between(START, END)

bad_time = ~valid_time
bad_date = ~valid_date

time_mode = (
    df.loc[valid_time].groupby("show_id")["show_time"]
    .agg(lambda values: values.mode().iat[0])
)
date_mode = (
    df.loc[valid_date].groupby("show_id")["show_date"]
    .agg(lambda values: values.mode().iat[0])
)

df.loc[bad_time, "show_time"] = df.loc[bad_time, "show_id"].map(time_mode)
df.loc[bad_date, "show_date"] = df.loc[bad_date, "show_id"].map(date_mode)
df["show_date_dt"] = pd.to_datetime(df["show_date"], errors="coerce")

log("")
log("STEP 4 -- Repair show dates and times")
log(f"  invalid show_time rows : {int(bad_time.sum())}")
log(f"  out-of-period date rows: {int(bad_date.sum())}")
log(f"  shows without a valid time to copy: {int(time_mode.isna().sum())}")
log(f"  shows without a valid date to copy: {int(date_mode.isna().sum())}")

# ---------------------------------------------------------------------------
# 6. Repair ratings and ages
# ---------------------------------------------------------------------------
valid_rating = df["rating"].between(0, 10)
bad_rating = ~valid_rating
rating_mode = (
    df.loc[valid_rating].groupby("movie_title")["rating"]
    .agg(lambda values: values.mode().iat[0])
)
df.loc[bad_rating, "rating"] = df.loc[bad_rating, "movie_title"].map(rating_mode)
df["rating"] = df["rating"].astype(float)

valid_age = df["age"].between(18, 68)
bad_age = ~valid_age
age_mode = (
    df.loc[valid_age].groupby("customer_id")["age"]
    .agg(lambda values: values.mode().iat[0])
)
df.loc[bad_age, "age"] = df.loc[bad_age, "customer_id"].map(age_mode)
fallback_age = int(df.loc[valid_age, "age"].median())
df["age"] = df["age"].fillna(fallback_age).round().astype("int64")

log("")
log("STEP 5 -- Repair ratings and ages")
log(f"  out-of-range ratings repaired: {int(bad_rating.sum())}")
log(f"  impossible ages repaired     : {int(bad_age.sum())}")
log(f"  age fallback (median) used   : {int((~valid_age & df['customer_id'].map(age_mode).isna()).sum())}")

# ---------------------------------------------------------------------------
# 7. Fill missing contact details
# ---------------------------------------------------------------------------
for column, placeholder in [
    ("customer_email", None),
    ("phone", "0000000000"),
]:
    missing = df[column].isna() | (df[column].astype("string").str.strip() == "")
    n_missing = int(missing.sum())

    # A customer's other bookings carry the same email/phone.
    fill_values = df.loc[~missing].groupby("customer_id")[column].first()
    df.loc[missing, column] = df.loc[missing, "customer_id"].map(fill_values)

    still_missing = df[column].isna() | (df[column].astype("string").str.strip() == "")
    n_unrecoverable = int(still_missing.sum())
    if n_unrecoverable:
        if column == "customer_email":
            df.loc[still_missing, column] = (
                df.loc[still_missing, "customer_id"].str.lower() + "@example.com"
            )
        else:
            df.loc[still_missing, column] = placeholder

    df[column] = df[column].astype("string").str.strip()
    log("")
    log(f"STEP 6 -- Fill missing {column}")
    log(f"  blanks found        : {n_missing}")
    log(f"  copied from customer: {n_missing - n_unrecoverable}")
    log(f"  placeholders used   : {n_unrecoverable}")

# ---------------------------------------------------------------------------
# 8. Re-derive age_group
# ---------------------------------------------------------------------------
def age_band(age: int) -> str:
    if age < 25:
        return "18-24"
    if age < 35:
        return "25-34"
    if age < 45:
        return "35-44"
    if age < 55:
        return "45-54"
    return "55+"


age_group_before = df["age_group"].copy()
df["age_group"] = df["age"].map(age_band)
age_group_conflicts = int(
    (age_group_before.notna() & (age_group_before != df["age_group"])).sum()
)

log("")
log("STEP 7 -- Re-derive age_group from age")
log(f"  blanks before        : {int(age_group_before.isna().sum())}")
log(f"  rows that disagreed  : {age_group_conflicts}")
log(f"  bands after          : {sorted(df['age_group'].unique())}")

# ---------------------------------------------------------------------------
# 9. Infer missing promo codes
# ---------------------------------------------------------------------------
blank_promo = df["promo_code"].isna() | (df["promo_code"].astype("string").str.strip() == "")
n_blank_promo = int(blank_promo.sum())

subtotal = (df["ticket_price"] * df["seats"]).replace(0, np.nan)
discount_rate = df["discount_amount"] / subtotal

inferred = []
unmatched = 0
for index in df.index[blank_promo]:
    if df.at[index, "discount_amount"] == 0:
        inferred.append("NONE")
        continue

    rate = discount_rate.at[index]
    if pd.isna(rate):
        inferred.append("NONE")
        unmatched += 1
        continue

    code = min(PROMO_RATES, key=lambda key: abs(PROMO_RATES[key] - rate))
    if abs(PROMO_RATES[code] - rate) > 0.01:
        code = "NONE"
        unmatched += 1
    inferred.append(code)

df.loc[blank_promo, "promo_code"] = inferred
df["promo_code"] = df["promo_code"].astype("string").str.strip()

log("")
log("STEP 8 -- Infer missing promo codes")
log(f"  blanks found       : {n_blank_promo}")
log(f"  matched to a rate  : {n_blank_promo - unmatched}")
log(f"  set to NONE        : {int((pd.Series(inferred) == 'NONE').sum())}")

# ---------------------------------------------------------------------------
# 10. Verify the revenue formula
# ---------------------------------------------------------------------------
expected_total = (
    df["ticket_price"] * df["seats"]
    + df["convenience_fee"]
    - df["discount_amount"]
)
formula_mismatch = expected_total != df["total_amount"]

log("")
log("STEP 9 -- Verify the revenue formula")
log(f"  rows failing: {int(formula_mismatch.sum())}")

if formula_mismatch.any():
    bad_ids = df.loc[formula_mismatch, "booking_id"].head(10).tolist()
    raise ValueError(
        f"Revenue formula still fails for {int(formula_mismatch.sum())} rows "
        f"(examples: {bad_ids}). Do not write the clean file."
    )

# ---------------------------------------------------------------------------
# 11. Derive customer_type and show_occupancy_rate
# ---------------------------------------------------------------------------
bookings_per_customer = df.groupby("customer_id").size()
customer_bookings = df["customer_id"].map(bookings_per_customer)
df["customer_type"] = np.select(
    [customer_bookings == 1, customer_bookings <= 3],
    ["New", "Returning"],
    default="Loyal",
)

confirmed = df[df["booking_status"] == "Confirmed"]
seats_sold = confirmed.groupby("show_id")["seats"].sum()
capacity = df.groupby("show_id")["seats_capacity"].first()
occupancy = seats_sold.reindex(capacity.index, fill_value=0) / capacity
df["show_occupancy_rate"] = df["show_id"].map(occupancy).round(6)

log("")
log("STEP 10 -- Derive reporting fields")
log(f"  customer_type counts : {df['customer_type'].value_counts().to_dict()}")
log(
    "  occupancy min/mean/max: "
    f"{occupancy.min():.3f} / {occupancy.mean():.3f} / {occupancy.max():.3f}"
)

# ---------------------------------------------------------------------------
# 12. Validation
# ---------------------------------------------------------------------------
required_columns = [
    "booking_id", "customer_id", "customer_name", "customer_email", "phone",
    "age", "age_group", "gender", "city", "theatre_name", "screen",
    "seats_capacity", "movie_title", "genre", "language", "rating", "format",
    "show_id", "show_date", "show_time", "ticket_type", "seats",
    "ticket_price", "convenience_fee", "promo_code", "discount_amount",
    "total_amount", "payment_method", "booking_channel", "booking_status",
    "booking_datetime", "customer_type", "show_occupancy_rate",
]

blank_total = 0
for column in required_columns:
    series = df[column]
    blanks = int(series.isna().sum())
    if str(series.dtype) in ("object", "string"):
        blanks += int((series.astype("string").str.strip() == "").sum())
    blank_total += blanks

show_groups = df.groupby("show_id")
show_conflicts = int(
    (
        show_groups[
            ["movie_title", "theatre_name", "screen", "seats_capacity",
             "show_date", "show_time"]
        ].nunique() > 1
    ).any(axis=1).sum()
)

customer_groups = df.groupby("customer_id")
customer_conflicts = int(
    (
        customer_groups[["customer_name", "gender", "city"]].nunique() > 1
    ).any(axis=1).sum()
)

show_datetime = pd.to_datetime(
    df["show_date"] + " " + df["show_time"], errors="coerce"
)
booking_datetime = pd.to_datetime(df["booking_datetime"], errors="coerce")
booked_after_show = int((booking_datetime > show_datetime).sum())

phone_valid = df["phone"].str.fullmatch(r"[6-9]\d{9}").fillna(False)
phone_invalid = int((~phone_valid).sum())

confirmed_revenue = int(
    df.loc[df["booking_status"] == "Confirmed", "total_amount"].sum()
)
confirmed_tickets = int(
    df.loc[df["booking_status"] == "Confirmed", "seats"].sum()
)

checks = [
    ("Rows = 10,000", len(df) == TARGET_ROWS, f"{len(df):,}"),
    ("Unique booking_id = 10,000", df["booking_id"].nunique() == TARGET_ROWS,
     f"{df['booking_id'].nunique():,}"),
    ("No blanks in required fields", blank_total == 0, f"{blank_total} blanks"),
    ("Revenue formula holds", int(formula_mismatch.sum()) == 0,
     f"{int(formula_mismatch.sum())} failures"),
    ("Ticket price > 0", int((df['ticket_price'] <= 0).sum()) == 0,
     f"min {int(df['ticket_price'].min())}"),
    ("Show time in valid slots", int((~df['show_time'].isin(VALID_TIMES)).sum()) == 0,
     f"{int((~df['show_time'].isin(VALID_TIMES)).sum())} invalid"),
    ("Show date inside window", int((~df['show_date_dt'].between(START, END)).sum()) == 0,
     f"{df['show_date'].min()} to {df['show_date'].max()}"),
    ("Rating 0-10", int((~df['rating'].between(0, 10)).sum()) == 0,
     f"{df['rating'].min():.1f} to {df['rating'].max():.1f}"),
    ("Age 18-68", int((~df['age'].between(18, 68)).sum()) == 0,
     f"{int(df['age'].min())} to {int(df['age'].max())}"),
    ("Exactly 8 canonical cities", set(df["city"]) == VALID_CITIES,
     f"{df['city'].nunique()} labels"),
    ("Show consistency", show_conflicts == 0, f"{show_conflicts} shows conflict"),
    ("Customer consistency", customer_conflicts == 0, f"{customer_conflicts} customers conflict"),
    ("Occupancy within 0-1", int((~df['show_occupancy_rate'].between(0, 1)).sum()) == 0,
     f"{df['show_occupancy_rate'].min():.3f} to {df['show_occupancy_rate'].max():.3f}"),
    ("Confirmed revenue = INR 10,787,567", confirmed_revenue == TARGET_REVENUE,
     f"{confirmed_revenue:,}"),
    ("No discount without a promo",
     int(((df['discount_amount'] > 0) & (df['promo_code'] == "NONE")).sum()) == 0,
     f"{int(((df['discount_amount'] > 0) & (df['promo_code'] == 'NONE')).sum())} rows"),
    ("Seats <= capacity", int((df['seats'] > df['seats_capacity']).sum()) == 0,
     f"{int((df['seats'] > df['seats_capacity']).sum())} rows"),
    ("Booking before show start", booked_after_show == 0, f"{booked_after_show} rows"),
    ("Phone is 10 digits starting 6-9", phone_invalid == 0, f"{phone_invalid} invalid"),
    ("Raw file untouched", sha256(RAW) == raw_hash_before, "SHA256 match"),
]

log("")
log("=" * 78)
log("VALIDATION")
log("=" * 78)
for name, passed, detail in checks:
    log(f"  [{'PASS' if passed else 'FAIL'}] {name:38s} {detail}")

failed = [name for name, passed, _ in checks if not passed]
if failed:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    LOG.write_text("\n".join(log_lines), encoding="utf-8")
    raise SystemExit(f"Cleaning failed {len(failed)} check(s): {failed}")

# ---------------------------------------------------------------------------
# 13. Write the clean file and the log
# ---------------------------------------------------------------------------
df = df.drop(columns=["show_date_dt"])

CLEAN.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(CLEAN, index=False, encoding="utf-8")

log("")
log("=" * 78)
log("SUMMARY")
log("=" * 78)
log(f"  rows written        : {len(df):,}")
log(f"  columns written     : {len(df.columns)}")
log(f"  confirmed bookings  : {int((df['booking_status'] == 'Confirmed').sum()):,}")
log(f"  confirmed tickets   : {confirmed_tickets:,}")
log(f"  confirmed revenue   : INR {confirmed_revenue:,}")
log(f"  cancellation rate   : {100 * (df['booking_status'] == 'Cancelled').mean():.2f}%")
log(f"  mean occupancy (per show): {occupancy.mean():.3f}")
log(f"  clean file          : {CLEAN}")
log(f"  raw SHA256 (unchanged): {sha256(RAW)}")

LOG.parent.mkdir(parents=True, exist_ok=True)
LOG.write_text("\n".join(log_lines) + "\n", encoding="utf-8")

print()
print(f"Wrote {len(df):,} rows x {len(df.columns)} columns to {CLEAN}")
print(f"Wrote cleaning log to {LOG}")
print("ALL CHECKS PASSED")
