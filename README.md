# Movie Ticket Booking Analytics Project

> ⚠️ **Status: work in progress.** Dataset v2 is generated and documented in
> `docs/data_dictionary.md`, `notebooks/01_data_understanding.ipynb` and
> `reports/data_quality_report.md`; a verified v2 snapshot appears below.
> The pipeline sections still describe the v1 scripts, which are being
> rewritten in Phase 3. The full 12-section README rewrite happens in Phase 8.

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
│   └── powerbi/                  # Star schema CSVs for Power BI
├── src/
│   ├── 00_generate_data.py       # Generate synthetic data
│   ├── 01_clean_data.py          # Data cleaning & standardization
│   ├── 03_oracle_load.py         # Load to Oracle star schema
│   └── 05_export_powerbi.py      # Export for Power BI
├── sql/
│   ├── 01_schema.sql             # Star schema DDL
│   └── 03_analysis_queries.sql   # 20 business analysis queries
├── dashboard/app.py              # Streamlit dashboard
├── powerbi/                      # Build guide & DAX measures
└── reports/                      # Cleaning log & findings
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
```bash
# Generate data
python src/00_generate_data.py

# Clean data
python src/01_clean_data.py

# Create schema in Oracle (run via Python or SQLcl)
python -c "..." # schema creation done

# Load to Oracle
$env:PYTHONPATH='src'
python src/03_oracle_load.py

# Export for Power BI
python src/05_export_powerbi.py
```

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
- **Mean show occupancy:** 40.2% across 290 shows
- **Customers:** 3,480 · **Loyal segment:** 25.4% of customers, 53.3% of bookings
- **Network:** 8 cities · 16 multiplexes · 80 screens · 22 fictional movies

## Business Recommendations

Not written yet — deliberately. Recommendations will be derived from the EDA
and SQL results in Phases 4–5, not guessed in advance.

## Oracle SQL Highlights
- Star schema with fact & dimension tables
- Window functions (RANK, LAG, SUM OVER)
- CTEs for complex aggregations
- PIVOT-style CASE aggregations
- Date/time functions (TO_CHAR, EXTRACT)
- NULL handling with NVL
