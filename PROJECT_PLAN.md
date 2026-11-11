# PROJECT PLAN — Movie Ticket Booking Analytics

> Status: **Complete.** All phases delivered: dataset v2 (now with recent
> releases), 19/19 cleaning checks, Oracle star schema with 18/18 load checks,
> 25 SQL queries with every revenue slice reconciled to ₹10,823,192, EDA,
> Power BI report and Streamlit app. Published to GitHub.
> Last updated: 2026-11-11
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
| Database | Oracle 26ai Free, `FREEPDB1`, port 1521 | **v2** | ✅ Loaded and reconciled |
| Raw data | `data/raw/bookings_raw.csv` (10,300 × 31) | **v2** | ✅ Current |
| Generation | `src/00_generate_data.py` (seed 42, 26 movies) | **v2** | ✅ Runs |
| Data dictionary | `docs/data_dictionary.md` (31 columns + rules) | **v2** | ✅ Current |
| Understanding | `notebooks/01_data_understanding.ipynb` (21 code cells, 0 errors) | **v2** | ✅ Executed |
| Quality report | `reports/data_quality_report.md` (11 issues, 14 targets) | **v2** | ✅ Current |
| Clean data | `data/clean/bookings_clean.csv` (10,000 × 33) | **v2** | ✅ Current |
| Cleaning script | `src/01_clean_data.py` + `reports/cleaning_log.txt` | **v2** | ✅ 19/19 checks pass |
| Cleaning notebook | `notebooks/02_data_cleaning.ipynb` (18 code cells, 0 errors) | **v2** | ✅ Executed; matches script |
| Oracle schema | `sql/01_schema.sql` (7 tables, 4 views, 105 constraints) | **v2** | ✅ Built |
| Oracle runner/loader | `src/02_create_schema.py`, `src/03_oracle_load.py` | **v2** | ✅ 18/18 reconciliation checks |
| Power BI export | `src/05_export_powerbi.py` → `data/powerbi/*.csv` | **v2** | ✅ 8 objects, revenue matches |
| Dashboard | `dashboard/app.py`, `run_dashboard.ps1` | **v2** | ✅ 4 tabs + recent-release view |
| SQL analysis | `sql/03_analysis_queries.sql` (25 queries) | **v2** | ✅ All execute; 20 revenue slices reconcile |
| EDA | `notebooks/03_exploratory_data_analysis.ipynb`, 17 figures | **v2** | ✅ Executed |
| Power BI report | `powerbi/Movie_Booking_Analytics.pbix` (4 pages) | **v2** | ✅ Built |
| README | `README.md` | **v2** | ✅ Rewritten |
| Git | GitHub `Chinmaysk08/-movie-ticket-booking-analytics` | — | ✅ Pushed |

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
| Distinct customers | **3,499** |
| Distinct shows | **290** |
| Theatres / screens | **16** multiplexes / **80** screens designed, **76** in the sample |
| Movies | **26** titles (Hindi / Tamil / Telugu / Kannada), incl. recent releases |
| Cities | **8** |
| Show-date window | 2025-10-01 → 2026-09-29 (design window 2025-10-01 → 2026-09-30; raw includes 21 × 2027-12-31 defects) |
| Booking-timestamp window | 2025-09-02 → 2026-09-29 |
| Confirmed tickets (deduplicated) | **22,920** |
| Confirmed revenue (deduplicated) | **₹10,823,192** |
| Average confirmed booking value | **₹1,159.92** |
| Cancellation rate | **6.69%** (669 of 10,000) |
| Mean show occupancy (deduplicated) | **41.23%** (min 10.3%, max 90.7%) |
| Aggregate seat occupancy | **42.14%** |
| Rows with at least one blank | 223 |

### 3.1 Segments (deduplicated)

| Segment | Rule | Customers | % of customers | Bookings | % of bookings |
|---|---|---:|---:|---:|---:|
| New | 1 booking | 1,112 | 31.8% | 1,112 | 11.1% |
| Returning | 2–3 bookings | 1,527 | 43.6% | 3,653 | 36.5% |
| Loyal | 4+ bookings | 860 | 24.6% | 5,235 | 52.4% |

### 3.2 Raw defects to be repaired in Phase 3

