# Project Progress Summary

> **Status:** All phases complete — generation, cleaning, EDA, Oracle SQL,
> Power BI, Streamlit, documentation and GitHub.
> Last updated: 2026-11-11

All data in this project is **synthetic**. Results demonstrate analytical
method, not real cinema performance. Four recent release names (KGF Chapter 2,
Pushpa 2, War 2, Animal) are used as recognisable labels only.

---

## 1. What the project does

Takes 10,300 messy synthetic booking rows, cleans them to 10,000 validated
bookings, loads them into a 7-table Oracle star schema, answers 25 business
questions in SQL, explores them in a notebook, and presents the results in a
4-page Power BI report with a Streamlit app as a runnable fallback.

The defining feature: **every headline number is reconciled across four
independent layers** — Pandas, Oracle, SQL and the dashboard all report
₹10,823,192. Nothing is hand-copied.

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

**Network:** 8 cities · 16 multiplexes · 76 screens in the sample · 26 movies ·
3,499 customers · 290 shows.

> 76 screens, not 80: the generator designs 16 × 5, but four screens have no
> sampled booking. This is a property of the sample, not a claim about those
> multiplexes.

**Recent releases:** KGF Chapter 2 (Kannada), Pushpa 2: The Rule (Telugu),
War 2 (Hindi) and Animal (Hindi). Kannada was added as a fourth language, and
movie selection now weights new releases more heavily in their opening weeks
(5× within 14 days, 3× within 45, 1.6× within 90). Without that, a film
released late in the year only had the few remaining show slots — KGF had 17
bookings before the fix and 325 after.

---

## 3. Phase status

### Complete — Phase 1: Environment

Python 3.13.17 venv at `D:\venvs\cinema` (pandas 3.1.0, numpy 2.5.4,
oracledb 26.0.1, streamlit 1.66.1, plotly 7.1.0). Git 2.56. Oracle 26ai Free
(`FREEPDB1`, port 1521).

### Complete — Phase 2: Generation and understanding

- `src/00_generate_data.py` — seeded generator (42), 10,300 × 31, 26 movies.
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
| Wrong ticket prices | 50 | Recomputed from the revenue formula |
| Malformed show times | 30 | Modal slot for the same show |
| Invalid dates | 20 | Modal date for the same show |
| Invalid ratings | 10 | Modal rating for the movie |
| Impossible ages | 10 | Customer's age from another booking |
| Missing emails / phones | 60 / 60 | Copied from the same customer |
| Missing age groups | 50 | Re-derived from age |
| Missing promos | 50 | 14 recovered, 36 set to `NONE` |
| City label variants | 273 | 34 variants → 8 cities |

Raw file SHA256 unchanged: `71c37b9b3527c002a6a47eba992b23af81c37c68b01a09199e8a97c62f027fa9`.

### Complete — Phase 4: EDA

`notebooks/03_exploratory_data_analysis.ipynb` with 17 figures in
`reports/figures/` and interpretations in `reports/eda_findings.md`.

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
₹10,823,192.**

### Complete — Phase 6: Presentation

- `powerbi/Movie_Booking_Analytics.pbix` — 4 pages, 5 reconciliation anchors.
- `src/05_export_powerbi.py` — 8 objects to `data/powerbi/*.csv`, re-read and
  verified against the generator's total.
- `dashboard/app.py` — Streamlit fallback, 4 tabs plus a
  **Recent Movies (last 30 days)** table and chart; filters reconcile
  (Mumbai = ₹2,035,068, matching SQL).
- `powerbi/build_guide.md` + `dax_measures.txt` — current anchors.

### Complete — Phase 8: Docs, QA, Git

README rewritten, `docs/QA_CHECKLIST.md` all green, MIT LICENSE, pushed to
`https://github.com/Chinmaysk08/-movie-ticket-booking-analytics`.

---

## 4. Headline numbers

| Metric | Value |
|---|---:|
| Bookings | 10,000 |
| Confirmed bookings | 9,331 |
| Confirmed tickets | 22,920 |
| **Confirmed revenue** | **₹10,823,192** |
| Average booking value | ₹1,159.92 |
| Cancellation rate | 6.69% |
| Mean show occupancy | 41.23% |
| Aggregate seat occupancy | 42.14% |
| Customers | 3,499 |

### Findings (synthetic)

- **IMAX = 47.5% of revenue** (₹5,142,788). 2D = 36.1%, 3D = 16.4%.
  *Caveat: the generator prices IMAX highest, so this is partly designed.*
- **Evening shows dominate:** 18:45 + 21:30 = 67.7% of revenue.
- **Cancellation is a channel problem:** Third-Party 12.66% vs Mobile App
  5.24%. Ahmedabad worst city at 7.94%.
- **Loyal = 24.6% of customers, 52.4% of bookings, ₹5,577,566.**
- **Recliner yields ₹816.84/ticket vs Standard ₹382.50.**
- **Rating does not predict demand:** r = −0.10 across 26 movies.
- **Mumbai leads revenue** (₹2,035,068) but is 4th on occupancy (41.01%).
- **Top 5 movies = 41.5% of revenue.** Mar 2026 peak ₹1,211,679; Sep 2026 low
  ₹541,724.
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

Open / optional:

| Item | Status |
|---|---|
| Phase 7 ML | Skipped deliberately — 290 shows and 26 movies give too little signal |
| Power BI page screenshots | Optional; add to `reports/figures/` |
| Larger show sample | Optional; would strengthen per-movie rankings |

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
├── notebooks\                      01 understanding, 02 cleaning, 03 EDA
├── dashboard\app.py                Streamlit fallback, 4 tabs
├── powerbi\                        .pbix, build guide, DAX measures
├── reports\                        quality, cleaning, load, SQL evidence
├── docs\                           data dictionary, QA checklist
├── PROJECT_PLAN.md                 phase status + decision log
└── README.md                       project overview and caveats
```

Credentials live in `.env`, which is git-ignored — never committed, never
hardcoded.

---

## 7. Remaining work

None required. Optional follow-ups are listed in section 5 and in
`PROJECT_PLAN.md` section 12.
