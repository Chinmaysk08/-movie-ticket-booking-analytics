# Power BI Dashboard Build Guide — dataset v2

> **Status:** the data model and measures are ready; the `.pbix` file is **not
> built yet** because Power BI Desktop is not installed on this machine.
> This guide is the exact sequence to follow once it is installed.
>
> All data is **synthetic**. The dashboard demonstrates analytical method, not
> real cinema performance.

---

## 0. Prerequisites

- Power BI Desktop (Microsoft Store, signed-in account required).
- The exported CSVs. Regenerate them from Oracle at any time:

```powershell
cd D:\chinmay\movie-ticket-booking-analytics
$env:PYTHONPATH = "D:\chinmay\movie-ticket-booking-analytics\src"
D:\venvs\cinema\Scripts\python.exe src\05_export_powerbi.py
```

Expected export (verified 2026-11-11):

| File | Rows |
|---|---:|
| `fact_bookings.csv` | 10,000 |
| `dim_customer.csv` | 3,499 |
| `dim_movie.csv` | 26 |
| `dim_theatre.csv` | 16 |
| `dim_show.csv` | 290 |
| `dim_date.csv` | 365 |
| `dim_payment.csv` | 18 |
| `v_show_performance.csv` | 290 (optional, for inspection) |

`data/powerbi/*.csv` is git-ignored: the files are rebuilt from Oracle, which
is the source of truth.

---

## 1. Import

1. Open Power BI Desktop.
2. **Home → Get data → Text/CSV**.
3. Import the seven model tables: `fact_bookings`, `dim_customer`,
   `dim_movie`, `dim_theatre`, `dim_show`, `dim_date`, `dim_payment`.
4. In **Transform Data**, confirm:
   - `dim_date[full_date]`, `dim_show[show_date]`, and
     `fact_bookings[booking_datetime]` are Date/Time types.
   - `dim_customer[phone]` is **Text**, not a number (leading zeros and exact
     digits matter).
   - `fact_bookings[booking_id]` is Text.
5. Close & Apply.

Do **not** import `v_show_performance` into the model: occupancy is computed by
a DAX measure from `fact_bookings` and `dim_show`, so importing the view as well
would create two competing sources of the same number.

---

## 2. Model relationships

This is a star schema with two snowflaked dimensions. Movie and theatre are
attributes of a **show**, so they hang off `dim_show` rather than sitting
directly on the fact table.

| From | To | Cardinality | Cross filter |
|---|---|---|---|
| `fact_bookings[customer_key]` | `dim_customer[customer_key]` | Many to one (*:1) | Single |
| `fact_bookings[show_key]` | `dim_show[show_key]` | Many to one (*:1) | Single |
| `fact_bookings[date_key]` | `dim_date[date_key]` | Many to one (*:1) | Single |
| `fact_bookings[payment_key]` | `dim_payment[payment_key]` | Many to one (*:1) | Single |
| `dim_show[movie_key]` | `dim_movie[movie_key]` | Many to one (*:1) | Single |
| `dim_show[theatre_key]` | `dim_theatre[theatre_key]` | Many to one (*:1) | Single |

Then:

- **Table view → dim_date → Mark as date table → `full_date`.**
- Hide the surrogate keys (`*_key`) from Report view.
- Sort `dim_date[month_name]` by `dim_date[month_number]`.
- Sort `dim_date[day_name]` by `dim_date[day_of_week]`.

---

## 3. Measures

Copy every measure from `powerbi/dax_measures.txt` into **Table view → New
measure**. Create a dedicated empty table called `_Measures` if you prefer to
keep them together.

The five reconciliation anchors are:

| Measure | Expected |
|---|---:|
| Total Revenue | ₹10,823,192 |
| Tickets Sold | 22,920 |
| Confirmed Bookings | 9,331 |
| Cancellation Rate % | 6.69 |
| Mean Show Occupancy % | 41.23 |

If any card disagrees, the relationship or the Confirmed filter is wrong.

---

## 4. Report pages

### Page 1 — Overview

- **Cards:** Total Revenue, Total Bookings, Tickets Sold, Average Booking
  Value, Cancellation Rate %, Mean Show Occupancy %.
- **Line chart:** Revenue by `dim_date[year]` + `month_name` (or a proper date
  axis on `full_date`).
- **Column chart:** Revenue by `dim_theatre[city]`.
- **Bar chart:** Top 10 movies by revenue (`dim_movie[movie_title]`).
- **Slicers:** City, Genre, Language, Format.

### Page 2 — Movies & Formats

- **Clustered bar:** Revenue by `dim_movie[genre]`.
- **Treemap:** Revenue by `dim_movie[language]`.
- **Column chart:** Revenue by `dim_show[format]` (2D / 3D / IMAX).
- **Scatter:** `dim_movie[rating]` vs Total Revenue, one point per movie.
  Add a trend line only if you also show the correlation (r = 0.04 in the SQL
  analysis), so the chart does not imply a relationship that is not there.
- **Table:** movie, rating, bookings, tickets, revenue, average ticket price.

### Page 3 — Customers

- **Cards:** Customers, Revenue per Customer, Loyal Revenue Share %.
- **Bar chart:** Revenue by `dim_customer[customer_type]`
  (New / Returning / Loyal).
- **Donut:** Bookings by `dim_customer[age_group]`.
- **Donut:** Bookings by `dim_payment[payment_method]`.
- **Column chart:** Revenue by `dim_payment[booking_channel]`.
- **Table:** segment, customers, bookings, revenue, revenue per customer.

### Page 4 — Operations

- **Column chart:** Mean Show Occupancy % by `dim_show[show_time]`.
- **Column chart:** Cancellation Rate % by `dim_payment[booking_channel]`.
- **Matrix:** `dim_theatre[theatre_name]` × measures (Shows, Tickets Sold,
  Revenue, Mean Show Occupancy %).
- **Bar chart:** Revenue and discount by `fact_bookings[promo_code]`.
- **Table:** ticket type, tickets, revenue, average ticket price.

---

## 5. Formatting

- Use a restrained cinema palette: deep red `#B3122F`, charcoal `#1F2933`,
  warm grey `#F5F1EA`, gold accent `#C9A227`.
- Currency format: `₹#,0` (Indian grouping is applied by the viewer's locale;
  Power BI stores the value, not the formatting).
- Percentages: one decimal place.
- Add a footer on every page: *"Synthetic data — analytical demonstration."*
- Add a tooltip page for show-level detail (movie, theatre, screen, occupancy).

---

## 6. Save and verify

1. Save as `powerbi/Movie_Booking_Analytics.pbix`.
2. Check the five anchors in section 3.
3. Check that the page-level totals still reconcile after each slicer:
   selecting a city must reduce revenue, but the **unfiltered** total must stay
   ₹10,823,192.
4. Take screenshots for the README (`reports/figures/powerbi_*.png`).
5. Only then commit the `.pbix` (it is a binary file; keep it under 25 MB).
