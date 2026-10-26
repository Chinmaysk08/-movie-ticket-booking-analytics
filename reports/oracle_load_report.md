# Oracle Load Report — dataset v2

Generated: 2026-10-26 16:05:21
Source: `data\clean\bookings_clean.csv`
Schema: `sql/01_schema.sql` (Oracle 26ai Free, FREEPDB1)

Every number below was read back from Oracle after the commit and compared
with the clean CSV. The loader would have stopped before writing this report
if any check failed.

## Row counts

| Table | Rows | Matches CSV |
|---|---:|---|
| `DIM_CUSTOMER` | 3,480 | ✅ |
| `DIM_MOVIE` | 22 | ✅ |
| `DIM_THEATRE` | 16 | ✅ |
| `DIM_DATE` | 365 | ✅ |
| `DIM_PAYMENT` | 18 | ✅ |
| `DIM_SHOW` | 290 | ✅ |
| `FACT_BOOKINGS` | 10,000 | ✅ |

## KPI reconciliation

| KPI | Pandas (clean CSV) | Oracle | Match |
|---|---:|---:|---|
| `bookings` | 10,000 | 10,000 | ✅ |
| `confirmed_bookings` | 9,311 | 9,311 | ✅ |
| `confirmed_tickets` | 22,690 | 22,690 | ✅ |
| `confirmed_revenue` | 10,787,567 | 10,787,567 | ✅ |
| `cancellation_rate_pct` | 6.89 | 6.89 | ✅ |
| `mean_occupancy_pct` | 40.18 | 40.18 | ✅ |

## Integrity checks

| Check | Expected | Actual | Result |
|---|---:|---:|---|
| Revenue formula failures | 0 | 0 | ✅ |
| Fact rows with a missing dimension | 0 | 0 | ✅ |
| Shows outside the date dimension | 0 | 0 | ✅ |
| Shows with seats above capacity | 0 | 0 | ✅ |
| Shows outside the design window | 0 | 0 | ✅ |

## Notes

- **79 screens, not 80.** The generator designs 16 multiplexes × 5 screens,
  but one screen (Screen 3 at Deccan Mall Cinemas - Baner) has no bookings
  in the 10,000-row sample. `DIM_THEATRE.screens_in_sample` records what the
  sample contains; it is not a claim about the multiplex's real layout.
- **18 payment combinations, not 20.** Kiosk does not appear with NetBanking
  or Wallet in this dataset.
- **365 calendar rows.** `DIM_DATE` covers the full design window
  (2025-10-01 → 2026-09-30), including days with no show, so time-series
  queries do not silently skip empty dates.
- **Cancelled bookings are retained.** They are excluded from revenue and
  occupancy by filtering `booking_status = 'Confirmed'`.
- **Occupancy is derived.** `V_SHOW_PERFORMANCE` computes confirmed seats ÷
  `seats_capacity`; the value is never stored, so it cannot drift.

## Reproduce

```powershell
$env:PYTHONPATH = "D:\chinmay\movie-ticket-booking-analytics\src"
D:\venvs\cinema\Scripts\python.exe src\02_create_schema.py
D:\venvs\cinema\Scripts\python.exe src\03_oracle_load.py
```
