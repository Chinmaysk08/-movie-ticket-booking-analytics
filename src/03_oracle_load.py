import csv
from pathlib import Path
from datetime import datetime
from db import get_conn

ROOT = Path(__file__).resolve().parents[1]
CLEAN = ROOT / "data" / "clean" / "bookings_clean.csv"

con = get_conn()
cur = con.cursor()

print("Loading data from", CLEAN)
with open(CLEAN, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

# dim_customer
customers = {}
for r in rows:
    key = (r['customer_name'], r['customer_email'], r['phone'])
    if key not in customers:
        customers[key] = r
print(f"Unique customers: {len(customers)}")

cust_sql = """INSERT INTO dim_customer (customer_id, customer_name, customer_email, phone, age, age_group, gender, city)
              VALUES (:1,:2,:3,:4,:5,:6,:7,:8)"""
cust_data = [(r['booking_id'], r['customer_name'], r['customer_email'], r['phone'],
              int(r['age']), r['age_group'], r['gender'], r['city']) for r in customers.values()]
cur.executemany(cust_sql, cust_data)
print("Inserted dim_customer:", cur.rowcount)

# dim_movie
movies = {}
for r in rows:
    key = (r['movie_title'], r['genre'], r['language'])
    if key not in movies:
        movies[key] = r
movie_sql = "INSERT INTO dim_movie (movie_title, genre, language) VALUES (:1,:2,:3)"
movie_data = [(r['movie_title'], r['genre'], r['language']) for r in movies.values()]
cur.executemany(movie_sql, movie_data)
print("Inserted dim_movie:", cur.rowcount)

# dim_show
shows = {}
for r in rows:
    key = (r['screen'], r['format'], r['show_date'], r['show_time'])
    if key not in shows:
        try:
            sd = datetime.strptime(r['show_date'], '%Y-%m-%d')
            sdt = datetime.strptime(f"{r['show_date']} {r['show_time']}", '%Y-%m-%d %H:%M')
        except:
            sd = datetime(2026,1,1)
            sdt = datetime(2026,1,1)
        shows[key] = (r['screen'], r['format'], sd, r['show_time'], sdt)
show_sql = "INSERT INTO dim_show (screen, format, show_date, show_time, show_datetime) VALUES (:1,:2,:3,:4,:5)"
show_data = list(shows.values())
cur.executemany(show_sql, show_data)
print("Inserted dim_show:", cur.rowcount)

# dim_date
dates = {}
for r in rows:
    try:
        d = datetime.strptime(r['show_date'], '%Y-%m-%d')
        dk = int(d.strftime('%Y%m%d'))
        dates[dk] = (dk, d, d.strftime('%A'), d.strftime('%A')[:3], d.month, d.strftime('%B')[:3], ((d.month-1)//3)+1, d.year, 'Y' if d.weekday()>=5 else 'N')
    except:
        pass
date_sql = "INSERT INTO dim_date (date_key, full_date, day_of_week, day_name, month, month_name, quarter, year, is_weekend) VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9)"
date_data = list(dates.values())
cur.executemany(date_sql, date_data)
print("Inserted dim_date:", cur.rowcount)

# dim_payment
payments = {}
for r in rows:
    key = (r['payment_method'], r['booking_channel'])
    if key not in payments:
        payments[key] = r
pay_sql = "INSERT INTO dim_payment (payment_method, booking_channel) VALUES (:1,:2)"
pay_data = [(r['payment_method'], r['booking_channel']) for r in payments.values()]
cur.executemany(pay_sql, pay_data)
print("Inserted dim_payment:", cur.rowcount)

con.commit()

# Build lookup maps
cur.execute("SELECT customer_key, customer_name, customer_email, phone FROM dim_customer")
cust_map = {(n,e,p): k for k,n,e,p in cur.fetchall()}
cur.execute("SELECT movie_key, movie_title, genre, language FROM dim_movie")
movie_map = {(t,g,l): k for k,t,g,l in cur.fetchall()}
cur.execute("SELECT show_key, screen, format, show_date, show_time FROM dim_show")
show_map = {(s,f,sd.strftime('%Y-%m-%d') if sd else None,st): k for k,s,f,sd,st in cur.fetchall()}
cur.execute("SELECT date_key, TO_CHAR(full_date,'YYYY-MM-DD') FROM dim_date")
date_map = {(d,): k for k,d in cur.fetchall()}
cur.execute("SELECT payment_key, payment_method, booking_channel FROM dim_payment")
pay_map = {(pm,bc): k for k,pm,bc in cur.fetchall()}

fact_sql = """INSERT INTO fact_bookings (booking_id, customer_key, movie_key, show_key, date_key, payment_key,
                                          seats, ticket_price, convenience_fee, discount_amount, total_amount,
                                          promo_code, booking_status, booking_datetime)
              VALUES (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14)"""

fact_data = []
for r in rows:
    try:
        ck = cust_map.get((r['customer_name'], r['customer_email'], r['phone']))
        mk = movie_map.get((r['movie_title'], r['genre'], r['language']))
        sk = show_map.get((r['screen'], r['format'], r['show_date'], r['show_time']))
        dk = date_map.get((r['show_date'],))
        pk = pay_map.get((r['payment_method'], r['booking_channel']))
        bdt = datetime.strptime(r['booking_datetime'], '%Y-%m-%d %H:%M:%S')
        fact_data.append((r['booking_id'], ck, mk, sk, dk, pk,
                          int(r['seats']), int(r['ticket_price']), int(r['convenience_fee']),
                          int(r['discount_amount']), int(r['total_amount']),
                          r['promo_code'], r['booking_status'], bdt))
    except Exception as e:
        pass

cur.executemany(fact_sql, fact_data)
con.commit()
print("Inserted fact_bookings:", len(fact_data))

cur.execute("SELECT COUNT(*) FROM fact_bookings")
print("Fact count:", cur.fetchone()[0])
cur.execute("SELECT SUM(total_amount) FROM fact_bookings WHERE booking_status='Confirmed'")
print("Confirmed revenue:", cur.fetchone()[0])

con.close()
print("Done")
