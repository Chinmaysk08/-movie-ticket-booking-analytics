# SQL Analysis Results — dataset v2

Generated: 2026-10-26 16:05:25

| Item | Value |
|---|---|
| Database | Oracle 26ai Free, `FREEPDB1` |
| Query file | `sql/03_analysis_queries.sql` |
| Queries executed | 25 |
| Queries with errors | 0 |
| Revenue target | ₹10,787,567 |

> ⚠️ All data is **synthetic**. These results demonstrate analytical method,
> not real cinema performance.

## Revenue reconciliation

Every query below slices the confirmed population a different way. Each
slice must still add up to the same total — if one does not, the query has
a join or filter bug.

| Query | Slice | Rows | `revenue_inr` sum | Matches ₹10,787,567 |
|---|---|---:|---:|---|
| Q1 | Overall KPIs | 1 | 10,787,567 | ✅ |
| Q2 | Monthly revenue trend | 12 | 10,787,567 | ✅ |
| Q4 | City performance | 8 | 10,787,567 | ✅ |
| Q5 | Revenue by day of week | 7 | 10,787,567 | ✅ |
| Q6 | Show-time performance | 6 | 10,787,567 | ✅ |
| Q7 | Genre performance | 8 | 10,787,567 | ✅ |
| Q8 | Language distribution | 3 | 10,787,567 | ✅ |
| Q9 | Payment method split | 5 | 10,787,567 | ✅ |
| Q10 | Booking channel performance | 4 | 10,787,567 | ✅ |
| Q12 | Promo code effectiveness | 5 | 10,787,567 | ✅ |
| Q13 | Age-group analysis | 5 | 10,787,567 | ✅ |
| Q14 | Screen and format performance | 5 | 10,787,567 | ✅ |
| Q16 | Running monthly revenue (window function) | 12 | 10,787,567 | ✅ |
| Q17 | Month-over-month growth (LAG) | 12 | 10,787,567 | ✅ |
| Q18 | Weekend vs weekday | 2 | 10,787,567 | ✅ |
| Q21 | Customer segments (New / Returning / Loyal) | 3 | 10,787,567 | ✅ |
| Q22 | Theatre performance | 16 | 10,787,567 | ✅ |
| Q23 | Ticket-type profitability | 3 | 10,787,567 | ✅ |
| Q24 | Revenue concentration (Pareto) | 22 | 10,787,567 | ✅ |
| Q25 | Does a higher rating mean more bookings? | 22 | 10,787,567 | ✅ |

## Query plan example (Q4 — City performance)

`EXPLAIN PLAN` for the city-performance query. At 10,000 fact rows Oracle
chooses full table scans, which is correct when most of a small table is
needed; the foreign-key indexes matter as the fact table grows.

