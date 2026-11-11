# SQL Analysis Results — dataset v2

Generated: 2026-11-11 14:11:38

| Item | Value |
|---|---|
| Database | Oracle 26ai Free, `FREEPDB1` |
| Query file | `sql/03_analysis_queries.sql` |
| Queries executed | 25 |
| Queries with errors | 0 |
| Revenue target | ₹10,823,192 |

> ⚠️ All data is **synthetic**. These results demonstrate analytical method,
> not real cinema performance.

## Revenue reconciliation

Every query below slices the confirmed population a different way. Each
slice must still add up to the same total — if one does not, the query has
a join or filter bug.

| Query | Slice | Rows | `revenue_inr` sum | Matches ₹10,823,192 |
|---|---|---:|---:|---|
| Q1 | Overall KPIs | 1 | 10,823,192 | ✅ |
| Q2 | Monthly revenue trend | 12 | 10,823,192 | ✅ |
| Q4 | City performance | 8 | 10,823,192 | ✅ |
| Q5 | Revenue by day of week | 7 | 10,823,192 | ✅ |
| Q6 | Show-time performance | 6 | 10,823,192 | ✅ |
| Q7 | Genre performance | 8 | 10,823,192 | ✅ |
| Q8 | Language distribution | 4 | 10,823,192 | ✅ |
| Q9 | Payment method split | 5 | 10,823,192 | ✅ |
| Q10 | Booking channel performance | 4 | 10,823,192 | ✅ |
| Q12 | Promo code effectiveness | 5 | 10,823,192 | ✅ |
| Q13 | Age-group analysis | 5 | 10,823,192 | ✅ |
| Q14 | Screen and format performance | 5 | 10,823,192 | ✅ |
| Q16 | Running monthly revenue (window function) | 12 | 10,823,192 | ✅ |
| Q17 | Month-over-month growth (LAG) | 12 | 10,823,192 | ✅ |
| Q18 | Weekend vs weekday | 2 | 10,823,192 | ✅ |
| Q21 | Customer segments (New / Returning / Loyal) | 3 | 10,823,192 | ✅ |
| Q22 | Theatre performance | 16 | 10,823,192 | ✅ |
| Q23 | Ticket-type profitability | 3 | 10,823,192 | ✅ |
| Q24 | Revenue concentration (Pareto) | 26 | 10,823,192 | ✅ |
| Q25 | Does a higher rating mean more bookings? | 26 | 10,823,192 | ✅ |

## Query plan example (Q4 — City performance)

`EXPLAIN PLAN` for the city-performance query. At 10,000 fact rows Oracle
chooses full table scans, which is correct when most of a small table is
needed; the foreign-key indexes matter as the fact table grows.

```text
Plan hash value: 3064611631

---------------------------------------------------------------------------------------------------
| Id  | Operation                 | Name          | Rows  | Bytes |TempSpc| Cost (%CPU)| Time     |
---------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT          |               |  5511K|   520M|       |   124K  (1)| 00:00:05 |
|   1 |  SORT ORDER BY            |               |  5511K|   520M|   574M|   124K  (1)| 00:00:05 |
|*  2 |   HASH JOIN               |               |  5511K|   520M|       |   125  (36)| 00:00:01 |
|   3 |    VIEW                   |               |  9391 |   275K|       |    43   (7)| 00:00:01 |
|   4 |     HASH GROUP BY         |               |  9391 |   871K|       |    43   (7)| 00:00:01 |
|*  5 |      HASH JOIN OUTER      |               |  9391 |   871K|       |    42   (5)| 00:00:01 |
|*  6 |       HASH JOIN           |               |   290 | 20010 |       |     6   (0)| 00:00:01 |
|   7 |        TABLE ACCESS FULL  | DIM_THEATRE   |    16 |   480 |       |     3   (0)| 00:00:01 |
|   8 |        TABLE ACCESS FULL  | DIM_SHOW      |   290 | 11310 |       |     3   (0)| 00:00:01 |
|   9 |       VIEW                |               |  9391 |   238K|       |    36   (6)| 00:00:01 |
|  10 |        HASH GROUP BY      |               |  9391 |   421K|       |    36   (6)| 00:00:01 |
|  11 |         TABLE ACCESS FULL | FACT_BOOKINGS |  9391 |   421K|       |    34   (0)| 00:00:01 |
|  12 |    VIEW                   |               |  9391 |   632K|       |    42   (5)| 00:00:01 |
|  13 |     HASH GROUP BY         |               |  9391 |   632K|       |    42   (5)| 00:00:01 |
|  14 |      VIEW                 | VW_DAG_0      |  9391 |   632K|       |    42   (5)| 00:00:01 |
|  15 |       HASH GROUP BY       |               |  9391 |  1293K|       |    42   (5)| 00:00:01 |
|* 16 |        HASH JOIN          |               |  9391 |  1293K|       |    41   (3)| 00:00:01 |
|* 17 |         HASH JOIN         |               |   290 | 16240 |       |     6   (0)| 00:00:01 |
|  18 |          TABLE ACCESS FULL| DIM_THEATRE   |    16 |   480 |       |     3   (0)| 00:00:01 |
|  19 |          TABLE ACCESS FULL| DIM_SHOW      |   290 |  7540 |       |     3   (0)| 00:00:01 |
|* 20 |         TABLE ACCESS FULL | FACT_BOOKINGS |  9391 |   779K|       |    34   (0)| 00:00:01 |
---------------------------------------------------------------------------------------------------

Predicate Information (identified by operation id):
---------------------------------------------------

   2 - access("CO"."CITY"="CF"."CITY")
   5 - access("F"."SHOW_KEY"(+)="S"."SHOW_KEY")
   6 - access("T"."THEATRE_KEY"="S"."THEATRE_KEY")
  16 - access("S"."SHOW_KEY"="F"."SHOW_KEY")
  17 - access("T"."THEATRE_KEY"="S"."THEATRE_KEY")
  20 - filter("TICKET_PRICE"*"SEATS"+"CONVENIENCE_FEE"-"DISCOUNT_AMOUNT">=0)

Note
-----
   - dynamic statistics used: dynamic sampling (level=2)
```


