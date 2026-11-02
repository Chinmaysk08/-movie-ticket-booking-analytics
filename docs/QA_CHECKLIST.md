# QA Checklist

All checks for the Movie Ticket Booking Analytics project (Dataset v2). Run before pushing to GitHub or sharing.

## 1. Data Integrity
- [x] Raw file hash unchanged: `4130a03d818488c5b97ad8aa9016e4c345569e30a19e3204b54ad8f300186963`
- [x] Clean dataset: 10,000 × 33 rows
- [x] 19/19 cleaning checks pass
- [x] Duplicates removed (300 from 10,300)
- [x] All defects repaired from evidence (no row deletions)

## 2. Oracle Database
- [x] 7 tables created (DIM_CUSTOMER, DIM_MOVIE, DIM_THEATRE, DIM_SHOW, DIM_DATE, DIM_PAYMENT, FACT_BOOKINGS)
- [x] 4 views created (V_SHOW_PERFORMANCE, V_BOOKING_DETAIL, V_MONTHLY_REVENUE, V_MOVIE_PERFORMANCE)
- [x] 105 constraints enabled
- [x] 18/18 load reconciliation checks pass
- [x] Confirmed revenue: ₹10,787,567
- [x] Revenue formula enforced by CHECK constraint
- [x] Occupancy derived (not stored)

## 3. SQL Analysis
- [x] 25 queries execute without errors
- [x] 20 revenue slices reconcile to ₹10,787,567
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
- [x] Power BI `.pbix` created (0.58 MB) with 4 pages
- [x] All 5 anchors verified in Power BI

## 6. Documentation
- [x] `README.md` updated with v2 info
- [x] `PROJECT_PLAN.md` tracks all phases
- [x] `docs/data_dictionary.md` complete
- [x] `powerbi/build_guide.md` and `dax_measures.txt` ready
- [x] Reports generated (quality, load, SQL, cleaning, progress)

## 7. Git & Security
- [x] `.gitignore` excludes `.env`, `data/powerbi/`, `archive/`, `__pycache__/`
- [x] No credentials committed
- [x] `.env` only contains local DB credentials (git-ignored)
- [x] All commits are clean and descriptive
- [x] 5 commits total, clean working tree

## Final Verification
- [x] Re-run pipeline end-to-end works
- [x] All numbers match across Pandas/Oracle/SQL/Dashboard
- [x] Synthetic data clearly labeled throughout
- [x] All insights include appropriate caveats

**Status:** ✅ Ready for GitHub push