| # | Defect | Rows | Treatment |
|---|---|---:|---|
| 1 | Duplicate `booking_id` | 300 | Drop duplicates, keep first |
| 2 | Missing `customer_email` | 62 | Copy from same customer; else placeholder |
| 3 | Missing `phone` | 60 | Copy from same customer; else placeholder |
| 4 | Missing `age_group` | 50 | Re-derive from `age` |
| 5 | Missing `promo_code` | 51 | Infer from discount rate; else `NONE` |
| 6 | `ticket_price` ≤ 0 | 51 | Recover from `total_amount` formula |
| 7 | Invalid `show_time` | 31 | Modal time for same `show_id` |
| 8 | `show_date` outside period | 21 | Modal date for same `show_id` |
| 9 | `rating` outside 0–10 | 10 | Modal rating for same movie |
| 10 | `age` outside 18–68 | 11 | Customer's age from another booking |
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
| D2 | No `customer_id`; every booking had a unique customer | 3,499-customer pool, 1–17 bookings each | ✅ Fixed |
| D3 | No theatre name | 16 multiplexes, 2 per city | ✅ Fixed |
| D4 | No seat capacity | 80 screens, 100–340 seats, capacity stored per booking | ✅ Fixed |
| D5 | No `ticket_type` | Standard / Premium / Recliner | ✅ Fixed |
| D6 | No movie rating | One rating per movie, 0–10 | ✅ Fixed |
| D7 | `total_amount` not re-derived | Cleaning recomputes and asserts the formula; Oracle enforces it with a CHECK constraint | ✅ Fixed |
| D8 | `age_group` could drift from `age` | Cleaning re-derives and asserts it | ✅ Fixed |

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
│ 3. STORAGE LAYER (Oracle 26ai Free, star + snowflaked dims)  │
│    DIM_CUSTOMER / DIM_MOVIE / DIM_THEATRE / DIM_SHOW        │
│    DIM_DATE / DIM_PAYMENT / FACT_BOOKINGS                   │
│    4 views: show, booking, monthly, movie performance       │
│    sql/01_schema.sql + src/03_oracle_load.py                │
└───────────────┬──────────────────────────────┬──────────────┘
                ▼                              ▼
┌───────────────────────────┐   ┌─────────────────────────────┐
│ 4a. SQL ANALYTICS         │   │ 4b. PYTHON EDA              │
│ 25 queries, 4 views       │   │ notebooks/03_eda.ipynb      │
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
- The model is a star at booking grain with two **snowflaked** dimensions:
  `DIM_MOVIE` and `DIM_THEATRE` hang off `DIM_SHOW`, because a movie and a
  theatre are attributes of a show, not of a booking. Calling that a "star"
  would be loose; the README says "star with snowflaked dimensions" and
  explains why.
- Two dashboard options means there is always something demoable, even if
  Power BI is unavailable on the review machine.
- Everything is scripted and seeded, so results are reproducible — a common
  interview question.

**Database decision:** keep **Oracle 26ai Free** (already installed, verified).
It is less common than MySQL/PostgreSQL in junior portfolios, which is an
advantage if the schema, CTEs, window functions and `MERGE` can be
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
- [x] Assertions: 19/19 pass, revenue = ₹10,823,192
- [x] Raw file SHA256 unchanged

### Phase 4 — EDA
- [x] `notebooks/03_exploratory_data_analysis.ipynb`
- [x] 17 charts saved to `reports/figures/`
- [x] `reports/eda_findings.md` — question → result → interpretation → next step

### Phase 5 — Oracle SQL
- [x] Updated schema: `DIM_THEATRE`, `show_id`, capacity, ticket type, rating, `customer_type`
- [x] Reload + 18 reconciliation checks; revenue = ₹10,823,192
- [x] 25 queries, each executed and result captured
- [x] 4 views; `EXPLAIN PLAN` example in `reports/sql_results.md`
- [x] `reports/sql_results.md` and `reports/oracle_load_report.md`
- [x] Streamlit fallback updated to the v2 views (headless test passes)

### Phase 6 — Power BI
- [x] Install Desktop; import star-schema CSVs
- [x] Relationships, DAX measures, 4 report pages
- [x] Reconcile KPIs to Python/SQL
- [x] `powerbi/build_guide.md` and `powerbi/dax_measures.txt`
- [x] Save `powerbi/Movie_Booking_Analytics.pbix`

