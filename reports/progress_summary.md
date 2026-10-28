# Project Progress Summary

> **Status:** Phases 1, 2, 3 and 5 complete. Phase 4 (EDA) next.
> Phase 6 (Power BI) blocked on Desktop installation.
> Last updated: 2026-10-26

All data in this project is **synthetic**. Results demonstrate analytical
method, not real cinema performance.

---

## 1. What the project does

Takes 10,300 messy synthetic booking rows, cleans them to 10,000 validated
bookings, loads them into a 7-table Oracle star schema, answers 25 business
questions in SQL, and presents the results in a Streamlit dashboard with a
Power BI build guide ready to use.

The defining feature: **every headline number is reconciled across four
independent layers** — Pandas, Oracle, SQL and the dashboard all report
₹10,787,567. Nothing is hand-copied.

---

## 2. Why there are two dataset versions

The original dataset (v1) could not answer the project's questions. It had no
theatre names, no seat capacity, no ticket type, no movie rating and no
customer ID — which made **occupancy impossible** (seats sold ÷ unknown
capacity) and customer retention unmeasurable.

v1 was archived at `archive/v1_2026-10-26/` (git-ignored, kept as evidence) and
v2 was generated with a fixed seed.

| | v1 | v2 |
|---|---|---|
| Columns | 18 | 31 raw → 33 clean |
| Theatre / capacity | No | Yes |
| Ticket type, rating | No | Yes |
| Customer ID, type | No | Yes |
| Occupancy possible | No | Yes |

**v2 composition:** 10,300 raw rows = 10,000 unique bookings + 300 exact
duplicates. Clean output: 10,000 × 33.

**Network:** 8 cities · 16 multiplexes · 79 screens · 22 fictional movies ·
3,480 customers · 290 shows.

> 79 screens, not 80: the generator designs 16 × 5, but Screen 3 at Deccan Mall
> Cinemas - Baner has no sampled booking. This is a property of the sample, not
> a claim about the multiplex.

---

## 3. Phase status

### Complete — Phase 1: Environment

Python 3.13.17 venv at `D:\venvs\cinema` (pandas 3.1.0, numpy 2.5.4,
oracledb 26.0.1, streamlit 1.66.1, plotly 7.1.0). Git 2.56. Oracle 26ai Free
(`FREEPDB1`, port 1521).

### Complete — Phase 2: Generation and understanding

- `src/00_generate_data.py` — seeded generator (42), 10,300 × 31.
- `docs/data_dictionary.md` — every column, type, valid range, business rule.
- `notebooks/01_data_understanding.ipynb` — 21 code cells, 0 errors.
- `reports/data_quality_report.md` — 11 issue categories, scorecard,
  treatment plan, 14 validation targets.

### Complete — Phase 3: Cleaning

`src/01_clean_data.py` + `notebooks/02_data_cleaning.ipynb` (18 cells,
0 errors). 19/19 checks pass; `assert_frame_equal` proves notebook and script
output are byte-identical.

Decision: **repair defects from evidence, never delete rows.** Every defect was
recoverable; deleting would have lost real revenue and broken the 10,000-row
target.

| Defect | Count | Treatment |
|---|---:|---|
| Wrong ticket prices | 50 | Recomputed from tier + format |
| Malformed show times | 30 | Snapped to valid slots |
| Invalid dates | 20 | Repaired into the design window |
| Missing ratings | 10 | Filled from movie master |
| Missing ages | 10 | Derived from age group |
| Bad emails / phones | 60 / 60 | Rebuilt to valid format |
| Wrong age groups | 50 | Re-derived from age |
| Invalid promos | 50 | 15 recovered, 35 set to `NONE` |
| City label variants | 232 | 34 variants → 8 cities |

Raw file SHA256 unchanged: `4130a03d818488c5b97ad8aa9016e4c345569e30a19e3204b54ad8f300186963`.

### Complete — Phase 5: Oracle SQL

**Schema:** 7 tables, 4 views, 105 constraints, 18 indexes.

Star at booking grain with two **snowflaked** dimensions: `DIM_MOVIE` and
`DIM_THEATRE` hang off `DIM_SHOW`, because a movie and a theatre are attributes
of a show, not a booking.

Two design points worth explaining:

1. **Occupancy is never stored.** `V_SHOW_PERFORMANCE` derives it as
   `confirmed_seats / seats_capacity`, so it cannot drift from its inputs.
2. **The revenue identity is enforced by the database:**
   `CHECK (total_amount = ticket_price * seats + convenience_fee - discount_amount)`.

**Load:** 18/18 reconciliation checks pass against the clean CSV.

