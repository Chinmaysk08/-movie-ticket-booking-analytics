-- ============================================================================
-- Movie Ticket Booking Analytics -- Oracle 26ai Free star schema (dataset v2)
-- ============================================================================
-- Run as the CINEMA user in FREEPDB1, either with SQLcl:
--     sql cinema@localhost:1521/FREEPDB1 @sql/01_schema.sql
-- or from Python (drops, creates, commits, verifies):
--     python src/02_create_schema.py
--
-- Design notes
-- ------------
-- * Surrogate NUMBER keys for dimensions; the natural business key is kept
--   with a UNIQUE constraint so the load can be reconciled.
-- * FACT_BOOKINGS keeps one row per booking. Cancelled bookings stay in the
--   fact table: they are real events, and their seats were released, so every
--   revenue/occupancy query filters booking_status = 'Confirmed'.
-- * Ratios are NOT stored as facts. Occupancy is confirmed seats divided by
--   the show's capacity, exposed by V_SHOW_PERFORMANCE, so it can never
--   disagree with its inputs.
-- * CHECK constraints encode the business rules from docs/data_dictionary.md,
--   including total_amount = ticket_price*seats + fee - discount.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 0. Drop in dependency order (ignore ORA-00942: table or view does not exist)
-- ---------------------------------------------------------------------------
BEGIN EXECUTE IMMEDIATE 'DROP VIEW v_booking_detail'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP VIEW v_show_performance'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP VIEW v_monthly_revenue'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP VIEW v_movie_performance'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE fact_bookings CASCADE CONSTRAINTS PURGE'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE dim_show CASCADE CONSTRAINTS PURGE'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE dim_payment CASCADE CONSTRAINTS PURGE'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE dim_date CASCADE CONSTRAINTS PURGE'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE dim_theatre CASCADE CONSTRAINTS PURGE'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE dim_movie CASCADE CONSTRAINTS PURGE'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/
BEGIN EXECUTE IMMEDIATE 'DROP TABLE dim_customer CASCADE CONSTRAINTS PURGE'; EXCEPTION WHEN OTHERS THEN IF SQLCODE != -942 THEN RAISE; END IF; END;
/

-- ---------------------------------------------------------------------------
-- 1. Dimensions
-- ---------------------------------------------------------------------------

-- One row per person. customer_type is a derived attribute of the 12-month
-- window (New = 1 booking, Returning = 2-3, Loyal = 4+).
CREATE TABLE dim_customer (
    customer_key    NUMBER(6)     NOT NULL,
    customer_id     VARCHAR2(10)  NOT NULL,
    customer_name   VARCHAR2(80)  NOT NULL,
    customer_email  VARCHAR2(120) NOT NULL,
    phone           VARCHAR2(10)  NOT NULL,
    age             NUMBER(3)     NOT NULL,
    age_group       VARCHAR2(10)  NOT NULL,
    gender          VARCHAR2(10)  NOT NULL,
    city            VARCHAR2(30)  NOT NULL,
    customer_type   VARCHAR2(10)  NOT NULL,
    CONSTRAINT pk_customer       PRIMARY KEY (customer_key),
    CONSTRAINT uq_customer_id    UNIQUE (customer_id),
    CONSTRAINT ck_customer_age   CHECK (age BETWEEN 18 AND 68),
    CONSTRAINT ck_customer_group CHECK (age_group IN ('18-24','25-34','35-44','45-54','55+')),
    CONSTRAINT ck_customer_gender CHECK (gender IN ('Male','Female','Other')),
    CONSTRAINT ck_customer_type  CHECK (customer_type IN ('New','Returning','Loyal')),
    CONSTRAINT ck_customer_city  CHECK (city IN ('Mumbai','Delhi','Bengaluru','Hyderabad',
                                                 'Chennai','Pune','Kolkata','Ahmedabad')),
    CONSTRAINT ck_customer_phone CHECK (REGEXP_LIKE(phone, '^[6-9][0-9]{9}$'))
);

