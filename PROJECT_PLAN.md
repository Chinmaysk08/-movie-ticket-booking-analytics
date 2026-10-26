# PROJECT PLAN — Movie Ticket Booking Analytics

> Status: **Phase 3 complete — the cleaned dataset passes all 19 checks.
> Awaiting review before rebuilding the Oracle layer.**
> Last updated: 2026-10-26
> Owner: Chinmay
> Project path: `D:\chinmay\movie-ticket-booking-analytics`

---

## 1. Project Objectives

Build an end-to-end, reproducible analytics project on **synthetic** movie-ticket
booking data that demonstrates:

1. Data quality assessment and defensible cleaning with Pandas.
2. Exploratory analysis that answers real business questions.
3. Relational database design and analytical SQL (Oracle 26ai Free).
4. An interactive Power BI dashboard (with Streamlit as a runnable fallback).
5. Professional documentation and version control suitable for interviews.

**Explicit non-goal:** this project does **not** describe real customers, real
cinema sales, or measured market demand. Every result is labelled synthetic.

---

## 2. Status at a Glance

| Layer | Artifact | Dataset | State |
|---|---|---|---|
| Environment | Python 3.13.17 venv at `D:\venvs\cinema` | — | ✅ Working |
| Libraries | pandas 3.1.0, numpy 2.5.4, matplotlib, seaborn, jupyter, oracledb, streamlit, plotly | — | ✅ Installed |
| Database | Oracle 26ai Free, `FREEPDB1`, port 1521 | v1 | ⚠️ Running, but holds v1 data |
| Raw data | `data/raw/bookings_raw.csv` (10,300 × 31) | **v2** | ✅ Current |
| Generation | `src/00_generate_data.py` (seed 42) | **v2** | ✅ Runs |
| Data dictionary | `docs/data_dictionary.md` (31 columns + rules) | **v2** | ✅ Current |
| Understanding | `notebooks/01_data_understanding.ipynb` (21 code cells, 0 errors) | **v2** | ✅ Executed |
| Quality report | `reports/data_quality_report.md` (11 issues, 14 targets) | **v2** | ✅ Current |
| Clean data | `data/clean/bookings_clean.csv` (10,000 × 33) | **v2** | ✅ Current |
| Cleaning script | `src/01_clean_data.py` + `reports/cleaning_log.txt` | **v2** | ✅ 19/19 checks pass |
| Cleaning notebook | `notebooks/02_data_cleaning.ipynb` (18 code cells, 0 errors) | **v2** | ✅ Executed; matches script exactly |
| Oracle schema | `sql/01_schema.sql` | v1 | ❌ Stale — no theatre/capacity/ticket_type/rating |
| Oracle loader | `src/03_oracle_load.py` | v1 | ❌ Stale |
| Power BI export | `src/05_export_powerbi.py` → `data/powerbi/*.csv` | v1 | ❌ Stale |
| Dashboard | `dashboard/app.py`, `run_dashboard.ps1` | v1 | ⚠️ Runs, queries old schema |
| SQL analysis | `sql/03_analysis_queries.sql` (20 queries) | v1 | ⚠️ Written, not all validated against v2 |
| README | `README.md` | v1 | ⚠️ Marked outdated; full rewrite in Phase 8 |
| Notebooks | `01_data_understanding`, `02_data_cleaning` done; EDA pending | **v2** | ⚠️ EDA not started |
| Git | installed (2.56) | — | ⚠️ Installed; repo not initialised |
| Power BI Desktop | — | — | ❌ Blocked: not installed |

**Rule for this project:** a downstream artifact is only "done" when it has been
re-run against v2 and its totals reconcile to the numbers in section 3.

---

## 3. Dataset v2 — Verified Profile

Every number below is measured, not assumed. Source: executed
`notebooks/01_data_understanding.ipynb` and `reports/generation_summary.json`.