### Phase 7 — Optional ML
- [x] Feasibility note: 290 shows and 26 movies give too little signal for a
  model that would beat the descriptive analysis; skipped deliberately

### Phase 8 — Docs, Git, QA
- [x] README rewritten with current totals and caveats
- [x] `requirements.txt` pinned
- [x] `.gitignore` covers `.env`, logs, venv, notebook checkpoints, Power BI CSVs
- [x] Structured commits; pushed to GitHub
- [x] `docs/QA_CHECKLIST.md` with pass/fail evidence

---

## 8. Testing & Validation Strategy

| Test | Method | Pass criterion |
|---|---|---|
| Raw file untouched | SHA256 before/after pipeline | Hash unchanged |
| Row integrity | `COUNT(*)` raw vs clean vs fact | Clean = 10,000; fact = 10,000 |
| Duplicate removal | `COUNT(DISTINCT booking_id)` | Equals row count |
| Revenue formula | `price*seats+fee-discount == total_amount` | 100% of rows |
| Revenue reconciliation | Pandas sum vs Oracle sum (Confirmed) | ₹10,823,192 both |
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
| Occupancy is measured on the bookings captured in the sample | Documented: 41.23% measured vs 42.14% aggregate |
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
- [x] EDA notebook with interpretations (no invented insights)
- [x] Oracle schema + 10,000 rows + 25 validated queries
- [x] Python/SQL revenue reconciliation passes
- [x] Power BI `.pbix` with 4 pages, reconciled KPIs
- [x] Streamlit dashboard matching the same KPIs
- [x] README complete
- [x] Git history with meaningful commits, pushed to GitHub
- [x] QA checklist all green, exceptions documented

---

## 11. Decision Log

| Date | Decision | Rationale |
|---|---|---|
| 2026-10-26 | Choose **Option A**: regenerate as dataset v2 | v1 could not support theatre, occupancy, ticket-type, rating or retention analysis |
| 2026-10-26 | Keep v1 under `archive/v1_2026-10-26/` | Preserve evidence; allow comparison |
| 2026-10-26 | Oracle 26ai Free as the database | Already installed and verified; stronger portfolio differentiator |
| 2026-10-26 | Power BI primary, Streamlit fallback | Power BI is the requested tool; Streamlit guarantees a runnable demo |
| 2026-10-26 | Repair defects instead of deleting rows | Every defect is recoverable from evidence in the file; deleting would lose real revenue and break the 10,000-row target |
| 2026-10-26 | `DIM_SHOW` stores capacity, not occupancy | Occupancy is derived by `V_SHOW_PERFORMANCE` as confirmed seats ÷ capacity, so the ratio can never drift from its inputs |
| 2026-10-26 | Snowflake `DIM_MOVIE` and `DIM_THEATRE` off `DIM_SHOW` | A movie and a theatre are attributes of a show; duplicating them on 10,000 fact rows would add no analytical value |
| 2026-10-26 | Revenue formula enforced by a CHECK constraint | A loader bug cannot silently produce a total that disagrees with price × seats + fee − discount |
| 2026-10-26 | 25 queries, each revenue slice reconciled to the pipeline total (currently ₹10,823,192) | A slice that does not add up to the total reveals a join or filter bug that a plausible-looking table would hide |
| 2026-11-11 | Add recent releases (KGF Chapter 2, Pushpa 2, War 2, Animal) and a fourth language (Kannada) | The dashboard should show recognisable current titles, not only invented ones |
| 2026-11-11 | Release-recency weighting in movie selection (5× / 3× / 1.6× by age of release) | Without it, a film released late in the year gets only the few remaining show slots and looks artificially unpopular (KGF had 17 bookings) |
| 2026-11-11 | Read the revenue target from `generation_summary.json` instead of hard-coding it | Adding movies changes the total; one source of truth prevents stale checks in four scripts |

---

## 12. Next Step

**The project is complete.** All layers reconcile to ₹10,823,192, 9,331 confirmed
bookings, 22,920 tickets and 41.23% mean occupancy, and the code is published at
`https://github.com/Chinmaysk08/-movie-ticket-booking-analytics`.

Optional follow-ups, if the dataset is extended again:

1. Increase `N_SHOWS` (currently 290) so per-movie and per-theatre rankings are
   statistically stronger.
2. Add screenshots of the four Power BI pages to `reports/figures/`.
3. Revisit Phase 7 (ML) only with a larger show sample.