```text
Plan hash value: 3064611631

---------------------------------------------------------------------------------------------------
| Id  | Operation                 | Name          | Rows  | Bytes |TempSpc| Cost (%CPU)| Time     |
---------------------------------------------------------------------------------------------------
|   0 | SELECT STATEMENT          |               |  5712K|   539M|       |   128K  (1)| 00:00:06 |
|   1 |  SORT ORDER BY            |               |  5712K|   539M|   595M|   128K  (1)| 00:00:06 |
|*  2 |   HASH JOIN               |               |  5712K|   539M|       |   127  (38)| 00:00:01 |
|   3 |    VIEW                   |               |  9560 |   280K|       |    43   (7)| 00:00:01 |
|   4 |     HASH GROUP BY         |               |  9560 |   886K|       |    43   (7)| 00:00:01 |
|*  5 |      HASH JOIN OUTER      |               |  9560 |   886K|       |    42   (5)| 00:00:01 |
|*  6 |       HASH JOIN           |               |   290 | 20010 |       |     6   (0)| 00:00:01 |
|   7 |        TABLE ACCESS FULL  | DIM_THEATRE   |    16 |   480 |       |     3   (0)| 00:00:01 |
|   8 |        TABLE ACCESS FULL  | DIM_SHOW      |   290 | 11310 |       |     3   (0)| 00:00:01 |
|   9 |       VIEW                |               |  9560 |   242K|       |    36   (6)| 00:00:01 |
|  10 |        HASH GROUP BY      |               |  9560 |   429K|       |    36   (6)| 00:00:01 |
|  11 |         TABLE ACCESS FULL | FACT_BOOKINGS |  9560 |   429K|       |    34   (0)| 00:00:01 |
|  12 |    VIEW                   |               |  9560 |   644K|       |    42   (5)| 00:00:01 |
|  13 |     HASH GROUP BY         |               |  9560 |   644K|       |    42   (5)| 00:00:01 |
|  14 |      VIEW                 | VW_DAG_0      |  9560 |   644K|       |    42   (5)| 00:00:01 |
|  15 |       HASH GROUP BY       |               |  9560 |  1316K|       |    42   (5)| 00:00:01 |
|* 16 |        HASH JOIN          |               |  9560 |  1316K|       |    41   (3)| 00:00:01 |
|* 17 |         HASH JOIN         |               |   290 | 16240 |       |     6   (0)| 00:00:01 |
|  18 |          TABLE ACCESS FULL| DIM_THEATRE   |    16 |   480 |       |     3   (0)| 00:00:01 |
|  19 |          TABLE ACCESS FULL| DIM_SHOW      |   290 |  7540 |       |     3   (0)| 00:00:01 |
|* 20 |         TABLE ACCESS FULL | FACT_BOOKINGS |  9560 |   793K|       |    34   (0)| 00:00:01 |
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
| 10,000 | 9,311 | 689 | 22,690 | 10,787,567 | 1,158.58 | 6.89 |

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
| 2025-10 | 783 | 1,762 | 787,741 |
| 2025-11 | 905 | 2,046 | 1,056,911 |
| 2025-12 | 1,121 | 2,558 | 1,223,532 |
| 2026-01 | 568 | 1,276 | 519,563 |
| 2026-02 | 671 | 1,477 | 636,632 |
| 2026-03 | 737 | 1,661 | 720,504 |
| 2026-04 | 979 | 2,171 | 1,131,470 |
| 2026-05 | 1,264 | 2,901 | 1,591,552 |
| 2026-06 | 917 | 2,067 | 936,395 |
| 2026-07 | 555 | 1,299 | 580,324 |
| 2026-08 | 874 | 2,015 | 948,386 |
| 2026-09 | 626 | 1,457 | 654,557 |

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
| Dilli Nights | Thriller | Hindi | 8.10 | 1,640 | 3,724 | 1,841,194 | 494.41 |
| Chandni Chowk Express | Comedy | Hindi | 6.90 | 1,117 | 2,588 | 1,317,244 | 508.98 |
| Rangmanch | Drama | Hindi | 7.40 | 888 | 1,987 | 957,638 | 481.95 |
| Kanaka | Action | Tamil | 7.20 | 568 | 1,291 | 793,838 | 614.90 |
| Antariksh 2050 | Sci-Fi | Hindi | 7.50 | 666 | 1,507 | 717,072 | 475.83 |
| Aakhri Raasta | Action | Hindi | 7.80 | 644 | 1,442 | 618,015 | 428.58 |
| Raktham | Action | Telugu | 8 | 500 | 1,117 | 565,851 | 506.58 |
| Vaanam | Drama | Tamil | 8 | 539 | 1,198 | 552,561 | 461.24 |
| Pei Veedu | Horror-Comedy | Tamil | 6.80 | 427 | 983 | 437,916 | 445.49 |
| Mehfil | Romance | Hindi | 7.20 | 432 | 932 | 436,668 | 468.53 |

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
| Mumbai | 1,889 | 4,312 | 2,587,211 | 50,729.63 | 38.53 |
| Delhi | 1,665 | 3,632 | 1,754,679 | 35,809.78 | 40.57 |
| Chennai | 1,222 | 2,823 | 1,333,873 | 39,231.56 | 45.76 |
| Pune | 1,151 | 2,667 | 1,270,141 | 43,797.97 | 42.24 |
| Bengaluru | 1,162 | 2,685 | 1,225,897 | 29,899.93 | 35.09 |
| Hyderabad | 1,125 | 2,561 | 1,024,790 | 28,466.39 | 38.72 |
| Kolkata | 941 | 2,070 | 826,646 | 33,065.84 | 41.59 |
| Ahmedabad | 845 | 1,940 | 764,330 | 30,573.20 | 41.87 |

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
| Monday | 1 | 1,271 | 2,949 | 1,431,892 |
| Tuesday | 2 | 1,552 | 3,514 | 1,621,251 |
| Wednesday | 3 | 979 | 2,188 | 885,199 |
| Thursday | 4 | 1,291 | 2,906 | 1,300,983 |
| Friday | 5 | 1,599 | 3,678 | 1,657,870 |
| Saturday | 6 | 1,595 | 3,604 | 1,889,943 |
| Sunday | 7 | 1,713 | 3,851 | 2,000,429 |

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
| 09:00 | 25 | 376 | 847 | 379,343 | 17.49 |
| 12:15 | 45 | 1,017 | 2,378 | 861,524 | 30.23 |
| 15:30 | 57 | 1,631 | 3,761 | 1,727,621 | 33.75 |
| 18:45 | 72 | 3,312 | 7,507 | 3,708,600 | 53.32 |
| 21:30 | 61 | 3,054 | 6,894 | 3,499,681 | 56.80 |
| 23:45 | 30 | 610 | 1,303 | 610,798 | 20.92 |

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
| Action | 2,098 | 4,705 | 2,303,740 | 489.64 |
| Thriller | 1,851 | 4,237 | 2,133,426 | 503.52 |
| Drama | 1,933 | 4,357 | 2,017,064 | 462.95 |
| Comedy | 1,489 | 3,438 | 1,724,460 | 501.59 |
| Romance | 1,038 | 2,326 | 1,031,916 | 443.64 |
| Sci-Fi | 666 | 1,507 | 717,072 | 475.83 |
| Horror-Comedy | 427 | 983 | 437,916 | 445.49 |
| Historical | 498 | 1,137 | 421,973 | 371.13 |

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
| Hindi | 5,885 | 13,308 | 6,389,739 | 59.23 |
| Tamil | 2,471 | 5,589 | 2,699,756 | 25.03 |
| Telugu | 1,644 | 3,793 | 1,698,072 | 15.74 |

*3 row(s).*

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
| UPI | 4,175 | 4,540,212 | 41.75 |
| Credit Card | 2,271 | 2,425,426 | 22.71 |
| Debit Card | 1,760 | 1,920,356 | 17.60 |
| NetBanking | 944 | 1,016,817 | 9.44 |
| Wallet | 850 | 884,756 | 8.50 |

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
| Mobile App | 4,508 | 4,949,295 | 251 | 5.57 |
| Website | 2,990 | 3,242,844 | 161 | 5.38 |
| Third-Party | 1,458 | 1,469,875 | 186 | 12.76 |
| Kiosk | 1,044 | 1,125,553 | 91 | 8.72 |

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
| Delhi | 1,665 | 135 | 8.11 |
| Ahmedabad | 845 | 62 | 7.34 |
| Hyderabad | 1,125 | 80 | 7.11 |
| Pune | 1,151 | 76 | 6.60 |
| Chennai | 1,222 | 80 | 6.55 |
| Bengaluru | 1,162 | 76 | 6.54 |
| Kolkata | 941 | 61 | 6.48 |
| Mumbai | 1,889 | 119 | 6.30 |

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
| NONE | 6,962 | 6,490 | 7,796,592 | 0 | 0 | 0 |
| WEEKEND10 | 1,027 | 952 | 996,304 | 107,255 | 112.66 | 10 |
| FIRSTBUY5 | 812 | 753 | 865,734 | 44,274 | 58.80 | 5 |
| STUDENT15 | 688 | 633 | 665,886 | 113,891 | 179.92 | 15 |
| FAMILY20 | 511 | 483 | 463,051 | 111,824 | 231.52 | 20 |

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
| 18-24 | 2,180 | 4,936 | 2,337,702 | 1,140.90 |
| 25-34 | 3,020 | 6,830 | 3,231,339 | 1,153.64 |
| 35-44 | 2,370 | 5,375 | 2,532,224 | 1,152.58 |
| 45-54 | 1,607 | 3,690 | 1,800,397 | 1,196.28 |
| 55+ | 823 | 1,859 | 885,905 | 1,167.20 |

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
| Screen 1 | IMAX | 58 | 3,437 | 7,831 | 5,276,756 |
| Screen 2 | 3D | 53 | 2,019 | 4,578 | 1,983,301 |
| Screen 4 | 2D | 68 | 1,770 | 4,052 | 1,349,275 |
| Screen 3 | 2D | 47 | 1,504 | 3,358 | 1,203,516 |
| Screen 5 | 2D | 64 | 1,270 | 2,871 | 974,719 |

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
| Ahmedabad | Dilli Nights | 229 | 206,725 | 1 |
| Ahmedabad | Aakhri Raasta | 176 | 181,920 | 2 |
| Ahmedabad | Chandni Chowk Express | 144 | 121,936 | 3 |
| Bengaluru | Raktham | 250 | 343,324 | 1 |
| Bengaluru | Dhoop Chhaon | 105 | 127,248 | 2 |
| Bengaluru | Golconda | 141 | 119,062 | 3 |
| Chennai | Kanaka | 408 | 555,667 | 1 |
| Chennai | Neruppu | 157 | 145,866 | 2 |
| Chennai | Mehfil | 71 | 97,943 | 3 |
| Delhi | Dilli Nights | 395 | 452,755 | 1 |
| Delhi | Chandni Chowk Express | 286 | 348,715 | 2 |
| Delhi | Rangmanch | 215 | 271,489 | 3 |
| Hyderabad | Vennela | 186 | 158,491 | 1 |
| Hyderabad | Vaanam | 119 | 149,868 | 2 |
| Hyderabad | Golconda | 167 | 141,557 | 3 |
| Kolkata | Dilli Nights | 273 | 298,043 | 1 |
| Kolkata | Chandni Chowk Express | 193 | 191,413 | 2 |
| Kolkata | Neruppu | 110 | 80,382 | 3 |
| Mumbai | Dilli Nights | 453 | 642,793 | 1 |
| Mumbai | Chandni Chowk Express | 242 | 415,947 | 2 |
| Mumbai | Antariksh 2050 | 179 | 249,827 | 3 |
| Pune | Kadal Nilavu | 185 | 237,843 | 1 |
| Pune | Antariksh 2050 | 169 | 197,867 | 2 |
| Pune | Rangmanch | 137 | 162,486 | 3 |

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
| 2025-10 | 787,741 | 787,741 |
| 2025-11 | 1,056,911 | 1,844,652 |
| 2025-12 | 1,223,532 | 3,068,184 |
| 2026-01 | 519,563 | 3,587,747 |
| 2026-02 | 636,632 | 4,224,379 |
| 2026-03 | 720,504 | 4,944,883 |
| 2026-04 | 1,131,470 | 6,076,353 |
| 2026-05 | 1,591,552 | 7,667,905 |
| 2026-06 | 936,395 | 8,604,300 |
| 2026-07 | 580,324 | 9,184,624 |
| 2026-08 | 948,386 | 10,133,010 |
| 2026-09 | 654,557 | 10,787,567 |

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
| 2025-10 | 787,741 | — | — |
| 2025-11 | 1,056,911 | 787,741 | 34.17 |
| 2025-12 | 1,223,532 | 1,056,911 | 15.76 |
| 2026-01 | 519,563 | 1,223,532 | -57.54 |
| 2026-02 | 636,632 | 519,563 | 22.53 |
| 2026-03 | 720,504 | 636,632 | 13.17 |
| 2026-04 | 1,131,470 | 720,504 | 57.04 |
| 2026-05 | 1,591,552 | 1,131,470 | 40.66 |
| 2026-06 | 936,395 | 1,591,552 | -41.16 |
| 2026-07 | 580,324 | 936,395 | -38.03 |
| 2026-08 | 948,386 | 580,324 | 63.42 |
| 2026-09 | 654,557 | 948,386 | -30.98 |

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
| Weekend | 3,308 | 7,455 | 3,890,372 | 1,268.05 |
| Weekday | 6,692 | 15,235 | 6,897,195 | 1,104.79 |

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
| CUS00146 | Rahul Reddy | Mumbai | Loyal | 15 | 45 | 26,947 |
| CUS00675 | Rajesh Mondal | Mumbai | Loyal | 15 | 32 | 26,683 |
| CUS03114 | Pranav Roy | Chennai | Loyal | 14 | 44 | 21,186 |
| CUS00154 | Ira Sethi | Mumbai | Loyal | 14 | 37 | 20,943 |
| CUS00331 | Ishita Chatterjee | Mumbai | Loyal | 9 | 27 | 19,704 |
| CUS00632 | Aadhya Das | Mumbai | Loyal | 12 | 32 | 19,589 |
| CUS03010 | Siddharth Thomas | Chennai | Loyal | 17 | 38 | 18,674 |
| CUS00069 | Aarav Dutta | Mumbai | Loyal | 13 | 29 | 18,156 |
| CUS02892 | Rajesh Arora | Chennai | Loyal | 14 | 37 | 17,607 |
| CUS02426 | Manish Shinde | Hyderabad | Loyal | 15 | 40 | 17,548 |
| CUS03501 | Khushi Mondal | Pune | Loyal | 8 | 30 | 17,432 |
| CUS03089 | Harsh D'Souza | Chennai | Loyal | 13 | 35 | 17,376 |
| CUS00171 | Amit Singh | Mumbai | Loyal | 11 | 23 | 17,287 |
| CUS03447 | Nandini Bansal | Pune | Loyal | 15 | 34 | 17,258 |
| CUS00832 | Nisha Shinde | Mumbai | Loyal | 14 | 28 | 17,216 |

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
| 3,527,510 | 1,983,301 | 5,276,756 | 4,544 | 2,019 | 3,437 |

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
| New | 1,090 | 1,090 | 2,484 | 1,202,536 | 1,103.24 | 1,178.96 |
| Returning | 1,507 | 3,581 | 8,145 | 3,907,880 | 2,593.15 | 1,166.18 |
| Loyal | 883 | 5,329 | 12,061 | 5,677,151 | 6,429.39 | 1,149.22 |

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
| Skyline Multiplex - Andheri | Mumbai | 5 | 28 | 1,102 | 2,559 | 1,573,482 | 39.79 |
| Capital Screens - Saket | Delhi | 5 | 28 | 1,115 | 2,446 | 1,199,819 | 43.94 |
| Metro Cinema - Lower Parel | Mumbai | 5 | 23 | 787 | 1,753 | 1,013,729 | 36.99 |
| Anand Cinema - T. Nagar | Chennai | 5 | 20 | 883 | 2,020 | 998,081 | 52.02 |
| Orion Cinemas - Koramangala | Bengaluru | 5 | 21 | 680 | 1,584 | 782,272 | 39.84 |
| Deccan Mall Cinemas - Baner | Pune | 4 | 13 | 549 | 1,284 | 679,699 | 43.16 |
| Sunset Screens - Kothrud | Pune | 5 | 16 | 602 | 1,383 | 590,442 | 41.49 |
| Regal Multiplex - Dwarka | Delhi | 5 | 21 | 550 | 1,186 | 554,860 | 36.07 |
| Deccan Talkies - Banjara Hills | Hyderabad | 5 | 14 | 549 | 1,207 | 528,611 | 45.42 |
| Sabarmati Screens - SG Highway | Ahmedabad | 5 | 14 | 512 | 1,178 | 512,446 | 42.09 |
| Nova Screens - Gachibowli | Hyderabad | 5 | 22 | 576 | 1,354 | 496,179 | 34.46 |
| Riverside Multiplex - Howrah | Kolkata | 5 | 13 | 549 | 1,217 | 465,482 | 47.43 |
| CineVerse - Whitefield | Bengaluru | 5 | 20 | 482 | 1,101 | 443,625 | 30.10 |
| Bengal Cinema - Salt Lake | Kolkata | 5 | 12 | 392 | 853 | 361,164 | 35.27 |
| Marina Movies - Velachery | Chennai | 5 | 14 | 339 | 803 | 335,792 | 36.81 |
| Heritage Cinema - Navrangpura | Ahmedabad | 5 | 11 | 333 | 762 | 251,884 | 41.58 |

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
| Standard | 6,061 | 13,795 | 5,341,474 | 387.20 | 949.26 |
| Premium | 2,962 | 6,642 | 3,569,185 | 537.37 | 1,288.05 |
| Recliner | 977 | 2,253 | 1,876,908 | 833.07 | 2,055.76 |

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
| Dilli Nights | 1,841,194 | 1 | 17.07 | 17.07 | 1 |
| Chandni Chowk Express | 1,317,244 | 2 | 12.21 | 29.28 | 1 |
| Rangmanch | 957,638 | 3 | 8.88 | 38.16 | 1 |
| Kanaka | 793,838 | 4 | 7.36 | 45.51 | 1 |
| Antariksh 2050 | 717,072 | 5 | 6.65 | 52.16 | 1 |
| Aakhri Raasta | 618,015 | 6 | 5.73 | 57.89 | 2 |
| Raktham | 565,851 | 7 | 5.25 | 63.14 | 2 |
| Vaanam | 552,561 | 8 | 5.12 | 68.26 | 2 |
| Pei Veedu | 437,916 | 9 | 4.06 | 72.32 | 2 |
| Mehfil | 436,668 | 10 | 4.05 | 76.37 | 2 |
| Golconda | 421,973 | 11 | 3.91 | 80.28 | 3 |
| Kadal Nilavu | 333,502 | 12 | 3.09 | 83.37 | 3 |
| Neruppu | 326,036 | 13 | 3.02 | 86.39 | 3 |
| Bhramaram | 268,566 | 14 | 2.49 | 88.88 | 3 |
| Vennela | 261,746 | 15 | 2.43 | 91.31 | 4 |
| Dhoop Chhaon | 252,371 | 16 | 2.34 | 93.65 | 4 |
| Shor Macha | 249,537 | 17 | 2.31 | 95.96 | 4 |
| Thiruvizha | 157,679 | 18 | 1.46 | 97.42 | 4 |
| Manikya | 154,686 | 19 | 1.43 | 98.86 | 5 |
| Sivappu Manjal | 74,558 | 20 | 0.69 | 99.55 | 5 |
| Suryodayam | 25,250 | 21 | 0.23 | 99.78 | 5 |
| Iravu Payanam | 23,666 | 22 | 0.22 | 100 | 5 |

*22 row(s).*

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
| Dhoop Chhaon | 8.40 | Drama | Hindi | 285 | 634 | 252,371 | 0.04 |
| Sivappu Manjal | 8.30 | Drama | Tamil | 57 | 142 | 74,558 | 0.04 |
| Neruppu | 8.20 | Action | Tamil | 386 | 855 | 326,036 | 0.04 |
| Dilli Nights | 8.10 | Thriller | Hindi | 1,640 | 3,724 | 1,841,194 | 0.04 |
| Golconda | 8.10 | Historical | Telugu | 498 | 1,137 | 421,973 | 0.04 |
| Vaanam | 8 | Drama | Tamil | 539 | 1,198 | 552,561 | 0.04 |
| Raktham | 8 | Action | Telugu | 500 | 1,117 | 565,851 | 0.04 |
| Iravu Payanam | 7.90 | Thriller | Tamil | 28 | 60 | 23,666 | 0.04 |
| Aakhri Raasta | 7.80 | Action | Hindi | 644 | 1,442 | 618,015 | 0.04 |
| Suryodayam | 7.80 | Drama | Telugu | 12 | 32 | 25,250 | 0.04 |
| Bhramaram | 7.60 | Thriller | Telugu | 183 | 453 | 268,566 | 0.04 |
| Antariksh 2050 | 7.50 | Sci-Fi | Hindi | 666 | 1,507 | 717,072 | 0.04 |
| Rangmanch | 7.40 | Drama | Hindi | 888 | 1,987 | 957,638 | 0.04 |
| Vennela | 7.30 | Romance | Telugu | 299 | 690 | 261,746 | 0.04 |
| Kanaka | 7.20 | Action | Tamil | 568 | 1,291 | 793,838 | 0.04 |
| Mehfil | 7.20 | Romance | Hindi | 432 | 932 | 436,668 | 0.04 |
| Kadal Nilavu | 7.10 | Romance | Tamil | 307 | 704 | 333,502 | 0.04 |
| Thiruvizha | 7 | Comedy | Tamil | 159 | 356 | 157,679 | 0.04 |
| Manikya | 7 | Drama | Telugu | 152 | 364 | 154,686 | 0.04 |
| Chandni Chowk Express | 6.90 | Comedy | Hindi | 1,117 | 2,588 | 1,317,244 | 0.04 |
| Pei Veedu | 6.80 | Horror-Comedy | Tamil | 427 | 983 | 437,916 | 0.04 |
| Shor Macha | 6.50 | Comedy | Hindi | 213 | 494 | 249,537 | 0.04 |

*22 row(s).*

## Reproduce

```powershell
$env:PYTHONPATH = "D:\chinmay\movie-ticket-booking-analytics\src"
D:\venvs\cinema\Scripts\python.exe src\04_run_sql_queries.py
```

The runner stops before writing this file if any query errors or any
revenue slice fails to reconcile.