| Attribute | Value |
|---|---|
| Raw file | 10,300 rows × 31 columns |
| Unique bookings | **10,000** |
| Exact duplicate rows | **300** (2.91%) |
| Distinct customers | **3,480** |
| Distinct shows | **290** |
| Theatres / screens | **16** multiplexes / **80** screens (5 per multiplex) |
| Movies | **22** fictional titles (Hindi / Tamil / Telugu) |
| Cities | **8** |
| Show-date window | 2025-10-02 → 2026-09-27 (design window 2025-10-01 → 2026-09-30; raw includes 20 × 2027-12-31 defects) |
| Booking-timestamp window | 2025-09-02 → 2026-09-27 |
| Confirmed tickets (deduplicated) | **22,690** |
| Confirmed revenue (deduplicated) | **₹10,787,567** |
| Average confirmed booking value | **₹1,158.58** |
| Cancellation rate | **6.89%** (689 of 10,000) |
| Mean show occupancy (deduplicated) | **40.2%** (min 5.0%, max 91.5%) |
| Rows with at least one blank | 223 |

### 3.1 Segments (deduplicated)

| Segment | Rule | Customers | % of customers | Bookings | % of bookings |
|---|---|---:|---:|---:|---:|
| New | 1 booking | 1,090 | 31.3% | 1,090 | 10.9% |
| Returning | 2–3 bookings | 1,507 | 43.3% | 3,581 | 35.8% |
| Loyal | 4+ bookings | 883 | 25.4% | 5,329 | 53.3% |

### 3.2 Raw defects to be repaired in Phase 3

| # | Defect | Rows | Treatment |
|---|---|---:|---|
| 1 | Duplicate `booking_id` | 300 | Drop duplicates, keep first |
| 2 | Missing `customer_email` | 62 | Copy from same customer; else placeholder |
| 3 | Missing `phone` | 61 | Copy from same customer; else placeholder |
| 4 | Missing `age_group` | 51 | Re-derive from `age` |
| 5 | Missing `promo_code` | 50 | Infer from discount rate; else `NONE` |
| 6 | `ticket_price` ≤ 0 | 52 | Recover from `total_amount` formula |
| 7 | Invalid `show_time` | 31 | Modal time for same `show_id` |
| 8 | `show_date` outside period | 20 | Modal date for same `show_id` |
| 9 | `rating` outside 0–10 | 10 | Modal rating for same movie |
| 10 | `age` outside 18–68 | 10 | Customer's age from another booking |
| 11 | City label variants | 242 | Strip, title-case, map to 8 canonical cities |

Full evidence, examples and validation criteria:
`reports/data_quality_report.md`.

---

## 4. Data Model

### 4.1 Grain and definitions

| Term | Definition | Calculation |
|---|---|---|
| Booking | One transaction / one row | `COUNT(*)` |
| Ticket | One seat sold | `SUM(seats)` |
| Revenue | Money collected | `SUM(total_amount)` where `booking_status = 'Confirmed'` |
| Customer | One person | `COUNT(DISTINCT customer_id)` |
| Show | One movie at one screen, date and time | `COUNT(DISTINCT show_id)` |
| Occupancy | Share of a show's seats sold | confirmed seats ÷ `seats_capacity` |

Cancelled bookings keep their row but are **excluded from revenue and
occupancy**, because the seats were released.

### 4.2 Raw schema (31 columns)

The full column-by-column dictionary, allowed values and business rules live in
`docs/data_dictionary.md`. Summary by group:

| Group | Columns |
|---|---|
| Booking | `booking_id`, `booking_datetime`, `booking_status`, `booking_channel` |
| Customer | `customer_id`, `customer_name`, `customer_email`, `phone`, `age`, `age_group`, `gender`, `city` |
| Venue | `theatre_name`, `screen`, `seats_capacity`, `format` |
| Show | `show_id`, `show_date`, `show_time`, `movie_title`, `genre`, `language`, `rating` |
| Commercial | `ticket_type`, `seats`, `ticket_price`, `convenience_fee`, `promo_code`, `discount_amount`, `total_amount`, `payment_method` |

### 4.3 Derived fields (never stored raw)

| Field | Definition | Where |
|---|---|---|
| `show_occupancy_rate` | confirmed seats for the show ÷ `seats_capacity` | clean CSV, `DIM_SHOW` |
| `customer_type` | New = 1 booking, Returning = 2–3, Loyal = 4+ in the window | clean CSV, `DIM_CUSTOMER` |
| `is_weekend`, `month_name`, `quarter`, `year` | calendar attributes of `show_date` | `DIM_DATE` |