## Query results

### Q1 — Overall KPIs

*what are total bookings, tickets, revenue and average value?*

```sql
SELECT COUNT(*) AS total_bookings,
       SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END) AS confirmed_bookings,
       SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_bookings,
       SUM(CASE WHEN booking_status = 'Confirmed' THEN seats ELSE 0 END) AS confirmed_tickets,
       SUM(CASE WHEN booking_status = 'Confirmed' THEN total_amount ELSE 0 END) AS revenue_inr,
       ROUND(AVG(CASE WHEN booking_status = 'Confirmed' THEN total_amount END), 2) AS avg_booking_value_inr,
       ROUND(100 * SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancellation_rate_pct
FROM fact_bookings
```

| `total_bookings` | `confirmed_bookings` | `cancelled_bookings` | `confirmed_tickets` | `revenue_inr` | `avg_booking_value_inr` | `cancellation_rate_pct` |
|---|---|---|---|---|---|---|
| 10,000 | 9,331 | 669 | 22,920 | 10,823,192 | 1,159.92 | 6.69 |

*1 row(s).*

### Q2 — Monthly revenue trend

*how does revenue trend month over month (by show date)?*

```sql
SELECT TO_CHAR(d.full_date, 'YYYY-MM') AS month,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
FROM fact_bookings f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY TO_CHAR(d.full_date, 'YYYY-MM')
ORDER BY month
```

| `month` | `bookings` | `tickets` | `revenue_inr` |
|---|---|---|---|
| 2025-10 | 715 | 1,724 | 864,461 |
| 2025-11 | 927 | 2,081 | 1,030,699 |
| 2025-12 | 911 | 2,152 | 861,389 |
| 2026-01 | 852 | 1,980 | 975,948 |
| 2026-02 | 610 | 1,370 | 586,476 |
| 2026-03 | 1,029 | 2,298 | 1,211,679 |
| 2026-04 | 889 | 2,030 | 899,032 |
| 2026-05 | 836 | 1,952 | 852,693 |
| 2026-06 | 1,006 | 2,262 | 1,183,716 |
| 2026-07 | 844 | 1,928 | 925,404 |
| 2026-08 | 808 | 1,830 | 889,971 |
| 2026-09 | 573 | 1,313 | 541,724 |

*12 row(s).*

### Q3 — Top 10 movies by revenue

*which movies earn the most, and do they also sell the most tickets?*

```sql
SELECT m.movie_title,
       m.genre,
       m.language,
       m.rating,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END)
           / NULLIF(SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END), 0),
           2
       ) AS avg_price_per_ticket
FROM fact_bookings f
JOIN dim_show s    ON s.show_key = f.show_key
JOIN dim_movie m   ON m.movie_key = s.movie_key
GROUP BY m.movie_title, m.genre, m.language, m.rating
ORDER BY revenue_inr DESC
FETCH FIRST 10 ROWS ONLY
```

| `movie_title` | `genre` | `language` | `rating` | `bookings` | `tickets` | `revenue_inr` | `avg_price_per_ticket` |
|---|---|---|---|---|---|---|---|
| Mehfil | Romance | Hindi | 7.20 | 1,086 | 2,548 | 1,235,373 | 484.84 |
| Rangmanch | Drama | Hindi | 7.40 | 895 | 2,029 | 969,106 | 477.63 |
| Aakhri Raasta | Action | Hindi | 7.80 | 686 | 1,584 | 797,699 | 503.60 |
| Dilli Nights | Thriller | Hindi | 8.10 | 731 | 1,674 | 767,898 | 458.72 |
| Antariksh 2050 | Sci-Fi | Hindi | 7.50 | 632 | 1,392 | 722,931 | 519.35 |
| Chandni Chowk Express | Comedy | Hindi | 6.90 | 608 | 1,421 | 617,484 | 434.54 |
| War 2 | Action | Hindi | 8.20 | 451 | 1,029 | 593,081 | 576.37 |
| Kadal Nilavu | Romance | Tamil | 7.10 | 574 | 1,370 | 591,006 | 431.39 |
| KGF Chapter 2 | Action | Kannada | 8.40 | 347 | 771 | 420,538 | 545.44 |
| Iravu Payanam | Thriller | Tamil | 7.90 | 376 | 895 | 414,638 | 463.28 |

*10 row(s).*

### Q4 — City performance

*how does revenue vary by city, and is it volume or price?*

```sql
WITH city_facts AS (
    SELECT t.city,
           COUNT(*) AS bookings,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
           COUNT(DISTINCT f.show_key) AS shows
    FROM fact_bookings f
    JOIN dim_show s    ON s.show_key = f.show_key
    JOIN dim_theatre t ON t.theatre_key = s.theatre_key
    GROUP BY t.city
),
city_occupancy AS (
    SELECT city,
           ROUND(AVG(occupancy_rate) * 100, 2) AS avg_occupancy_pct
    FROM v_show_performance
    GROUP BY city
)
SELECT cf.city,
       cf.bookings,
       cf.tickets,
       cf.revenue_inr,
       ROUND(cf.revenue_inr / NULLIF(cf.shows, 0), 2) AS revenue_per_show,
       co.avg_occupancy_pct
FROM city_facts cf
JOIN city_occupancy co ON co.city = cf.city
ORDER BY cf.revenue_inr DESC
```