-- One row per fictional title. rating belongs to the movie, not the booking.
CREATE TABLE dim_movie (
    movie_key    NUMBER(4)    NOT NULL,
    movie_title  VARCHAR2(80) NOT NULL,
    genre        VARCHAR2(20) NOT NULL,
    language     VARCHAR2(10) NOT NULL,
    rating       NUMBER(3,1)  NOT NULL,
    CONSTRAINT pk_movie        PRIMARY KEY (movie_key),
    CONSTRAINT uq_movie_title  UNIQUE (movie_title),
    CONSTRAINT ck_movie_rating CHECK (rating BETWEEN 0 AND 10),
    CONSTRAINT ck_movie_lang   CHECK (language IN ('Hindi','Tamil','Telugu')),
    CONSTRAINT ck_movie_genre  CHECK (genre IN ('Action','Comedy','Drama','Historical',
                                                'Horror-Comedy','Romance','Sci-Fi','Thriller'))
);

-- One row per multiplex. screen counts describe the screens that actually
-- appear in the booking sample (79 of the 80 designed screens).
CREATE TABLE dim_theatre (
    theatre_key       NUMBER(4)    NOT NULL,
    theatre_name      VARCHAR2(80) NOT NULL,
    city              VARCHAR2(30) NOT NULL,
    screens_in_sample NUMBER(2)    NOT NULL,
    total_capacity    NUMBER(5)    NOT NULL,
    CONSTRAINT pk_theatre        PRIMARY KEY (theatre_key),
    CONSTRAINT uq_theatre_name   UNIQUE (theatre_name),
    CONSTRAINT ck_theatre_city   CHECK (city IN ('Mumbai','Delhi','Bengaluru','Hyderabad',
                                                 'Chennai','Pune','Kolkata','Ahmedabad')),
    CONSTRAINT ck_theatre_screens CHECK (screens_in_sample BETWEEN 1 AND 5),
    CONSTRAINT ck_theatre_capacity CHECK (total_capacity > 0)
);

-- Calendar for the design window 2025-10-01 .. 2026-09-30 (365 rows).
-- date_key is a smart key: YYYYMMDD (e.g. 20260115).
CREATE TABLE dim_date (
    date_key      NUMBER(8)   NOT NULL,
    full_date     DATE        NOT NULL,
    day_of_month  NUMBER(2)   NOT NULL,
    day_of_week   NUMBER(1)   NOT NULL,   -- ISO: 1 = Monday ... 7 = Sunday
    day_name      VARCHAR2(10) NOT NULL,
    month_number  NUMBER(2)   NOT NULL,
    month_name    VARCHAR2(10) NOT NULL,
    quarter       NUMBER(1)   NOT NULL,
    year          NUMBER(4)   NOT NULL,
    is_weekend    CHAR(1)     NOT NULL,
    CONSTRAINT pk_date        PRIMARY KEY (date_key),
    CONSTRAINT uq_date_full   UNIQUE (full_date),
    CONSTRAINT ck_date_dow    CHECK (day_of_week BETWEEN 1 AND 7),
    CONSTRAINT ck_date_weekend CHECK (is_weekend IN ('Y','N')),
    CONSTRAINT ck_date_month  CHECK (month_number BETWEEN 1 AND 12),
    CONSTRAINT ck_date_quarter CHECK (quarter BETWEEN 1 AND 4)
);

-- Payment method x booking channel. 18 observed combinations, not 5 x 4 = 20:
-- Kiosk does not offer NetBanking or Wallet in this dataset.
CREATE TABLE dim_payment (
    payment_key     NUMBER(3)    NOT NULL,
    payment_method  VARCHAR2(20) NOT NULL,
    booking_channel VARCHAR2(20) NOT NULL,
    CONSTRAINT pk_payment        PRIMARY KEY (payment_key),
    CONSTRAINT uq_payment_combo  UNIQUE (payment_method, booking_channel),
    CONSTRAINT ck_payment_method CHECK (payment_method IN ('Credit Card','Debit Card',
                                                           'NetBanking','UPI','Wallet')),
    CONSTRAINT ck_payment_channel CHECK (booking_channel IN ('Kiosk','Mobile App',
                                                             'Third-Party','Website'))
);