Design rule: store facts and denominators; **derive** ratios so they can never
disagree with their inputs.

### 4.4 What changed from v1

| # | v1 defect | v2 resolution | Status |
|---|---|---|---|
| D1 | `Bengaluru`/`Bangalore`/`Banglore` were three equally-weighted cities | One Bengaluru weight; variants exist only as quality defects to clean | ✅ Fixed |
| D2 | No `customer_id`; every booking had a unique customer | 3,480-customer pool, 1–17 bookings each | ✅ Fixed |
| D3 | No theatre name | 16 multiplexes, 2 per city | ✅ Fixed |
| D4 | No seat capacity | 80 screens, 100–340 seats, capacity stored per booking | ✅ Fixed |
| D5 | No `ticket_type` | Standard / Premium / Recliner | ✅ Fixed |
| D6 | No movie rating | One rating per movie, 0–10 | ✅ Fixed |
| D7 | `total_amount` not re-derived | Cleaning recomputes and asserts the formula | ⏳ Phase 3 |
| D8 | `age_group` could drift from `age` | Cleaning re-derives and asserts it | ⏳ Phase 3 |

v1 is preserved at `archive/v1_2026-10-26/` (raw/clean CSVs, Power BI CSVs,
scripts, SQL, dashboard) for comparison and rollback.

---