| `city` | `bookings` | `tickets` | `revenue_inr` | `revenue_per_show` | `avg_occupancy_pct` |
|---|---|---|---|---|---|
| Mumbai | 1,645 | 3,807 | 2,035,068 | 39,903.29 | 41.01 |
| Delhi | 1,608 | 3,738 | 1,850,424 | 37,763.76 | 39.62 |
| Hyderabad | 1,628 | 3,625 | 1,821,146 | 50,587.39 | 46.86 |
| Bengaluru | 1,376 | 3,085 | 1,421,750 | 34,676.83 | 38.11 |
| Chennai | 1,218 | 2,798 | 1,277,025 | 37,559.56 | 44.37 |
| Pune | 988 | 2,306 | 1,094,618 | 37,745.45 | 39.91 |
| Ahmedabad | 756 | 1,746 | 705,701 | 28,228.04 | 37.69 |
| Kolkata | 781 | 1,815 | 617,460 | 24,698.40 | 42.67 |

*8 row(s).*

### Q5 — Revenue by day of week

*which days of the week carry the most demand?*

```sql
SELECT d.day_name,
       d.day_of_week,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
FROM fact_bookings f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.day_name, d.day_of_week
ORDER BY d.day_of_week
```

| `day_name` | `day_of_week` | `bookings` | `tickets` | `revenue_inr` |
|---|---|---|---|---|
| Monday | 1 | 959 | 2,171 | 908,582 |
| Tuesday | 2 | 1,232 | 2,810 | 1,171,475 |
| Wednesday | 3 | 1,312 | 3,006 | 1,348,743 |
| Thursday | 4 | 1,440 | 3,296 | 1,567,473 |
| Friday | 5 | 1,702 | 3,977 | 2,060,831 |
| Saturday | 6 | 1,954 | 4,475 | 2,141,435 |
| Sunday | 7 | 1,401 | 3,185 | 1,624,653 |

*7 row(s).*

### Q6 — Show-time performance

*which slots are peak, and how large is the occupancy gap?*

```sql
WITH slot_facts AS (
    SELECT s.show_time,
           COUNT(*) AS bookings,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
    FROM fact_bookings f
    JOIN dim_show s ON s.show_key = f.show_key
    GROUP BY s.show_time
),
slot_occupancy AS (
    SELECT show_time,
           COUNT(*) AS shows,
           ROUND(AVG(occupancy_rate) * 100, 2) AS avg_occupancy_pct
    FROM v_show_performance
    GROUP BY show_time
)
SELECT sf.show_time,
       so.shows,
       sf.bookings,
       sf.tickets,
       sf.revenue_inr,
       so.avg_occupancy_pct
FROM slot_facts sf
JOIN slot_occupancy so ON so.show_time = sf.show_time
ORDER BY sf.show_time
```

| `show_time` | `shows` | `bookings` | `tickets` | `revenue_inr` | `avg_occupancy_pct` |
|---|---|---|---|---|---|
| 09:00 | 26 | 487 | 1,079 | 489,282 | 19.94 |
| 12:15 | 44 | 969 | 2,258 | 948,111 | 27.42 |
| 15:30 | 49 | 1,475 | 3,345 | 1,449,872 | 35.79 |
| 18:45 | 78 | 3,413 | 7,899 | 3,915,591 | 53.82 |
| 21:30 | 63 | 3,038 | 6,955 | 3,412,318 | 56.24 |
| 23:45 | 30 | 618 | 1,384 | 608,018 | 24.60 |

*6 row(s).*

### Q7 — Genre performance

*which genres dominate revenue and ticket sales?*

```sql
SELECT m.genre,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END)
           / NULLIF(SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END), 0),
           2
       ) AS avg_price_per_ticket
FROM fact_bookings f
JOIN dim_show s  ON s.show_key = f.show_key
JOIN dim_movie m ON m.movie_key = s.movie_key
GROUP BY m.genre
ORDER BY revenue_inr DESC
```

| `genre` | `bookings` | `tickets` | `revenue_inr` | `avg_price_per_ticket` |
|---|---|---|---|---|
| Action | 2,836 | 6,481 | 3,266,808 | 504.06 |
| Romance | 1,957 | 4,605 | 2,191,003 | 475.79 |
| Drama | 1,921 | 4,372 | 1,968,449 | 450.24 |
| Thriller | 1,124 | 2,609 | 1,196,516 | 458.61 |
| Comedy | 920 | 2,121 | 900,023 | 424.34 |
| Sci-Fi | 632 | 1,392 | 722,931 | 519.35 |
| Historical | 349 | 743 | 335,559 | 451.63 |
| Horror-Comedy | 261 | 597 | 241,903 | 405.20 |

*8 row(s).*

### Q8 — Language distribution

*how is demand split across Hindi, Tamil and Telugu films?*

```sql
SELECT m.language,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(100 * SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END)
             / SUM(SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END)) OVER (), 2)
           AS revenue_share_pct
FROM fact_bookings f
JOIN dim_show s  ON s.show_key = f.show_key
JOIN dim_movie m ON m.movie_key = s.movie_key
GROUP BY m.language
ORDER BY revenue_inr DESC
```

| `language` | `bookings` | `tickets` | `revenue_inr` | `revenue_share_pct` |
|---|---|---|---|---|
| Hindi | 5,708 | 13,097 | 6,312,742 | 58.33 |
| Tamil | 2,464 | 5,722 | 2,511,421 | 23.20 |
| Telugu | 1,481 | 3,330 | 1,578,491 | 14.58 |
| Kannada | 347 | 771 | 420,538 | 3.89 |

*4 row(s).*

### Q9 — Payment method split

*which payment methods do customers prefer?*

```sql
SELECT p.payment_method,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) AS pct_of_bookings
FROM fact_bookings f
JOIN dim_payment p ON p.payment_key = f.payment_key
GROUP BY p.payment_method
ORDER BY revenue_inr DESC
```

