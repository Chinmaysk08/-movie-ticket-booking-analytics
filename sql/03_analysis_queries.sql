-- Movie Ticket Booking Analytics - Oracle SQL Analysis
-- 20 Business Questions with SQL

-- Q1: Overall KPIs
SELECT 
  COUNT(*) AS total_bookings,
  SUM(CASE WHEN booking_status='Confirmed' THEN 1 ELSE 0 END) AS confirmed_bookings,
  SUM(CASE WHEN booking_status='Cancelled' THEN 1 ELSE 0 END) AS cancelled_bookings,
  ROUND(SUM(CASE WHEN booking_status='Confirmed' THEN total_amount ELSE 0 END),2) AS total_revenue_inr,
  ROUND(AVG(CASE WHEN booking_status='Confirmed' THEN total_amount ELSE NULL END),2) AS avg_booking_value_inr
FROM fact_bookings;

-- Q2: Monthly Revenue Trend
SELECT TO_CHAR(d.full_date,'YYYY-MM') AS month,
       COUNT(f.booking_fact_key) AS bookings,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
FROM fact_bookings f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY TO_CHAR(d.full_date,'YYYY-MM')
ORDER BY month;

-- Q3: Top 10 Movies by Revenue
SELECT * FROM (
  SELECT m.movie_title, m.genre, m.language,
         COUNT(f.booking_fact_key) AS bookings,
         SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
  FROM fact_bookings f
  JOIN dim_movie m ON f.movie_key = m.movie_key
  GROUP BY m.movie_title, m.genre, m.language
  ORDER BY revenue_inr DESC
)
FETCH FIRST 10 ROWS ONLY;

-- Q4: City-wise Performance
SELECT c.city,
       COUNT(f.booking_fact_key) AS bookings,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.seats ELSE 0 END) AS seats_sold,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END)/
             NULLIF(COUNT(DISTINCT f.show_key),0),2) AS revenue_per_show
FROM fact_bookings f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.city
ORDER BY revenue_inr DESC;

-- Q5: Revenue by Day of Week
SELECT d.day_name,
       COUNT(f.booking_fact_key) AS bookings,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
FROM fact_bookings f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.day_name, d.day_of_week
ORDER BY d.day_of_week;

-- Q6: Show Time Analysis (Peak Hours)
SELECT s.show_time,
       COUNT(f.booking_fact_key) AS bookings,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.seats ELSE 0 END) AS seats_sold,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
FROM fact_bookings f
JOIN dim_show s ON f.show_key = s.show_key
GROUP BY s.show_time
ORDER BY s.show_time;

-- Q7: Genre Performance
SELECT m.genre,
       COUNT(f.booking_fact_key) AS bookings,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(AVG(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount/f.seats ELSE NULL END),2) AS avg_ticket_price
FROM fact_bookings f
JOIN dim_movie m ON f.movie_key = m.movie_key
GROUP BY m.genre
ORDER BY revenue_inr DESC;

-- Q8: Language Distribution
SELECT m.language,
       COUNT(f.booking_fact_key) AS bookings,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
FROM fact_bookings f
JOIN dim_movie m ON f.movie_key = m.movie_key
GROUP BY m.language
ORDER BY revenue_inr DESC;

-- Q9: Payment Method Split
SELECT p.payment_method,
       COUNT(f.booking_fact_key) AS bookings,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(COUNT(f.booking_fact_key)*100.0/SUM(COUNT(*)) OVER(),2) AS pct_of_bookings
FROM fact_bookings f
JOIN dim_payment p ON f.payment_key = p.payment_key
GROUP BY p.payment_method
ORDER BY revenue_inr DESC;