-- One row per show: one movie, at one screen, on one date, at one time.
CREATE TABLE dim_show (
    show_key       NUMBER(5)    NOT NULL,
    show_id        VARCHAR2(10) NOT NULL,
    movie_key      NUMBER(4)    NOT NULL,
    theatre_key    NUMBER(4)    NOT NULL,
    screen         VARCHAR2(10) NOT NULL,
    format         VARCHAR2(6)  NOT NULL,
    seats_capacity NUMBER(4)    NOT NULL,
    show_date      DATE         NOT NULL,
    show_time      VARCHAR2(5)  NOT NULL,
    CONSTRAINT pk_show          PRIMARY KEY (show_key),
    CONSTRAINT uq_show_id       UNIQUE (show_id),
    CONSTRAINT fk_show_movie    FOREIGN KEY (movie_key)   REFERENCES dim_movie (movie_key),
    CONSTRAINT fk_show_theatre  FOREIGN KEY (theatre_key) REFERENCES dim_theatre (theatre_key),
    CONSTRAINT ck_show_capacity CHECK (seats_capacity > 0),
    CONSTRAINT ck_show_format   CHECK (format IN ('2D','3D','IMAX')),
    CONSTRAINT ck_show_time     CHECK (show_time IN ('09:00','12:15','15:30','18:45','21:30','23:45'))
);

-- ---------------------------------------------------------------------------
-- 2. Fact table
-- ---------------------------------------------------------------------------
CREATE TABLE fact_bookings (
    booking_id       VARCHAR2(10) NOT NULL,
    customer_key     NUMBER(6)    NOT NULL,
    show_key         NUMBER(5)    NOT NULL,
    date_key         NUMBER(8)    NOT NULL,
    payment_key      NUMBER(3)    NOT NULL,
    ticket_type      VARCHAR2(10) NOT NULL,
    seats            NUMBER(2)    NOT NULL,
    ticket_price     NUMBER(6)    NOT NULL,
    convenience_fee  NUMBER(5)    NOT NULL,
    promo_code       VARCHAR2(12) NOT NULL,
    discount_amount  NUMBER(7)    NOT NULL,
    total_amount     NUMBER(9)    NOT NULL,
    booking_status   VARCHAR2(10) NOT NULL,
    booking_datetime DATE         NOT NULL,
    CONSTRAINT pk_fact            PRIMARY KEY (booking_id),
    CONSTRAINT fk_fact_customer   FOREIGN KEY (customer_key) REFERENCES dim_customer (customer_key),
    CONSTRAINT fk_fact_show       FOREIGN KEY (show_key)     REFERENCES dim_show (show_key),
    CONSTRAINT fk_fact_date       FOREIGN KEY (date_key)     REFERENCES dim_date (date_key),
    CONSTRAINT fk_fact_payment    FOREIGN KEY (payment_key)  REFERENCES dim_payment (payment_key),
    CONSTRAINT ck_fact_seats      CHECK (seats BETWEEN 1 AND 10),
    CONSTRAINT ck_fact_price      CHECK (ticket_price > 0),
    CONSTRAINT ck_fact_fee        CHECK (convenience_fee >= 0),
    CONSTRAINT ck_fact_discount   CHECK (discount_amount >= 0),
    CONSTRAINT ck_fact_total      CHECK (total_amount >= 0),
    CONSTRAINT ck_fact_status     CHECK (booking_status IN ('Confirmed','Cancelled')),
    CONSTRAINT ck_fact_ticket     CHECK (ticket_type IN ('Standard','Premium','Recliner')),
    CONSTRAINT ck_fact_promo      CHECK (promo_code IN ('NONE','FIRSTBUY5','WEEKEND10',
                                                        'STUDENT15','FAMILY20')),
    -- The revenue identity is enforced by the database, not just by the loader.
    CONSTRAINT ck_fact_math       CHECK (
        total_amount = ticket_price * seats + convenience_fee - discount_amount
    )
);

-- Foreign-key indexes: Oracle does not create them automatically, and every
-- analytical join starts from the fact table.
CREATE INDEX ix_fact_customer ON fact_bookings (customer_key);
CREATE INDEX ix_fact_show     ON fact_bookings (show_key);
CREATE INDEX ix_fact_date     ON fact_bookings (date_key);
CREATE INDEX ix_fact_payment  ON fact_bookings (payment_key);
CREATE INDEX ix_show_date     ON dim_show (show_date);