| `payment_method` | `bookings` | `revenue_inr` | `pct_of_bookings` |
|---|---|---|---|
| UPI | 4,307 | 4,714,215 | 43.07 |
| Credit Card | 2,263 | 2,451,679 | 22.63 |
| Debit Card | 1,668 | 1,833,988 | 16.68 |
| NetBanking | 914 | 960,521 | 9.14 |
| Wallet | 848 | 862,789 | 8.48 |

*5 row(s).*

### Q10 — Booking channel performance

*which channels bring revenue, and which cancel most?*

```sql
SELECT p.booking_channel,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       SUM(CASE WHEN f.booking_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_bookings,
       ROUND(100 * SUM(CASE WHEN f.booking_status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2)
           AS cancellation_rate_pct
FROM fact_bookings f
JOIN dim_payment p ON p.payment_key = f.payment_key
GROUP BY p.booking_channel
ORDER BY revenue_inr DESC
```

| `booking_channel` | `bookings` | `revenue_inr` | `cancelled_bookings` | `cancellation_rate_pct` |
|---|---|---|---|---|
| Mobile App | 4,466 | 4,872,737 | 234 | 5.24 |
| Website | 2,986 | 3,302,602 | 164 | 5.49 |
| Third-Party | 1,501 | 1,541,805 | 190 | 12.66 |
| Kiosk | 1,047 | 1,106,048 | 81 | 7.74 |

*4 row(s).*

### Q11 — Cancellation rate by city

*is cancellation a local problem or a network-wide one?*

```sql
SELECT t.city,
       COUNT(*) AS total_bookings,
       SUM(CASE WHEN f.booking_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
       ROUND(100 * SUM(CASE WHEN f.booking_status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2)
           AS cancellation_rate_pct
FROM fact_bookings f
JOIN dim_show s    ON s.show_key = f.show_key
JOIN dim_theatre t ON t.theatre_key = s.theatre_key
GROUP BY t.city
ORDER BY cancellation_rate_pct DESC
```

| `city` | `total_bookings` | `cancelled` | `cancellation_rate_pct` |
|---|---|---|---|
| Ahmedabad | 756 | 60 | 7.94 |
| Delhi | 1,608 | 115 | 7.15 |
| Pune | 988 | 66 | 6.68 |
| Hyderabad | 1,628 | 108 | 6.63 |
| Bengaluru | 1,376 | 91 | 6.61 |
| Mumbai | 1,645 | 107 | 6.50 |
| Chennai | 1,218 | 79 | 6.49 |
| Kolkata | 781 | 43 | 5.51 |

*8 row(s).*

### Q12 — Promo code effectiveness

*which promos generate revenue and how much margin do they cost?*

```sql
SELECT f.promo_code,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN 1 ELSE 0 END) AS confirmed_bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.discount_amount ELSE 0 END) AS discount_inr,
       ROUND(AVG(CASE WHEN f.booking_status = 'Confirmed' THEN f.discount_amount END), 2)
           AS avg_discount_inr,
       ROUND(100 * SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.discount_amount ELSE 0 END)
             / NULLIF(SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.ticket_price * f.seats ELSE 0 END), 0), 2)
           AS discount_pct_of_gross
FROM fact_bookings f
GROUP BY f.promo_code
ORDER BY revenue_inr DESC
```

| `promo_code` | `bookings` | `confirmed_bookings` | `revenue_inr` | `discount_inr` | `avg_discount_inr` | `discount_pct_of_gross` |
|---|---|---|---|---|---|---|
| NONE | 7,006 | 6,524 | 7,802,713 | 0 | 0 | 0 |
| WEEKEND10 | 982 | 920 | 1,018,808 | 109,905 | 119.46 | 10 |
| FIRSTBUY5 | 772 | 721 | 808,876 | 41,347 | 57.35 | 5 |
| STUDENT15 | 724 | 680 | 708,592 | 121,204 | 178.24 | 15 |
| FAMILY20 | 516 | 486 | 484,203 | 117,122 | 240.99 | 20 |

*5 row(s).*

### Q13 — Age-group analysis

*which age bands book and spend the most?*

```sql
SELECT c.age_group,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(AVG(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount END), 2)
           AS avg_booking_value_inr
FROM fact_bookings f
JOIN dim_customer c ON c.customer_key = f.customer_key
GROUP BY c.age_group
ORDER BY c.age_group
```

| `age_group` | `bookings` | `tickets` | `revenue_inr` | `avg_booking_value_inr` |
|---|---|---|---|---|
| 18-24 | 2,167 | 4,972 | 2,362,903 | 1,163.99 |
| 25-34 | 3,136 | 7,206 | 3,408,165 | 1,165.98 |
| 35-44 | 2,266 | 5,183 | 2,431,559 | 1,148.59 |
| 45-54 | 1,595 | 3,647 | 1,711,305 | 1,153.95 |
| 55+ | 836 | 1,912 | 909,260 | 1,168.71 |

*5 row(s).*

### Q14 — Screen and format performance

*do IMAX/3D screens earn more per booking than 2D screens?*

```sql
SELECT s.screen,
       s.format,
       COUNT(DISTINCT s.show_key) AS shows,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
FROM fact_bookings f
JOIN dim_show s ON s.show_key = f.show_key
GROUP BY s.screen, s.format
ORDER BY revenue_inr DESC
```

| `screen` | `format` | `shows` | `bookings` | `tickets` | `revenue_inr` |
|---|---|---|---|---|---|
| Screen 1 | IMAX | 54 | 3,389 | 7,697 | 5,142,788 |
| Screen 2 | 3D | 46 | 1,739 | 4,022 | 1,774,313 |
| Screen 3 | 2D | 68 | 2,070 | 4,742 | 1,677,644 |
| Screen 4 | 2D | 56 | 1,464 | 3,418 | 1,158,708 |
| Screen 5 | 2D | 66 | 1,338 | 3,041 | 1,069,739 |

*5 row(s).*

