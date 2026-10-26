# Power BI Dashboard Build Guide - Movie Ticket Booking Analytics

## Prerequisites
- Power BI Desktop installed (download from Microsoft Store if not present)
- CSV files from `data/powerbi/` folder

## Step 1: Export Data for Power BI
Run this to create Power BI-ready CSVs:
```bash
cd D:\chinmay\movie-ticket-booking-analytics
D:\venvs\cinema\Scripts\python.exe src\05_export_powerbi.py
```

## Step 2: Import Data
1. Open Power BI Desktop
2. Home > Get data > Text/CSV
3. Import all files from `data/powerbi/`: fact_bookings.csv, dim_customer.csv, dim_movie.csv, dim_show.csv, dim_date.csv, dim_payment.csv

## Step 3: Model Relationships (Star Schema)
Go to Model View and create these relationships:
| From | To | Cardinality | Cross filter |
|------|----|-------------|--------------|
| fact_bookings[customer_key] | dim_customer[customer_key] | Many to one (*:1) | Single |
| fact_bookings[movie_key] | dim_movie[movie_key] | Many to one (*:1) | Single |
| fact_bookings[show_key] | dim_show[show_key] | Many to one (*:1) | Single |
| fact_bookings[date_key] | dim_date[date_key] | Many to one (*:1) | Single |
| fact_bookings[payment_key] | dim_payment[payment_key] | Many to one (*:1) | Single |

## Step 4: Create DAX Measures
Copy measures from `powerbi/dax_measures.txt` into Table view > New Measure

## Step 5: Build Report Pages

### Page 1: Overview
Add these visuals:
- **Card**: Total Revenue = CALCULATE(SUM(fact_bookings[total_amount]), fact_bookings[booking_status]="Confirmed")
- **Card**: Total Bookings
- **Card**: Tickets Sold (SUM of seats where Confirmed)
- **Card**: Cancellation % = DIVIDE(CALCULATE(COUNTROWS(fact_bookings), fact_bookings[booking_status]="Cancelled"), COUNTROWS(fact_bookings))*100
- **Line Chart**: Revenue by Month (use dim_date[month_name]+year)
- **Bar Chart**: Top 5 Movies by Revenue
- **Column Chart**: Revenue by City

### Page 2: Movie & Show Analysis
- **Clustered Bar**: Revenue by Genre
- **Clustered Column**: Revenue by Show Time
- **Treemap**: Revenue by Language
- **Stacked Column**: Revenue by Format (2D/3D/IMAX)
- **Table**: Movie performance details

### Page 3: Customer & Sales
- **Donut Chart**: Payment Method split
- **Donut Chart**: Booking Channel split
- **Clustered Bar**: Revenue by Age Group
- **Clustered Column**: Revenue by Day of Week
- **Gauge/Bar**: Cancellation rate by City

## Step 6: Add Slicers
Add slicers for: City, Genre, Language, Format, Year, Month, Booking Channel

## Step 7: Format & Publish
- Apply a cinema-themed color palette (Reds/Blues)
- Add page navigation
- Add tooltips
- Publish to Power BI Service (optional)