-- ---------------------------------------------------------------------------
-- 3. Views
-- ---------------------------------------------------------------------------

-- Show-level performance. Occupancy is derived here, so it always equals
-- confirmed seats / capacity. Cancelled bookings contribute 0 seats.
CREATE OR REPLACE VIEW v_show_performance AS
WITH fact AS (
    SELECT show_key,
           COUNT(*) AS bookings,
           SUM(CASE WHEN booking_status = 'Confirmed' THEN seats ELSE 0 END)        AS confirmed_seats,
           SUM(CASE WHEN booking_status = 'Confirmed' THEN total_amount ELSE 0 END) AS confirmed_revenue
    FROM fact_bookings
    GROUP BY show_key
)
SELECT s.show_key,
       s.show_id,
       m.movie_title,
       m.genre,
       m.language,
       m.rating,
       t.theatre_name,
       t.city,
       s.screen,
       s.format,
       s.seats_capacity,
       s.show_date,
       s.show_time,
       NVL(f.bookings, 0)          AS bookings,
       NVL(f.confirmed_seats, 0)   AS confirmed_seats,
       NVL(f.confirmed_revenue, 0) AS confirmed_revenue,
       ROUND(NVL(f.confirmed_seats, 0) / s.seats_capacity, 4) AS occupancy_rate
FROM dim_show s
JOIN dim_movie m   ON m.movie_key = s.movie_key
JOIN dim_theatre t ON t.theatre_key = s.theatre_key
LEFT JOIN fact f   ON f.show_key = s.show_key;

-- Flat booking view for ad-hoc analysis and Power BI previews. One row per
-- booking, with every descriptive attribute already joined.
CREATE OR REPLACE VIEW v_booking_detail AS
SELECT f.booking_id,
       f.booking_datetime,
       f.booking_status,
       c.customer_id,
       c.customer_name,
       c.gender,
       c.age,
       c.age_group,
       c.city         AS customer_city,
       c.customer_type,
       m.movie_title,
       m.genre,
       m.language,
       m.rating,
       t.theatre_name,
       t.city         AS theatre_city,
       s.show_id,
       s.screen,
       s.format,
       s.show_date,
       s.show_time,
       p.payment_method,
       p.booking_channel,
       f.ticket_type,
       f.seats,
       f.ticket_price,
       f.convenience_fee,
       f.promo_code,
       f.discount_amount,
       f.total_amount
FROM fact_bookings f
JOIN dim_customer c ON c.customer_key = f.customer_key
JOIN dim_show s     ON s.show_key     = f.show_key
JOIN dim_movie m    ON m.movie_key    = s.movie_key
JOIN dim_theatre t  ON t.theatre_key  = s.theatre_key
JOIN dim_payment p  ON p.payment_key  = f.payment_key;

-- Monthly revenue at show-date grain. Useful for a trend line without
-- repeating the CASE expressions in every query or DAX measure.
CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT d.year,
       d.month_number,
       TO_CHAR(d.full_date, 'YYYY-MM') AS month,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END)        AS confirmed_tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS confirmed_revenue,
       ROUND(AVG(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount END), 2)
           AS avg_booking_value
FROM fact_bookings f
JOIN dim_date d ON d.date_key = f.date_key
GROUP BY d.year, d.month_number, TO_CHAR(d.full_date, 'YYYY-MM');

-- Movie-level performance. One row per movie, with revenue per ticket derived
-- from confirmed seats rather than from booking counts.
CREATE OR REPLACE VIEW v_movie_performance AS
SELECT m.movie_key,
       m.movie_title,
       m.genre,
       m.language,
       m.rating,
       COUNT(*) AS bookings,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END)        AS confirmed_tickets,
       SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END) AS confirmed_revenue,
       ROUND(
           SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.total_amount ELSE 0 END)
           / NULLIF(SUM(CASE WHEN f.booking_status = 'Confirmed' THEN f.seats ELSE 0 END), 0),
           2
       ) AS avg_price_per_ticket
FROM fact_bookings f
JOIN dim_show s  ON s.show_key = f.show_key
JOIN dim_movie m ON m.movie_key = s.movie_key
GROUP BY m.movie_key, m.movie_title, m.genre, m.language, m.rating;

COMMIT;