### Q15 — Top 3 movies per city (RANK)

*is the most popular movie different in each city?*

```sql
SELECT city, movie_title, bookings, revenue_inr, city_rank
FROM (
    SELECT t.city,
           m.movie_title,
           COUNT(*) AS bookings,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
           RANK() OVER (
               PARTITION BY t.city
               ORDER BY SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) DESC
           ) AS city_rank
    FROM fact_bookings f
    JOIN dim_show s    ON s.show_key = f.show_key
    JOIN dim_theatre t ON t.theatre_key = s.theatre_key
    JOIN dim_movie m   ON m.movie_key = s.movie_key
    GROUP BY t.city, m.movie_title
)
WHERE city_rank <= 3
ORDER BY city, city_rank
```

| `city` | `movie_title` | `bookings` | `revenue_inr` | `city_rank` |
|---|---|---|---|---|
| Ahmedabad | Aakhri Raasta | 149 | 183,969 | 1 |
| Ahmedabad | Mehfil | 202 | 156,502 | 2 |
| Ahmedabad | Rangmanch | 85 | 99,131 | 3 |
| Bengaluru | Antariksh 2050 | 170 | 204,044 | 1 |
| Bengaluru | Kadal Nilavu | 164 | 203,509 | 2 |
| Bengaluru | War 2 | 94 | 166,812 | 3 |
| Chennai | Kadal Nilavu | 261 | 272,307 | 1 |
| Chennai | Antariksh 2050 | 106 | 142,642 | 2 |
| Chennai | Aakhri Raasta | 85 | 132,923 | 3 |
| Delhi | Rangmanch | 242 | 351,828 | 1 |
| Delhi | War 2 | 150 | 227,117 | 2 |
| Delhi | Mehfil | 216 | 223,058 | 3 |
| Hyderabad | Vennela | 203 | 263,533 | 1 |
| Hyderabad | Mehfil | 185 | 247,291 | 2 |
| Hyderabad | KGF Chapter 2 | 185 | 244,265 | 3 |
| Kolkata | Rangmanch | 203 | 153,375 | 1 |
| Kolkata | Mehfil | 187 | 148,918 | 2 |
| Kolkata | War 2 | 93 | 80,747 | 3 |
| Mumbai | Mehfil | 194 | 284,711 | 1 |
| Mumbai | Dilli Nights | 212 | 276,631 | 2 |
| Mumbai | Aakhri Raasta | 181 | 241,349 | 3 |
| Pune | Rangmanch | 190 | 179,271 | 1 |
| Pune | Mehfil | 102 | 174,893 | 2 |
| Pune | Kanaka | 102 | 165,090 | 3 |

*24 row(s).*

### Q16 — Running monthly revenue (window function)

*what is cumulative revenue across the year?*

```sql
SELECT month,
       revenue_inr,
       SUM(revenue_inr) OVER (
           ORDER BY month ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
       ) AS running_total_inr
FROM (
    SELECT TO_CHAR(d.full_date, 'YYYY-MM') AS month,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
    FROM fact_bookings f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY TO_CHAR(d.full_date, 'YYYY-MM')
)
ORDER BY month
```

| `month` | `revenue_inr` | `running_total_inr` |
|---|---|---|
| 2025-10 | 864,461 | 864,461 |
| 2025-11 | 1,030,699 | 1,895,160 |
| 2025-12 | 861,389 | 2,756,549 |
| 2026-01 | 975,948 | 3,732,497 |
| 2026-02 | 586,476 | 4,318,973 |
| 2026-03 | 1,211,679 | 5,530,652 |
| 2026-04 | 899,032 | 6,429,684 |
| 2026-05 | 852,693 | 7,282,377 |
| 2026-06 | 1,183,716 | 8,466,093 |
| 2026-07 | 925,404 | 9,391,497 |
| 2026-08 | 889,971 | 10,281,468 |
| 2026-09 | 541,724 | 10,823,192 |

*12 row(s).*

### Q17 — Month-over-month growth (LAG)

*which months grew and which declined?*

```sql
SELECT month,
       revenue_inr,
       LAG(revenue_inr) OVER (ORDER BY month) AS prev_month_revenue,
       ROUND(
           (revenue_inr - LAG(revenue_inr) OVER (ORDER BY month))
           / NULLIF(LAG(revenue_inr) OVER (ORDER BY month), 0) * 100,
           2
       ) AS mom_growth_pct
FROM (
    SELECT TO_CHAR(d.full_date, 'YYYY-MM') AS month,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
    FROM fact_bookings f
    JOIN dim_date d ON d.date_key = f.date_key
    GROUP BY TO_CHAR(d.full_date, 'YYYY-MM')
)
ORDER BY month
```

| `month` | `revenue_inr` | `prev_month_revenue` | `mom_growth_pct` |
|---|---|---|---|
| 2025-10 | 864,461 | — | — |
| 2025-11 | 1,030,699 | 864,461 | 19.23 |
| 2025-12 | 861,389 | 1,030,699 | -16.43 |
| 2026-01 | 975,948 | 861,389 | 13.30 |
| 2026-02 | 586,476 | 975,948 | -39.91 |
| 2026-03 | 1,211,679 | 586,476 | 106.60 |
| 2026-04 | 899,032 | 1,211,679 | -25.80 |
| 2026-05 | 852,693 | 899,032 | -5.15 |
| 2026-06 | 1,183,716 | 852,693 | 38.82 |
| 2026-07 | 925,404 | 1,183,716 | -21.82 |
| 2026-08 | 889,971 | 925,404 | -3.83 |
| 2026-09 | 541,724 | 889,971 | -39.13 |

*12 row(s).*

### Q18 — Weekend vs weekday

*how much more do weekends deliver than weekdays?*

