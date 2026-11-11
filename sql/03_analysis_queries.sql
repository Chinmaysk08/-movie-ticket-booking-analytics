-- ============================================================================
-- Movie Ticket Booking Analytics -- analytical SQL (dataset v2)
-- ============================================================================
-- 25 queries against the star schema in sql/01_schema.sql.
--
-- Conventions
-- -----------
-- * Revenue and tickets always filter booking_status = 'Confirmed'. Cancelled
--   bookings are real events but their seats were released, so they must not
--   inflate revenue or occupancy.
-- * Occupancy comes from V_SHOW_PERFORMANCE, which derives it as confirmed
--   seats / seats_capacity at the show level. Averaging it per booking would
--   weight busy shows more heavily.
-- * Every query that slices confirmed revenue should sum back to INR
--   10,823,192. src/04_run_sql_queries.py enforces that automatically.
--
-- Run every query and capture the results:
--     python src/04_run_sql_queries.py
-- ============================================================================


-- Q1: Overall KPIs
-- Business question: what are total bookings, tickets, revenue and average value?
SELECT COUNT(*) AS total_bookings,
       SUM(CASE WHEN booking_status = 'Confirmed' THEN 1 ELSE 0 END) AS confirmed_bookings,
       SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_bookings,
       SUM(CASE WHEN booking_status = 'Confirmed' THEN seats ELSE 0 END) AS confirmed_tickets,
       SUM(CASE WHEN booking_status = 'Confirmed' THEN total_amount ELSE 0 END) AS revenue_inr,
       ROUND(AVG(CASE WHEN booking_status = 'Confirmed' THEN total_amount END), 2) AS avg_booking_value_inr,
       ROUND(100 * SUM(CASE WHEN booking_status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2) AS cancellation_rate_pct
FROM fact_bookings;


-- Q2: Monthly revenue trend
-- Business question: how does revenue trend month over month (by show date)?
SELECT TO_CHAR(d.full_date, 'YYYY-MM') AS month,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
FROM fact_bookings f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY TO_CHAR(d.full_date, 'YYYY-MM')
ORDER BY month;


-- Q3: Top 10 movies by revenue
-- Business question: which movies earn the most, and do they also sell the most tickets?
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
FETCH FIRST 10 ROWS ONLY;


-- Q4: City performance
-- Business question: how does revenue vary by city, and is it volume or price?
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
ORDER BY cf.revenue_inr DESC;


-- Q5: Revenue by day of week
-- Business question: which days of the week carry the most demand?
SELECT d.day_name,
       d.day_of_week,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
FROM fact_bookings f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.day_name, d.day_of_week
ORDER BY d.day_of_week;


-- Q6: Show-time performance
-- Business question: which slots are peak, and how large is the occupancy gap?
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
ORDER BY sf.show_time;


-- Q7: Genre performance
-- Business question: which genres dominate revenue and ticket sales?
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
ORDER BY revenue_inr DESC;


-- Q8: Language distribution
-- Business question: how is demand split across Hindi, Tamil and Telugu films?
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
ORDER BY revenue_inr DESC;


-- Q9: Payment method split
-- Business question: which payment methods do customers prefer?
SELECT p.payment_method,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(COUNT(*) * 100 / SUM(COUNT(*)) OVER (), 2) AS pct_of_bookings
FROM fact_bookings f
JOIN dim_payment p ON p.payment_key = f.payment_key
GROUP BY p.payment_method
ORDER BY revenue_inr DESC;


-- Q10: Booking channel performance
-- Business question: which channels bring revenue, and which cancel most?
SELECT p.booking_channel,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       SUM(CASE WHEN f.booking_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_bookings,
       ROUND(100 * SUM(CASE WHEN f.booking_status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2)
           AS cancellation_rate_pct
FROM fact_bookings f
JOIN dim_payment p ON p.payment_key = f.payment_key
GROUP BY p.booking_channel
ORDER BY revenue_inr DESC;


-- Q11: Cancellation rate by city
-- Business question: is cancellation a local problem or a network-wide one?
SELECT t.city,
       COUNT(*) AS total_bookings,
       SUM(CASE WHEN f.booking_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled,
       ROUND(100 * SUM(CASE WHEN f.booking_status = 'Cancelled' THEN 1 ELSE 0 END) / COUNT(*), 2)
           AS cancellation_rate_pct
FROM fact_bookings f
JOIN dim_show s    ON s.show_key = f.show_key
JOIN dim_theatre t ON t.theatre_key = s.theatre_key
GROUP BY t.city
ORDER BY cancellation_rate_pct DESC;


-- Q12: Promo code effectiveness
-- Business question: which promos generate revenue and how much margin do they cost?
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
ORDER BY revenue_inr DESC;


-- Q13: Age-group analysis
-- Business question: which age bands book and spend the most?
SELECT c.age_group,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(AVG(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount END), 2)
           AS avg_booking_value_inr
FROM fact_bookings f
JOIN dim_customer c ON c.customer_key = f.customer_key
GROUP BY c.age_group
ORDER BY c.age_group;


-- Q14: Screen and format performance
-- Business question: do IMAX/3D screens earn more per booking than 2D screens?
SELECT s.screen,
       s.format,
       COUNT(DISTINCT s.show_key) AS shows,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
FROM fact_bookings f
JOIN dim_show s ON s.show_key = f.show_key
GROUP BY s.screen, s.format
ORDER BY revenue_inr DESC;


-- Q15: Top 3 movies per city (RANK)
-- Business question: is the most popular movie different in each city?
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
ORDER BY city, city_rank;


-- Q16: Running monthly revenue (window function)
-- Business question: what is cumulative revenue across the year?
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
ORDER BY month;


-- Q17: Month-over-month growth (LAG)
-- Business question: which months grew and which declined?
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
ORDER BY month;


-- Q18: Weekend vs weekday
-- Business question: how much more do weekends deliver than weekdays?
SELECT CASE WHEN d.is_weekend = 'Y' THEN 'Weekend' ELSE 'Weekday' END AS day_type,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END) AS tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(AVG(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount END), 2)
           AS avg_booking_value_inr
FROM fact_bookings f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.is_weekend
ORDER BY d.is_weekend DESC;


-- Q19: Customers with the highest spend (CTE)
-- Business question: who are the most valuable customers?
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
FETCH FIRST 15 ROWS ONLY;


-- Q20: Revenue by format (pivot-style aggregation)
-- Business question: how much revenue comes from each screen format?
SELECT SUM(CASE WHEN s.format = '2D'   AND f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_2d,
       SUM(CASE WHEN s.format = '3D'   AND f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_3d,
       SUM(CASE WHEN s.format = 'IMAX' AND f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_imax,
       COUNT(CASE WHEN s.format = '2D'   THEN 1 END) AS bookings_2d,
       COUNT(CASE WHEN s.format = '3D'   THEN 1 END) AS bookings_3d,
       COUNT(CASE WHEN s.format = 'IMAX' THEN 1 END) AS bookings_imax
FROM fact_bookings f
JOIN dim_show s ON s.show_key = f.show_key;


-- Q21: Customer segments (New / Returning / Loyal)
-- Business question: how concentrated is demand in loyal customers?
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
ORDER BY CASE c.customer_type WHEN 'New' THEN 1 WHEN 'Returning' THEN 2 ELSE 3 END;


-- Q22: Theatre performance
-- Business question: which multiplexes under/over-perform?
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
ORDER BY tf.revenue_inr DESC;


-- Q23: Ticket-type profitability
-- Business question: which ticket class earns the most per seat?
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
ORDER BY revenue_inr DESC;


-- Q24: Revenue concentration (Pareto)
-- Business question: what share of revenue comes from the top 20% of movies?
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
ORDER BY revenue_rank;


-- Q25: Does a higher rating mean more bookings?
-- Business question: is movie rating correlated with demand?
-- CORR is used analytically so every row carries the same overall correlation.
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
ORDER BY rating DESC, bookings DESC;
