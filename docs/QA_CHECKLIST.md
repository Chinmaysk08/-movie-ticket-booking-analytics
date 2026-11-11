# QA Checklist

All checks for the Movie Ticket Booking Analytics project (Dataset v2). Run before pushing to GitHub or sharing.

## 1. Data Integrity
- [x] Raw file hash: `71c37b9b3527c002a6a47eba992b23af81c37c68b01a09199e8a97c62f027fa9`
- [x] Clean dataset: 10,000 × 33 rows
- [x] 19/19 cleaning checks pass
- [x] Duplicates removed (300 from 10,300)
- [x] All defects repaired from evidence (no row deletions)
- [x] Recent releases present: KGF Chapter 2 (325 bookings), Pushpa 2 (306), War 2 (422), Animal (292)

## 2. Oracle Database
- [x] 7 tables created (DIM_CUSTOMER, DIM_MOVIE, DIM_THEATRE, DIM_SHOW, DIM_DATE, DIM_PAYMENT, FACT_BOOKINGS)
- [x] 4 views created (V_SHOW_PERFORMANCE, V_BOOKING_DETAIL, V_MONTHLY_REVENUE, V_MOVIE_PERFORMANCE)
- [x] 105 constraints enabled
- [x] 18/18 load reconciliation checks pass
- [x] Confirmed revenue: ₹10,823,192
- [x] Revenue formula enforced by CHECK constraint
- [x] Occupancy derived (not stored)
- [x] `CK_MOVIE_LANG` accepts Hindi, Tamil, Telugu and Kannada

## 3. SQL Analysis
- [x] 25 queries execute without errors
- [x] 20 revenue slices reconcile to ₹10,823,192
- [x] CTEs, window functions (RANK, LAG, SUM OVER, NTILE, CORR) used
- [x] EXPLAIN PLAN documented
- [x] Results in `reports/sql_results.md`

## 4. Python & Notebooks
- [x] `01_data_understanding.ipynb` executed (0 errors)
- [x] `02_data_cleaning.ipynb` matches script output
- [x] `03_exploratory_data_analysis.ipynb` executed (0 errors)
- [x] 17 figures generated in `reports/figures/`

## 5. Dashboard
- [x] Streamlit app (`dashboard/app.py`) runs against v2 schema
- [x] Headless AppTest passes with 0 exceptions
- [x] Filters reconcile with SQL results
- [x] "Recent Movies (last 30 days)" view added to the Movies & Formats tab
- [x] Power BI `.pbix` created with 4 pages
- [x] All 5 anchors verified in Power BI

## 6. Documentation
- [x] `README.md` rewritten with current totals and caveats
- [x] `PROJECT_PLAN.md` tracks all phases
- [x] `docs/data_dictionary.md` complete
- [x] `powerbi/build_guide.md` and `dax_measures.txt` current
- [x] Reports generated (quality, load, SQL, cleaning, progress)

## 7. Git & Security
- [x] `.gitignore` excludes `.env`, `data/powerbi/`, `archive/`, `__pycache__/`
- [x] No credentials committed
- [x] `.env` only contains local DB credentials (git-ignored)
- [x] All commits are clean and descriptive
- [x] Published to GitHub, working tree clean

## Final Verification
- [x] Re-run pipeline end-to-end works
- [x] All numbers match across Pandas/Oracle/SQL/Dashboard
- [x] Synthetic data clearly labeled throughout
- [x] All insights include appropriate caveats

**Status:** ✅ Complete