```sql
SELECT CASE WHEN d.is_weekend = 'Y' THEN 'Weekend' ELSE 'Weekday' END AS day_type,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(AVG(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount END), 2)
           AS avg_booking_value_inr
FROM fact_bookings f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.is_weekend
ORDER BY d.is_weekend DESC
```

| `day_type` | `bookings` | `tickets` | `revenue_inr` | `avg_booking_value_inr` |
|---|---|---|---|---|
| Weekend | 3,355 | 7,660 | 3,766,088 | 1,203.99 |
| Weekday | 6,645 | 15,260 | 7,057,104 | 1,137.69 |

*2 row(s).*

### Q19 — Customers with the highest spend (CTE)

*who are the most valuable customers?*

```sql
WITH customer_stats AS (
    SELECT c.customer_id,
           c.customer_name,
           c.city,
           c.customer_type,
           COUNT(*) AS bookings,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
    FROM fact_bookings f
    JOIN dim_customer c ON c.customer_key = f.customer_key
    GROUP BY c.customer_id, c.customer_name, c.city, c.customer_type
)
SELECT customer_id, customer_name, city, customer_type, bookings, tickets, revenue_inr
FROM customer_stats
ORDER BY revenue_inr DESC
FETCH FIRST 15 ROWS ONLY
```

| `customer_id` | `customer_name` | `city` | `customer_type` | `bookings` | `tickets` | `revenue_inr` |
|---|---|---|---|---|---|---|
| CUS02549 | Ananya George | Hyderabad | Loyal | 16 | 37 | 21,334 |
| CUS02942 | Nisha Negi | Chennai | Loyal | 17 | 49 | 20,669 |
| CUS03089 | Harsh D'Souza | Chennai | Loyal | 17 | 45 | 19,163 |
| CUS03400 | Neel Nair | Pune | Loyal | 14 | 41 | 18,948 |
| CUS02727 | Meera Nambiar | Hyderabad | Loyal | 12 | 34 | 18,257 |
| CUS00868 | Aarav Shinde | Delhi | Loyal | 15 | 38 | 18,122 |
| CUS00410 | Sai Mehta | Mumbai | Loyal | 11 | 30 | 17,585 |
| CUS02458 | Sai Islam | Hyderabad | Loyal | 18 | 41 | 17,163 |
| CUS02393 | Nikhil Sharma | Hyderabad | Loyal | 12 | 33 | 16,934 |
| CUS03141 | Rohan Menon | Chennai | Loyal | 14 | 34 | 16,891 |
| CUS02637 | Vikram Iyer | Hyderabad | Loyal | 12 | 31 | 16,773 |
| CUS01217 | Om Sheikh | Delhi | Loyal | 13 | 35 | 16,528 |
| CUS02892 | Rajesh Arora | Chennai | Loyal | 13 | 34 | 16,338 |
| CUS02771 | Kabir Kulkarni | Chennai | Loyal | 14 | 30 | 15,974 |
| CUS02583 | Aadhya Thakur | Hyderabad | Loyal | 14 | 34 | 15,576 |

*15 row(s).*

### Q20 — Revenue by format (pivot-style aggregation)

*how much revenue comes from each screen format?*

```sql
SELECT SUM(CASE WHEN s.format = '2D'   AND f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_2d,
       SUM(CASE WHEN s.format = '3D'   AND f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_3d,
       SUM(CASE WHEN s.format = 'IMAX' AND f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_imax,
       COUNT(CASE WHEN s.format = '2D'   THEN 1 END) AS bookings_2d,
       COUNT(CASE WHEN s.format = '3D'   THEN 1 END) AS bookings_3d,
       COUNT(CASE WHEN s.format = 'IMAX' THEN 1 END) AS bookings_imax
FROM fact_bookings f
JOIN dim_show s ON s.show_key = f.show_key
```

| `revenue_2d` | `revenue_3d` | `revenue_imax` | `bookings_2d` | `bookings_3d` | `bookings_imax` |
|---|---|---|---|---|---|
| 3,906,091 | 1,774,313 | 5,142,788 | 4,872 | 1,739 | 3,389 |

*1 row(s).*

### Q21 — Customer segments (New / Returning / Loyal)

*how concentrated is demand in loyal customers?*

```sql
SELECT c.customer_type,
       COUNT(DISTINCT c.customer_id) AS customers,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END)
           / NULLIF(COUNT(DISTINCT c.customer_id), 0),
           2
       ) AS revenue_per_customer,
       ROUND(AVG(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount END), 2)
           AS avg_booking_value_inr
FROM fact_bookings f
JOIN dim_customer c ON c.customer_key = f.customer_key
GROUP BY c.customer_type
ORDER BY CASE c.customer_type WHEN 'New' THEN 1 WHEN 'Returning' THEN 2 ELSE 3 END
```

| `customer_type` | `customers` | `bookings` | `tickets` | `revenue_inr` | `revenue_per_customer` | `avg_booking_value_inr` |
|---|---|---|---|---|---|---|
| New | 1,112 | 1,112 | 2,552 | 1,250,205 | 1,124.29 | 1,216.15 |
| Returning | 1,527 | 3,653 | 8,460 | 3,995,421 | 2,616.52 | 1,164.85 |
| Loyal | 860 | 5,235 | 11,908 | 5,577,566 | 6,485.54 | 1,144.59 |

*3 row(s).*

### Q22 — Theatre performance

*which multiplexes under/over-perform?*

```sql
WITH theatre_facts AS (
    SELECT s.theatre_key,
           COUNT(*) AS bookings,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
    FROM fact_bookings f
    JOIN dim_show s ON s.show_key = f.show_key
    GROUP BY s.theatre_key
),
theatre_occupancy AS (
    SELECT theatre_name,
           COUNT(*) AS shows,
           ROUND(AVG(occupancy_rate) * 100, 2) AS avg_occupancy_pct
    FROM v_show_performance
    GROUP BY theatre_name
)
SELECT t.theatre_name,
       t.city,
       t.screens_in_sample,
       tocc.shows,
       tf.bookings,
       tf.tickets,
       tf.revenue_inr,
       tocc.avg_occupancy_pct
FROM theatre_facts tf
JOIN dim_theatre t        ON t.theatre_key = tf.theatre_key
JOIN theatre_occupancy tocc ON tocc.theatre_name = t.theatre_name
ORDER BY tf.revenue_inr DESC
```