## 5. Recommended Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ 1. SOURCE (synthetic, reproducible)                         │
│    src/00_generate_data.py  ──seed 42──▶ data/raw/*.csv     │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. CLEANING LAYER (Pandas)                                  │
│    notebooks/02_data_cleaning.ipynb                         │
│    src/01_clean_data.py                                     │
│    ▶ data/clean/bookings_clean.csv                          │
│    ▶ reports/cleaning_log.txt                               │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. STORAGE LAYER (Oracle 26ai Free, star schema)            │
│    DIM_CUSTOMER / DIM_MOVIE / DIM_THEATRE / DIM_SHOW        │
│    DIM_DATE / DIM_PAYMENT / FACT_BOOKINGS                   │
│    sql/01_schema.sql + src/03_oracle_load.py                │
└───────────────┬──────────────────────────────┬──────────────┘
                ▼                              ▼
┌───────────────────────────┐   ┌─────────────────────────────┐
│ 4a. SQL ANALYTICS         │   │ 4b. PYTHON EDA              │
│ 20 queries, views         │   │ notebooks/03_eda.ipynb      │
│ sql/03_analysis_queries   │   │ reports/figures/*.png       │
└───────────────┬───────────┘   └──────────────┬──────────────┘
                └──────────────┬───────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. PRESENTATION LAYER                                       │
│    Power BI (.pbix)  ← primary, 4 pages                     │
│    Streamlit/Plotly  ← runnable fallback                    │
└─────────────────────────────────────────────────────────────┘
```

**Why this fits a beginner portfolio**

- Each layer has one job, so failures are easy to isolate.
- Pandas cleaning is inspectable in a notebook — interviewers can follow the
  reasoning, not just the result.
- A star schema shows dimensional-modelling literacy without over-normalising.
- Two dashboard options means there is always something demoable, even if
  Power BI is unavailable on the review machine.
- Everything is scripted and seeded, so results are reproducible — a common
  interview question.

**Database decision:** keep **Oracle 26ai Free** (already installed, verified).
It is less common than MySQL/PostgreSQL in junior portfolios, which is an
advantage if the star schema, CTEs, window functions and `MERGE` can be
explained. The README will state the choice and include a portability note.

---

## 6. Business Questions

| # | Question | Primary tool |
|---|---|---|
| BQ1 | What are total bookings, tickets, revenue and average booking value? | SQL + Python |
| BQ2 | Which movies earn the most revenue vs sell the most tickets? | SQL |
| BQ3 | Which genres and languages dominate demand? | SQL + Python |
| BQ4 | How does revenue vary by city, and is that driven by volume or price? | SQL |
| BQ5 | Which theatres and screens under/over-perform? | SQL |
| BQ6 | What is average occupancy, and which shows fill up? | SQL |
| BQ7 | Which show times are peak, and how large is the gap vs off-peak? | SQL |
| BQ8 | Weekend vs weekday: volume, value, occupancy? | SQL |
| BQ9 | How does revenue trend month over month? | SQL window |
| BQ10 | Which ticket type (Standard/Premium/Recliner) is most profitable? | SQL |
| BQ11 | Does a higher movie rating translate into more bookings? | Python |
| BQ12 | Which payment methods and channels are preferred? | SQL |
| BQ13 | Which channels have the highest cancellation rate? | SQL |
| BQ14 | Which promos generate revenue vs erode margin? | SQL |
| BQ15 | What is the age/gender profile of bookers? | Python |
| BQ16 | What share of customers are New / Returning / Loyal? | SQL |
| BQ17 | Do loyal customers spend more per booking? | SQL |
| BQ18 | Where is revenue concentrated (Pareto: top 20% movies/cities)? | SQL |
| BQ19 | Which city×genre combinations are under-served? | SQL |
| BQ20 | Can booking demand be predicted from show/movie/city features? | ML (optional) |

---

## 7. Implementation Phases

### Phase 0 — Prerequisites
- [x] Install **Git** for Windows (2.56.0)
- [ ] Install **Power BI Desktop** (Microsoft Store) — **blocked on user**
- [x] `pip install matplotlib seaborn jupyter openpyxl`
- [x] Confirm pandas 3.1.0 compatibility in the generator

### Phase 1 — Planning & documentation
- [x] Workspace audit
- [x] Gap analysis (v1 vs brief)
- [x] `PROJECT_PLAN.md` updated to v2
- [x] `docs/data_dictionary.md` (31 columns, rules, limitations)

### Phase 2 — Dataset v2 + data understanding
- [x] Fix D1 (single Bengaluru weight; variants injected only as defects)
- [x] Add `customer_id`, `theatre_name`, `seats_capacity`, `ticket_type`, `rating`, `show_id`
- [x] Archive v1 at `archive/v1_2026-10-26/`
- [x] `notebooks/01_data_understanding.ipynb` (21 code cells, 0 errors)
- [x] `reports/data_quality_report.md` (11 issues, treatment plan, 14 targets)

### Phase 3 — Cleaning
- [x] Rewrite `src/01_clean_data.py` for v2
- [x] Read `phone` as text, not float
- [x] Deduplicate, normalise cities, repair prices/times/dates/ratings/ages
- [x] Fill email/phone/age_group/promo from in-file evidence
- [x] Derive `age_group`, `customer_type`, `show_occupancy_rate`
- [x] `notebooks/02_data_cleaning.ipynb` with before/after for every repair
- [x] `data/clean/bookings_clean.csv` (10,000 × 33)
- [x] Assertions: 19/19 pass, revenue = ₹10,787,567
- [x] Raw file SHA256 unchanged

### Phase 4 — EDA
- [ ] `notebooks/03_exploratory_data_analysis.ipynb`
- [ ] 12–15 charts saved to `reports/figures/`
- [ ] `reports/eda_findings.md` — question → result → interpretation → next step

### Phase 5 — Oracle SQL
- [ ] Updated star schema: add `DIM_THEATRE`, `show_id`, capacity, ticket type, rating
- [ ] Reload + row-count and revenue reconciliation to ₹10,787,567
- [ ] 15+ queries (target 20), each executed and result captured
- [ ] 3–4 views; `EXPLAIN PLAN` example
- [ ] `reports/sql_results.md`

### Phase 6 — Power BI
- [ ] Install Desktop; import star-schema CSVs
- [ ] Relationships, DAX measures, 4 report pages
- [ ] Reconcile KPIs to Python/SQL
- [ ] `powerbi/build_guide.md` updated with actual screenshots
- [ ] Save `Movie_Booking_Analytics.pbix`

### Phase 7 — Optional ML
- [ ] Feasibility note: predict booking size or high/low occupancy
- [ ] Baseline vs alternative, time-based split, leakage check
- [ ] Proceed only if it adds signal beyond the descriptive analysis

### Phase 8 — Docs, Git, QA
- [ ] README with all 12 required sections (replace the current v1 draft)
- [ ] `requirements.txt` pinned and verified in a fresh venv
- [ ] `.gitignore` covers `.env`, logs, venv, notebooks checkpoints
- [ ] `git init`, structured commits (ask before any push)
- [ ] `reports/qa_checklist.md` with pass/fail evidence

---

## 8. Testing & Validation Strategy

| Test | Method | Pass criterion |
|---|---|---|
| Raw file untouched | SHA256 before/after pipeline | Hash unchanged |
| Row integrity | `COUNT(*)` raw vs clean vs fact | Clean = 10,000; fact = 10,000 |
| Duplicate removal | `COUNT(DISTINCT booking_id)` | Equals row count |
| Revenue formula | `price*seats+fee-discount == total_amount` | 100% of rows |
| Revenue reconciliation | Pandas sum vs Oracle sum (Confirmed) | ₹10,787,567 both |
| Occupancy bounds | confirmed seats ÷ capacity | 0 ≤ value ≤ 1 |
| Show consistency | one movie/theatre/screen/capacity/date/time per `show_id` | 0 conflicts |
| Customer consistency | one name/gender/city per `customer_id` | 0 conflicts |
| Category validity | Allowed-value sets | No unexpected values |
| SQL executability | Run every query | 0 ORA errors |
| Dashboard reconciliation | Streamlit KPI vs SQL | Exact match |
| Reproducibility | Re-run generator with seed 42 | Identical row count + totals |

---

## 9. Risks & Assumptions

| Risk | Mitigation |
|---|---|
| Synthetic data → insights are illustrative only | Label everywhere; no real-world claims |
| City shares are sampled from a prior and can reorder | Document that they are illustrative, not market estimates |
| Occupancy is measured on a ~96% sample of each show | Documented: 40.2% measured vs 40.9% designed |
| Stale v1 artifacts could be mistaken for current | Status table above; README banner; rebuild in dependency order |
| Oracle is unusual in junior portfolios | Explain choice; note ANSI-portable SQL |
| Power BI unavailable on review machine | Streamlit fallback + screenshots in README |
| pandas 3.x API changes | Pin versions; test scripts after install |
| Scope creep (ML, extra pages) | ML only after the core is signed off |
| Credentials in repo | `.env` git-ignored; `src/db.py` reads env only; no secrets in docs |

---

## 10. Completion Checklist

- [x] Dataset v2 generated, seeded, v1 archived
- [x] Data dictionary (31 columns + derived fields)
- [x] Data-understanding notebook executed with 0 errors
- [x] Data-quality report with evidence and validation targets
- [x] Cleaning notebook reproducible end-to-end
- [ ] EDA notebook with interpretations (no invented insights)
- [ ] Oracle schema + 10,000 rows + 15 validated queries
- [ ] Python/SQL revenue reconciliation passes
- [ ] Power BI `.pbix` with 4 pages, reconciled KPIs
- [ ] Streamlit dashboard matching the same KPIs
- [ ] README complete (12 sections)
- [ ] Git history with meaningful commits
- [ ] QA checklist all green, exceptions documented

---

## 11. Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-10-26 | Choose **Option A**: regenerate as dataset v2 | v1 could not support theatre, occupancy, ticket-type, rating or retention analysis |
| 2026-10-26 | Keep v1 under `archive/v1_2026-10-26/` | Preserve evidence; allow comparison |
| 2026-10-26 | Oracle 26ai Free as the database | Already installed and verified; stronger portfolio differentiator |
| 2026-10-26 | Power BI primary, Streamlit fallback | Power BI is the requested tool; Streamlit guarantees a runnable demo |
| 2026-10-26 | Repair defects instead of deleting rows | Every defect is recoverable from evidence in the file; deleting would lose real revenue and break the 10,000-row target |

---

## 12. Next Step

**Phase 3 is complete.** `data/clean/bookings_clean.csv` reconciles to
₹10,787,567 and passes all 19 checks.

**Next:** Phase 5 (Oracle) and Phase 4 (EDA). Recommended order: rebuild the
Oracle star schema first, because Power BI and the SQL portfolio depend on it;
the EDA notebook can then read either the clean CSV or the database.

**Open item for the user:** Power BI Desktop still needs to be installed from
the Microsoft Store (requires a signed-in account). Everything else can proceed
without it.
