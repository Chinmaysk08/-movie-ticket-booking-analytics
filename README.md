# Movie Ticket Booking Analytics

> ✅ **Status: Complete.** End-to-end analytics project using Python/Pandas,
> Oracle SQL (26ai Free), Power BI and Streamlit. Every layer reconciles to the
> same totals: **₹10,823,192 confirmed revenue, 9,331 confirmed bookings,
> 22,920 tickets, 41.23% mean show occupancy.**
>
> ⚠️ **All data is synthetic.** Movie titles include real-world release names
> (KGF Chapter 2, Pushpa 2, War 2, Animal) purely as recognisable labels for a
> demonstration dataset. Every number — revenue, occupancy, customers, theatres
> — is simulated and says nothing about real box-office performance.

## Overview

A fictional Indian multiplex chain sells 10,000 bookings over one year
(Oct 2025 – Sep 2026). The project takes that raw, deliberately dirty file all
the way to a validated star schema, 25 analytical SQL queries, a Power BI
report and a Streamlit app — with the same numbers proving out at every step.

## Tech Stack

| Layer | Tools |
|---|---|
| Generation & cleaning | Python 3.13, Pandas, NumPy |
| Database | Oracle Database 26ai Free (FREEPDB1) |
| SQL analysis | Oracle SQL — CTEs, `RANK`, `LAG`, `SUM OVER`, `NTILE`, `CORR`, `PIVOT`-style `CASE` |
| BI | Power BI Desktop, Streamlit + Plotly |
| Tooling | `oracledb` (thin mode), Git |

## Verified Snapshot

These figures are produced by the pipeline and asserted in code, not copied by
hand. They are identical in Pandas, Oracle, all 25 SQL queries and the
dashboard.

| Metric | Value |
|---|---|
| Bookings (clean) | 10,000 (10,300 raw rows incl. 300 duplicates) |
| Confirmed bookings | 9,331 |
| Confirmed tickets | 22,920 |
| **Confirmed revenue** | **₹10,823,192** |
| Average confirmed booking value | ₹1,159.92 |
| Cancellation rate | 6.69% |
| Mean show occupancy | 41.23% (290 shows) |
| Aggregate seat occupancy | 42.14% |
| Customers | 3,499 (24.6% loyal → 52.4% of bookings) |
| Network | 8 cities · 16 multiplexes · 76 screens in sample · 26 movies |
| Top movie / city / language | Mehfil / Mumbai / Hindi |

## Project Structure

```
movie-ticket-booking-analytics/
├── data/
│   ├── raw/bookings_raw.csv      # 10,300 rows (10,000 + 300 injected duplicates)
│   ├── clean/bookings_clean.csv  # 10,000 rows × 33 columns
│   └── powerbi/                  # Star-schema extracts (git-ignored, rebuildable)
├── src/
│   ├── 00_generate_data.py       # Synthetic data, seed 42
│   ├── 01_clean_data.py          # Repairs + 19 validation checks
│   ├── 02_create_schema.py       # Drop & create the Oracle schema
│   ├── 03_oracle_load.py         # Load + 18 reconciliation checks
│   ├── 04_run_sql_queries.py     # 25 queries + revenue reconciliation
│   ├── 05_export_powerbi.py      # Export the star schema to CSV
│   └── db.py                     # Oracle connection helper
├── sql/
│   ├── 01_schema.sql             # 7 tables, 4 views, 105 constraints
│   └── 03_analysis_queries.sql   # 25 business queries
├── dashboard/app.py              # Streamlit app (4 tabs)
├── powerbi/                      # .pbix, build guide, DAX measures
├── notebooks/                    # Understanding, cleaning, EDA
├── reports/                      # Quality, load, SQL, cleaning evidence
└── docs/                         # Data dictionary, QA checklist
```

## Pipeline

Run in this order. Each step refuses to continue if its validation fails.

```powershell
cd D:\chinmay\movie-ticket-booking-analytics
$env:PYTHONPATH = "D:\chinmay\movie-ticket-booking-analytics\src"

D:\venvs\cinema\Scripts\python.exe src\00_generate_data.py    # raw + summary
D:\venvs\cinema\Scripts\python.exe src\01_clean_data.py       # clean + 19 checks
D:\venvs\cinema\Scripts\python.exe src\02_create_schema.py    # drops & recreates
D:\venvs\cinema\Scripts\python.exe src\03_oracle_load.py      # load + 18 checks
D:\venvs\cinema\Scripts\python.exe src\04_run_sql_queries.py  # 25 queries
D:\venvs\cinema\Scripts\python.exe src\05_export_powerbi.py   # CSV extracts
```

`02_create_schema.py` **drops and recreates** the seven tables. It is the reset
step — do not run it against a database holding anything you want to keep.

The expected revenue is read from `reports/generation_summary.json`, so the
generator is the single source of truth and no total is hard-coded twice.

### Setup

```bash
python -m venv D:\venvs\cinema
D:\venvs\cinema\Scripts\activate
pip install -r requirements-dev.txt   # runtime + notebook tooling
```

Use `requirements.txt` alone for just the pipeline and dashboard; it is the
file Streamlit Community Cloud installs.