| `theatre_name` | `city` | `screens_in_sample` | `shows` | `bookings` | `tickets` | `revenue_inr` | `avg_occupancy_pct` |
|---|---|---|---|---|---|---|---|
| Capital Screens - Saket | Delhi | 5 | 30 | 1,059 | 2,455 | 1,207,378 | 40.24 |
| Metro Cinema - Lower Parel | Mumbai | 5 | 29 | 919 | 2,142 | 1,157,133 | 40.76 |
| Deccan Talkies - Banjara Hills | Hyderabad | 5 | 20 | 901 | 1,956 | 928,925 | 49.71 |
| Nova Screens - Gachibowli | Hyderabad | 5 | 16 | 727 | 1,669 | 892,221 | 43.29 |
| Skyline Multiplex - Andheri | Mumbai | 5 | 22 | 726 | 1,665 | 877,935 | 41.34 |
| Orion Cinemas - Koramangala | Bengaluru | 5 | 22 | 779 | 1,751 | 788,432 | 41.24 |
| Anand Cinema - T. Nagar | Chennai | 5 | 20 | 688 | 1,564 | 695,799 | 43.32 |
| Regal Multiplex - Dwarka | Delhi | 5 | 19 | 549 | 1,283 | 643,046 | 38.64 |
| CineVerse - Whitefield | Bengaluru | 5 | 19 | 597 | 1,334 | 633,318 | 34.48 |
| Deccan Mall Cinemas - Baner | Pune | 5 | 15 | 518 | 1,179 | 595,533 | 38.22 |
| Marina Movies - Velachery | Chennai | 4 | 14 | 530 | 1,234 | 581,226 | 45.88 |
| Sunset Screens - Kothrud | Pune | 5 | 14 | 470 | 1,127 | 499,085 | 41.73 |
| Heritage Cinema - Navrangpura | Ahmedabad | 5 | 11 | 340 | 803 | 373,311 | 34.70 |
| Riverside Multiplex - Howrah | Kolkata | 3 | 11 | 428 | 984 | 345,910 | 51.08 |
| Sabarmati Screens - SG Highway | Ahmedabad | 4 | 14 | 416 | 943 | 332,390 | 40.03 |
| Bengal Cinema - Salt Lake | Kolkata | 5 | 14 | 353 | 831 | 271,550 | 36.07 |

*16 row(s).*

### Q23 — Ticket-type profitability

*which ticket class earns the most per seat?*

```sql
SELECT f.ticket_type,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END)
           / NULLIF(SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END), 0),
           2
       ) AS revenue_per_ticket,
       ROUND(AVG(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount END), 2)
           AS avg_booking_value_inr
FROM fact_bookings f
GROUP BY f.ticket_type
ORDER BY revenue_inr DESC
```

| `ticket_type` | `bookings` | `tickets` | `revenue_inr` | `revenue_per_ticket` | `avg_booking_value_inr` |
|---|---|---|---|---|---|
| Standard | 5,915 | 13,558 | 5,185,924 | 382.50 | 938.12 |
| Premium | 3,079 | 7,105 | 3,793,656 | 533.94 | 1,321.83 |
| Recliner | 1,006 | 2,257 | 1,843,612 | 816.84 | 1,976 |

*3 row(s).*

### Q24 — Revenue concentration (Pareto)

*what share of revenue comes from the top 20% of movies?*

```sql
WITH movie_revenue AS (
    SELECT m.movie_title,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
    FROM fact_bookings f
    JOIN dim_show s  ON s.show_key = f.show_key
    JOIN dim_movie m ON m.movie_key = s.movie_key
    GROUP BY m.movie_title
),
ranked AS (
    SELECT movie_title,
           revenue_inr,
           ROW_NUMBER() OVER (ORDER BY revenue_inr DESC) AS revenue_rank,
           SUM(revenue_inr) OVER (
               ORDER BY revenue_inr DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
           ) AS cumulative_revenue,
           SUM(revenue_inr) OVER () AS total_revenue,
           NTILE(5) OVER (ORDER BY revenue_inr DESC) AS revenue_quintile
    FROM movie_revenue
)
SELECT movie_title,
       revenue_inr,
       revenue_rank,
       ROUND(100 * revenue_inr / total_revenue, 2) AS revenue_share_pct,
       ROUND(100 * cumulative_revenue / total_revenue, 2) AS cumulative_share_pct,
       revenue_quintile
FROM ranked
ORDER BY revenue_rank
```

