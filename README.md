# Movie Ticket Booking Analytics Project

> ⚠️ **Status: work in progress.** Dataset v2 is generated, cleaned, loaded
> into Oracle, and analysed with 25 validated SQL queries. A verified snapshot
> and the current pipeline appear below. The full 12-section README rewrite
> happens in Phase 8, after the EDA and the Power BI report.

## Overview
End-to-end analytics project using Python, Pandas, Oracle SQL (26ai Free), and Power BI/Streamlit for analyzing movie ticket bookings for an Indian cinema chain.

## Tech Stack
- **Data Generation & Cleaning:** Python, Pandas, NumPy
- **Database:** Oracle Database 26ai Free (FREEPDB1)
- **SQL Analysis:** Oracle SQL (CTEs, Window Functions, RANK, LAG, PIVOT-style aggregations)
- **Visualization:** Streamlit + Plotly, Power BI (guide included)
- **Environment:** Python 3.13 venv

## Project Structure
```
movie-ticket-booking-analytics/
├── data/
│   ├── raw/bookings_raw.csv      # 10,300 rows (with injected defects)
│   ├── clean/bookings_clean.csv  # 10,000 clean rows
│   └── powerbi/                  # Regenerated from Oracle (git-ignored)
├── src/
│   ├── 00_generate_data.py       # Generate synthetic data (seed 42)
│   ├── 01_clean_data.py          # Cleaning + 19 validation checks
│   ├── 02_create_schema.py       # Drop & create the Oracle schema
│   ├── 03_oracle_load.py         # Load + 18 reconciliation checks
│   ├── 04_run_sql_queries.py     # Execute 25 queries, write results
│   └── 05_export_powerbi.py      # Export the star schema to CSV
├── sql/
│   ├── 01_schema.sql             # 7 tables, 4 views, 105 constraints
│   └── 03_analysis_queries.sql   # 25 business analysis queries
├── dashboard/app.py              # Streamlit fallback (4 tabs)
├── powerbi/                      # Build guide & DAX measures
├── notebooks/                    # Understanding & cleaning notebooks
└── reports/                      # Quality, load, SQL and cleaning evidence
```

## Setup Instructions

### 1. Environment Setup
```bash
# Create virtual environment (already done at D:\venvs\cinema)
D:\venvs\cinema\Scripts\activate
pip install -r requirements.txt
```

### 2. Oracle Database
Oracle 26ai Free is installed at `D:\app\admin\product\26ai\`
- Service: OracleServiceFREE (Running)
- Listener: port 1521
- PDB: FREEPDB1
- User: `cinema` (password is **not** stored here — see `.env`)

### 3. Run Pipeline

Run in this order. Each step refuses to continue if its validation fails.

```powershell
cd D:\chinmay\movie-ticket-booking-analytics
$env:PYTHONPATH = "D:\chinmay\movie-ticket-booking-analytics\src"

# 1. Generate the raw file (seed 42, reproducible)
D:\venvs\cinema\Scripts\python.exe src\00_generate_data.py

# 2. Clean it (writes data/clean/bookings_clean.csv + reports/cleaning_log.txt)
D:\venvs\cinema\Scripts\python.exe src\01_clean_data.py

# 3. Rebuild the Oracle schema (drops existing tables, creates 7 tables + 4 views)
D:\venvs\cinema\Scripts\python.exe src\02_create_schema.py

# 4. Load and reconcile to INR 10,787,567
D:\venvs\cinema\Scripts\python.exe src\03_oracle_load.py

# 5. Execute all 25 queries and write reports/sql_results.md
D:\venvs\cinema\Scripts\python.exe src\04_run_sql_queries.py

# 6. Export the star schema to data/powerbi/*.csv
D:\venvs\cinema\Scripts\python.exe src\05_export_powerbi.py
```

Step 3 **drops and recreates** the seven tables. It is the reset step; do not
run it casually once the database holds something you want to keep.

### 4. Run Dashboard
Easiest way (starts in background and opens the browser):
```powershell
cd D:\chinmay\movie-ticket-booking-analytics
.\run_dashboard.ps1
```
Stop it with `.\run_dashboard.ps1 -Stop`.

Manual way:
```powershell
cd D:\chinmay\movie-ticket-booking-analytics
$env:PYTHONPATH = "D:\chinmay\movie-ticket-booking-analytics\src"
D:\venvs\cinema\Scripts\streamlit.exe run dashboard/app.py
```
Access at http://127.0.0.1:8501

Logs are written to `reports\logs\streamlit.out.log` and `streamlit.err.log`.

## Dataset v2 Snapshot (verified)

These figures come from the executed understanding notebook and will be the
baseline for every later layer:

- **Unique bookings:** 10,000 (10,300 raw rows including 300 duplicates)
- **Confirmed revenue:** ₹10,787,567 · **Confirmed tickets:** 22,690
- **Average confirmed booking value:** ₹1,158.58
- **Cancellation rate:** 6.89%
- **Mean show occupancy:** 40.18% across 290 shows
- **Customers:** 3,480 · **Loyal segment:** 25.4% of customers, 53.3% of bookings
- **Network:** 8 cities · 16 multiplexes · 79 screens in the sample (80 designed) · 22 fictional movies

The same totals are reproduced by Pandas, by the Oracle load, by all 25 SQL
queries, and by the Streamlit dashboard. See `reports/oracle_load_report.md`
and `reports/sql_results.md`.

## Business Recommendations

Not written yet — deliberately. The SQL results are available in
`reports/sql_results.md`; recommendations will be derived from the EDA
(Phase 4) and then written up, not guessed in advance.

## Oracle SQL Highlights

- 7-table model at booking grain, with `DIM_MOVIE` and `DIM_THEATRE`
  snowflaked off `DIM_SHOW`
- 105 enabled constraints, including a CHECK that enforces
  `total_amount = ticket_price × seats + fee − discount`
- 4 views: show performance, booking detail, monthly revenue, movie performance
- Window functions (`RANK`, `LAG`, `SUM OVER`, `NTILE`, `CORR OVER`)
- CTEs for multi-step aggregations
- PIVOT-style `CASE` aggregation
- `EXPLAIN PLAN` example in `reports/sql_results.md`
- 25 queries, with 20 independent revenue slices all reconciling to
  ₹10,787,567