-- Q10: Booking Channel Performance
SELECT p.booking_channel,
       COUNT(f.booking_fact_key) AS bookings,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(SUM(CASE WHEN f.booking_status='Cancelled' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS cancellation_rate_pct
FROM fact_bookings f
JOIN dim_payment p ON f.payment_key = p.payment_key
GROUP BY p.booking_channel
ORDER BY revenue_inr DESC;

-- Q11: Cancellation Rate by City
SELECT c.city,
       COUNT(*) AS total_bookings,
       SUM(CASE WHEN f.booking_status='Cancelled' THEN 1 ELSE 0 END) AS cancelled,
       ROUND(SUM(CASE WHEN f.booking_status='Cancelled' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS cancel_rate_pct
FROM fact_bookings f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.city
HAVING COUNT(*) > 50
ORDER BY cancel_rate_pct DESC;

-- Q12: Promo Code Effectiveness
SELECT NVL(f.promo_code,'NONE') AS promo_code,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.discount_amount ELSE 0 END) AS total_discount_given,
       ROUND(AVG(CASE WHEN f.booking_status='Confirmed' THEN f.discount_amount ELSE NULL END),2) AS avg_discount
FROM fact_bookings f
GROUP BY f.promo_code
ORDER BY revenue_inr DESC;

-- Q13: Age Group Analysis
SELECT c.age_group,
       COUNT(f.booking_fact_key) AS bookings,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(AVG(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE NULL END),2) AS avg_spend
FROM fact_bookings f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.age_group
ORDER BY revenue_inr DESC;

-- Q14: Screen & Format Performance
SELECT s.screen, s.format,
       COUNT(f.booking_fact_key) AS bookings,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.seats ELSE 0 END) AS seats_sold,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
FROM fact_bookings f
JOIN dim_show s ON f.show_key = s.show_key
GROUP BY s.screen, s.format
ORDER BY revenue_inr DESC;

-- Q15: Top Movies per City (RANK)
SELECT * FROM (
  SELECT c.city, m.movie_title,
         SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
         RANK() OVER (PARTITION BY c.city ORDER BY SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) DESC) AS city_rank
  FROM fact_bookings f
  JOIN dim_customer c ON f.customer_key = c.customer_key
  JOIN dim_movie m ON f.movie_key = m.movie_key
  GROUP BY c.city, m.movie_title
)
WHERE city_rank <= 3
ORDER BY city, city_rank;

-- Q16: Running Monthly Revenue (Window Function)
SELECT month, revenue_inr,
       SUM(revenue_inr) OVER (ORDER BY month ROWS UNBOUNDED PRECEDING) AS running_total_inr
FROM (
  SELECT TO_CHAR(d.full_date,'YYYY-MM') AS month,
         SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
  FROM fact_bookings f
  JOIN dim_date d ON f.date_key = d.date_key
  GROUP BY TO_CHAR(d.full_date,'YYYY-MM')
)
ORDER BY month;

-- Q17: Month-over-Month Growth
SELECT month, revenue_inr,
       LAG(revenue_inr,1) OVER (ORDER BY month) AS prev_month_revenue,
       ROUND((revenue_inr - LAG(revenue_inr,1) OVER (ORDER BY month))/
             NULLIF(LAG(revenue_inr,1) OVER (ORDER BY month),0)*100,2) AS mom_growth_pct
FROM (
  SELECT TO_CHAR(d.full_date,'YYYY-MM') AS month,
         SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr
  FROM fact_bookings f
  JOIN dim_date d ON f.date_key = d.date_key
  GROUP BY TO_CHAR(d.full_date,'YYYY-MM')
)
ORDER BY month;

-- Q18: Weekend vs Weekday Performance
SELECT d.is_weekend,
       CASE WHEN d.is_weekend='Y' THEN 'Weekend' ELSE 'Weekday' END AS day_type,
       COUNT(f.booking_fact_key) AS bookings,
       SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS revenue_inr,
       ROUND(AVG(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE NULL END),2) AS avg_booking_value
FROM fact_bookings f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.is_weekend
ORDER BY d.is_weekend DESC;

-- Q19: Customers with Most Bookings (CTE)
WITH cust_stats AS (
  SELECT c.customer_name, c.city, c.age_group,
         COUNT(f.booking_fact_key) AS total_bookings,
         SUM(CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END) AS total_spent
  FROM fact_bookings f
  JOIN dim_customer c ON f.customer_key = c.customer_key
  GROUP BY c.customer_name, c.city, c.age_group
)
SELECT * FROM cust_stats
WHERE total_bookings >= 2
ORDER BY total_spent DESC
FETCH FIRST 15 ROWS ONLY;

-- Q20: Revenue by Format with Pivot-like Aggregation
SELECT 
  SUM(CASE WHEN s.format='2D' THEN CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END ELSE 0 END) AS revenue_2d,
  SUM(CASE WHEN s.format='3D' THEN CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END ELSE 0 END) AS revenue_3d,
  SUM(CASE WHEN s.format='IMAX' THEN CASE WHEN f.booking_status='Confirmed' THEN f.total_amount ELSE 0 END ELSE 0 END) AS revenue_imax,
  COUNT(CASE WHEN s.format='2D' THEN 1 END) AS bookings_2d,
  COUNT(CASE WHEN s.format='3D' THEN 1 END) AS bookings_3d,
  COUNT(CASE WHEN s.format='IMAX' THEN 1 END) AS bookings_imax
FROM fact_bookings f
JOIN dim_show s ON f.show_key = s.show_key;