| `movie_title` | `revenue_inr` | `revenue_rank` | `revenue_share_pct` | `cumulative_share_pct` | `revenue_quintile` |
|---|---|---|---|---|---|
| Mehfil | 1,235,373 | 1 | 11.41 | 11.41 | 1 |
| Rangmanch | 969,106 | 2 | 8.95 | 20.37 | 1 |
| Aakhri Raasta | 797,699 | 3 | 7.37 | 27.74 | 1 |
| Dilli Nights | 767,898 | 4 | 7.09 | 34.83 | 1 |
| Antariksh 2050 | 722,931 | 5 | 6.68 | 41.51 | 1 |
| Chandni Chowk Express | 617,484 | 6 | 5.71 | 47.22 | 1 |
| War 2 | 593,081 | 7 | 5.48 | 52.70 | 2 |
| Kadal Nilavu | 591,006 | 8 | 5.46 | 58.16 | 2 |
| KGF Chapter 2 | 420,538 | 9 | 3.89 | 62.04 | 2 |
| Iravu Payanam | 414,638 | 10 | 3.83 | 65.87 | 2 |
| Vennela | 364,624 | 11 | 3.37 | 69.24 | 2 |
| Animal | 340,265 | 12 | 3.14 | 72.39 | 3 |
| Golconda | 335,559 | 13 | 3.10 | 75.49 | 3 |
| Kanaka | 330,576 | 14 | 3.05 | 78.54 | 3 |
| Pushpa 2: The Rule | 326,410 | 15 | 3.02 | 81.56 | 3 |
| Manikya | 311,209 | 16 | 2.88 | 84.43 | 3 |
| Sivappu Manjal | 252,286 | 17 | 2.33 | 86.76 | 4 |
| Neruppu | 249,477 | 18 | 2.31 | 89.07 | 4 |
| Pei Veedu | 241,903 | 19 | 2.24 | 91.30 | 4 |
| Thiruvizha | 219,477 | 20 | 2.03 | 93.33 | 4 |
| Vaanam | 212,058 | 21 | 1.96 | 95.29 | 4 |
| Raktham | 208,762 | 22 | 1.93 | 97.22 | 5 |
| Dhoop Chhaon | 205,843 | 23 | 1.90 | 99.12 | 5 |
| Shor Macha | 63,062 | 24 | 0.58 | 99.71 | 5 |
| Suryodayam | 17,947 | 25 | 0.17 | 99.87 | 5 |
| Bhramaram | 13,980 | 26 | 0.13 | 100 | 5 |

*26 row(s).*

### Q25 — Does a higher rating mean more bookings?

*is movie rating correlated with demand?*

```sql
WITH movie_stats AS (
    SELECT m.movie_title,
           m.rating,
           m.genre,
           m.language,
           COUNT(*) AS bookings,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
    FROM fact_bookings f
    JOIN dim_show s  ON s.show_key = f.show_key
    JOIN dim_movie m ON m.movie_key = s.movie_key
    GROUP BY m.movie_title, m.rating, m.genre, m.language
)
SELECT movie_title,
       rating,
       genre,
       language,
       bookings,
       tickets,
       revenue_inr,
       ROUND(CORR(rating, bookings) OVER (), 3) AS corr_rating_vs_bookings
FROM movie_stats
ORDER BY rating DESC, bookings DESC
```

| `movie_title` | `rating` | `genre` | `language` | `bookings` | `tickets` | `revenue_inr` | `corr_rating_vs_bookings` |
|---|---|---|---|---|---|---|---|
| Pushpa 2: The Rule | 8.60 | Action | Telugu | 326 | 766 | 326,410 | -0.10 |
| KGF Chapter 2 | 8.40 | Action | Kannada | 347 | 771 | 420,538 | -0.10 |
| Dhoop Chhaon | 8.40 | Drama | Hindi | 243 | 551 | 205,843 | -0.10 |
| Animal | 8.30 | Action | Hindi | 307 | 703 | 340,265 | -0.10 |
| Sivappu Manjal | 8.30 | Drama | Tamil | 247 | 543 | 252,286 | -0.10 |
| War 2 | 8.20 | Action | Hindi | 451 | 1,029 | 593,081 | -0.10 |
| Neruppu | 8.20 | Action | Tamil | 249 | 546 | 249,477 | -0.10 |
| Dilli Nights | 8.10 | Thriller | Hindi | 731 | 1,674 | 767,898 | -0.10 |
| Golconda | 8.10 | Historical | Telugu | 349 | 743 | 335,559 | -0.10 |
| Vaanam | 8 | Drama | Tamil | 229 | 556 | 212,058 | -0.10 |
| Raktham | 8 | Action | Telugu | 185 | 401 | 208,762 | -0.10 |
| Iravu Payanam | 7.90 | Thriller | Tamil | 376 | 895 | 414,638 | -0.10 |
| Aakhri Raasta | 7.80 | Action | Hindi | 686 | 1,584 | 797,699 | -0.10 |
| Suryodayam | 7.80 | Drama | Telugu | 26 | 51 | 17,947 | -0.10 |
| Bhramaram | 7.60 | Thriller | Telugu | 17 | 40 | 13,980 | -0.10 |
| Antariksh 2050 | 7.50 | Sci-Fi | Hindi | 632 | 1,392 | 722,931 | -0.10 |
| Rangmanch | 7.40 | Drama | Hindi | 895 | 2,029 | 969,106 | -0.10 |
| Vennela | 7.30 | Romance | Telugu | 297 | 687 | 364,624 | -0.10 |
| Mehfil | 7.20 | Romance | Hindi | 1,086 | 2,548 | 1,235,373 | -0.10 |
| Kanaka | 7.20 | Action | Tamil | 285 | 681 | 330,576 | -0.10 |
| Kadal Nilavu | 7.10 | Romance | Tamil | 574 | 1,370 | 591,006 | -0.10 |
| Manikya | 7 | Drama | Telugu | 281 | 642 | 311,209 | -0.10 |
| Thiruvizha | 7 | Comedy | Tamil | 243 | 534 | 219,477 | -0.10 |
| Chandni Chowk Express | 6.90 | Comedy | Hindi | 608 | 1,421 | 617,484 | -0.10 |
| Pei Veedu | 6.80 | Horror-Comedy | Tamil | 261 | 597 | 241,903 | -0.10 |
| Shor Macha | 6.50 | Comedy | Hindi | 69 | 166 | 63,062 | -0.10 |

*26 row(s).*

## Reproduce

```powershell
$env:PYTHONPATH = "D:\chinmay\movie-ticket-booking-analytics\src"
D:\venvs\cinema\Scripts\python.exe src\04_run_sql_queries.py
```

The runner stops before writing this file if any query errors or any
revenue slice fails to reconcile.