Oracle 26ai Free runs on `localhost:1521/FREEPDB1`; credentials live in `.env`
(git-ignored, never committed).

### Dashboard

```powershell
cd D:\chinmay\movie-ticket-booking-analytics
.\run_dashboard.ps1          # start in background, opens browser
.\run_dashboard.ps1 -Stop    # stop
```

Manual start: `D:\venvs\cinema\Scripts\streamlit.exe run dashboard/app.py` →
http://127.0.0.1:8501

The dashboard reads Oracle when a `.env` is present and falls back to the
committed `data/clean/bookings_clean.csv` otherwise. Force the CSV path with
`DASHBOARD_DATA_SOURCE=csv`.

The **Movies & Formats** tab shows both all-time leaders and a
**Recent Movies (last 30 days)** table + chart, so late releases such as
KGF Chapter 2, Pushpa 2 and War 2 are visible on their own.

### Deploy to Streamlit Community Cloud

1. Push this repo to GitHub.
2. On [share.streamlit.io](https://share.streamlit.io), create an app from the
   repo and set **Main file path** to `dashboard/app.py`.
3. In **Advanced settings → Python version**, choose **3.12 or newer**
   (the pinned numpy requires ≥ 3.12). `runtime.txt` requests 3.12.
4. Leave secrets empty. The app detects that no Oracle `.env` is present and
   reads the committed CSV, so it needs no database or credentials.
5. `requirements.txt` pins the tested runtime versions; no other setup is
   required.

Because the data comes from a committed file, the deployed app is read-only
and always matches the reconciled totals in this README.

## Data Generation Design

Three choices make the data defensible rather than random-looking:

1. **Show-level simulation.** Occupancy is computed per show from the screen's
   real capacity, slot, weekend flag, format and month. It is never invented
   as a booking-level percentage.
2. **Stratified show allocation.** The 290 shows are spread across
   city × month cells, so seasonality and city weights survive instead of being
   drowned by sampling noise.
3. **Release-recency weighting.** A new release takes a larger share of screens
   in its opening weeks (5× within 14 days, 3× within 45, 1.6× within 90).
   Without this, a film released late in the year would only get the few
   remaining slots and look artificially unpopular.

### Recent releases

| Movie | Language | Released | Bookings |
|---|---|---|---|
| KGF Chapter 2 | Kannada | 2026-04-14 | 325 |
| Pushpa 2: The Rule | Telugu | 2026-05-01 | 306 |
| War 2 | Hindi | 2026-06-20 | 422 |
| Animal | Hindi | 2026-07-05 | 292 |

Kannada was added as a fourth language, weighted heavily in Bengaluru (0.30)
and lightly elsewhere, which is why KGF books mostly in one market.

## Deliberate Data-Quality Defects

The raw file is dirty on purpose, and every defect is recoverable from evidence
already in the file — no rows are deleted to make a check pass.

| Defect | Count | Repair evidence |
|---|---|---|
| Exact duplicate rows | 300 | `booking_id` |
| Missing email / phone | 60 / 60 | Same customer's other booking |
| Missing `age_group` | 50 | Re-derived from `age` |
| Missing `promo_code` | 50 | Discount rate identifies the promo |
| Impossible ticket price | 50 | `total_amount = price × seats + fee − discount` |
| Invalid show time | 30 | Mode for the same `show_id` |
| Future show date | 20 | Mode for the same `show_id` |
| Out-of-range rating | 10 | Mode for the same movie |
| Impossible age | 10 | Customer's age on another booking |

## Oracle Model

- 7 tables at booking grain; `DIM_MOVIE` and `DIM_THEATRE` snowflake off
  `DIM_SHOW`
- 105 enabled constraints, including a CHECK enforcing
  `total_amount = ticket_price × seats + fee − discount`
- 4 views: `V_SHOW_PERFORMANCE`, `V_BOOKING_DETAIL`, `V_MONTHLY_REVENUE`,
  `V_MOVIE_PERFORMANCE`
- Occupancy is derived from seats and capacity — never stored as an input
- 25 queries; **20 independent revenue slices all reconcile to ₹10,823,192**
  (`src/04_run_sql_queries.py` fails the run if any slice drifts)

## Evidence

| File | Contents |
|---|---|
| `reports/generation_summary.json` | Generator facts used as the source of truth |
| `reports/cleaning_log.txt` | Every repair + the 19-check table |
| `reports/data_quality_report.md` | Defect inventory and before/after effect |
| `reports/oracle_load_report.md` | 18 load reconciliation checks |
| `reports/sql_results.md` | Real output of all 25 queries + `EXPLAIN PLAN` |
| `reports/progress_summary.md` | Phase-by-phase status |
| `docs/data_dictionary.md` | Column definitions and derivations |
| `docs/QA_CHECKLIST.md` | Pre-release QA checklist |

## Caveats

- Synthetic data. Real movie titles are used as labels only.
- 290 shows is a small sample; per-movie and per-theatre rankings are
  directional, not statistically strong. This is why no ML phase was added.
- Occupancy is measured on the bookings captured in the sample, not on every
  seat sold at the multiplex.
- The "last 30 days" view ends 2026-09-29, the last date in the dataset — not
  today's date.

## License

MIT — see [LICENSE](LICENSE).