**SQL:** 25 queries, all executed, results auto-written to
`reports/sql_results.md`. **20 independent revenue slices all sum to
₹10,787,567.**

### Partial — Phase 4b: Presentation

- `src/05_export_powerbi.py` — 8 objects to `data/powerbi/*.csv`, re-read and
  verified.
- `dashboard/app.py` — Streamlit fallback, 4 tabs, headless `AppTest` reports
  0 exceptions; filters reconcile (Mumbai = ₹2,587,211, matching SQL).
- `powerbi/build_guide.md` + `dax_measures.txt` — written for v2 with 5
  reconciliation anchors.

---

## 4. Headline numbers

| Metric | Value |
|---|---:|
| Bookings | 10,000 |
| Confirmed bookings | 9,311 |
| Confirmed tickets | 22,690 |
| **Confirmed revenue** | **₹10,787,567** |
| Average booking value | ₹1,158.58 |
| Cancellation rate | 6.89% |
| Mean show occupancy | 40.18% |
| Customers | 3,480 |

### Findings (synthetic)

- **IMAX = 48.9% of revenue** (₹5,276,756). 2D = 32.7%, 3D = 18.4%.
  *Caveat: the generator prices IMAX highest, so this is partly designed.*
- **Evening shows dominate:** 18:45 + 21:30 = 66.8% of revenue.
- **Cancellation is a channel problem:** Third-Party 12.76% vs Mobile App
  5.57%. Delhi worst city at 8.11%.
- **Loyal = 25.4% of customers, 53.3% of bookings, ₹5,677,151.**
- **Recliner yields ₹833/ticket vs Standard ₹387.**
- **Rating does not predict demand:** r = 0.04 across 22 movies.
- **Mumbai leads revenue** (₹2,587,211) but is 6th on occupancy (38.5%).
- **Top 5 movies = 52.16% of revenue.** May 2026 peak ₹1,591,552; Jan 2026 low
  ₹519,563.
- **Promos cost what they advertise:** FAMILY20 = 20% of gross,
  STUDENT15 = 15%.

**Performance note:** `EXPLAIN PLAN` shows full table scans, which is correct
at 10,000 rows. The 18 indexes exist for scale, not for this dataset.

---

## 5. Verified vs open

Verified across layers:

- 19/19 cleaning checks
- 18/18 Oracle load checks
- 25/25 SQL queries execute; 20/20 revenue slices reconcile
- Dashboard headless test: 0 exceptions
- Power BI export re-read and checked

Still open:

| Item | Status |
|---|---|
| Phase 4 EDA notebook + findings | Not started |
| Power BI `.pbix` | Blocked — Desktop not installed |
| Optional ML (Phase 7) | Deferred; only if genuinely valuable |
| README 12-section rewrite (Phase 8) | Partial |
| QA checklist | Not started |
| GitHub remote | Not created — needs user decision |

---

## 6. File map

```
movie-ticket-booking-analytics\
├── data\
│   ├── raw\bookings_raw.csv        10,300 × 31
│   ├── clean\bookings_clean.csv    10,000 × 33
│   └── powerbi\                    8 CSVs regenerated from Oracle
├── src\
│   ├── 00_generate_data.py         seeded generator
│   ├── 01_clean_data.py            19-check cleaning pipeline
│   ├── 02_create_schema.py         drop + rebuild (the reset step)
│   ├── 03_oracle_load.py           18-check loader
│   ├── 04_run_sql_queries.py       runs 25 queries, writes report
│   ├── 05_export_powerbi.py        exports + verifies
│   └── db.py                       connection helper (reads .env)
├── sql\
│   ├── 01_schema.sql               7 tables, 4 views, 105 constraints
│   └── 03_analysis_queries.sql     25 business queries
├── notebooks\                      01 understanding, 02 cleaning
├── dashboard\app.py                Streamlit fallback, 4 tabs
├── powerbi\                        build guide + DAX measures
├── reports\                        quality, cleaning, load, SQL evidence
├── docs\data_dictionary.md         column dictionary + limitations
├── PROJECT_PLAN.md                 phase status + decision log
└── README.md                       work-in-progress snapshot
```

Credentials live in `.env`, which is git-ignored — never committed, never
hardcoded.

---

## 7. Remaining work

1. **Phase 4 EDA** — `notebooks/03_exploratory_data_analysis.ipynb` and
   `reports/eda_findings.md`. Explains the patterns the SQL exposed rather than
   repeating the queries.
2. **Phase 6 Power BI** — once Desktop is installed. Guide is ready.
3. **Phase 7 ML** — optional, only if it adds real value.
4. **Phase 8** — full README, QA checklist, then GitHub (remote creation and
   push only after explicit approval).
