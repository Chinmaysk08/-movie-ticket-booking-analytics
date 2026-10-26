import csv
import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "bookings_raw.csv"
CLEAN = ROOT / "data" / "clean" / "bookings_clean.csv"
LOG = ROOT / "reports" / "cleaning_log.txt"
LOG.parent.mkdir(parents=True, exist_ok=True)

CITY_CLEAN = {"Bangalore":"Bengaluru", "Banglore":"Bengaluru", "bengaluru":"Bengaluru", "bangalore":"Bengaluru"}
VALID_TIMES = ["09:00", "12:15", "15:30", "18:45", "21:30", "23:45"]
VALID_FORMATS = {"2D","3D","IMAX"}
VALID_STATUS = {"Confirmed","Cancelled"}
VALID_CHANNEL = {"Website","Mobile App","Kiosk","Third-Party"}
VALID_PAYMENT = {"UPI","Credit Card","Debit Card","NetBanking","Wallet"}

log = []
def L(msg):
    log.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")
    print(msg)

L(f"Reading {RAW}")
with open(RAW, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    rows = list(reader)

orig = len(rows)
L(f"Original rows: {orig}")

# Drop exact duplicates by booking_id keeping first
seen = set()
deduped = []
dups = 0
for r in rows:
    bid = r.get('booking_id')
    if bid in seen:
        dups += 1
        continue
    seen.add(bid)
    deduped.append(r)
rows = deduped
L(f"Removed duplicates: {dups}. Rows now: {len(rows)}")

cleaned = []
null_fixed = 0
for r in rows:
    nr = dict(r)
    # clean city
    c = (nr.get('city') or '').strip()
    nr['city'] = CITY_CLEAN.get(c, CITY_CLEAN.get(c.lower(), c))
    
    # clean email/phone
    if not nr.get('customer_email') or nr['customer_email'].strip() == '':
        nr['customer_email'] = f"{nr['booking_id'].lower()}@example.com"
        null_fixed += 1
    if not nr.get('phone') or str(nr['phone']).strip() == '':
        nr['phone'] = '0000000000'
        null_fixed += 1
    if not nr.get('age_group') or str(nr['age_group']).strip() == '':
        nr['age_group'] = '25-34'
        null_fixed += 1
    if not nr.get('promo_code') or str(nr['promo_code']).strip() == '':
        nr['promo_code'] = 'NONE'
        null_fixed += 1
    
    # numeric
    try:
        nr['age'] = int(float(nr['age']))
    except:
        nr['age'] = 25
    try:
        nr['seats'] = int(float(nr['seats']))
    except:
        nr['seats'] = 1
    try:
        nr['ticket_price'] = int(float(nr['ticket_price']))
    except:
        nr['ticket_price'] = 200
    try:
        nr['convenience_fee'] = int(float(nr['convenience_fee']))
    except:
        nr['convenience_fee'] = 30
    try:
        nr['discount_amount'] = int(float(nr['discount_amount']))
    except:
        nr['discount_amount'] = 0
    try:
        nr['total_amount'] = int(float(nr['total_amount']))
    except:
        nr['total_amount'] = 0
    
    # fix bad values
    if nr['ticket_price'] <= 0:
        nr['ticket_price'] = 200
    if nr['seats'] < 1:
        nr['seats'] = 1
    if nr['seats'] > 10:
        nr['seats'] = 6
    if nr['age'] < 16 or nr['age'] > 80:
        nr['age'] = 25
    if nr['show_time'] not in VALID_TIMES:
        nr['show_time'] = '18:45'
    if nr['format'] not in VALID_FORMATS:
        nr['format'] = '2D'
    if nr['booking_status'] not in VALID_STATUS:
        nr['booking_status'] = 'Confirmed'
    if nr['booking_channel'] not in VALID_CHANNEL:
        nr['booking_channel'] = 'Website'
    if nr['payment_method'] not in VALID_PAYMENT:
        nr['payment_method'] = 'UPI'
    
    # recompute total
    nr['total_amount'] = (nr['ticket_price'] * nr['seats']) + nr['convenience_fee'] - nr['discount_amount']
    if nr['total_amount'] < 0:
        nr['total_amount'] = (nr['ticket_price'] * nr['seats']) + nr['convenience_fee']
    
    # dates
    try:
        datetime.strptime(nr['show_date'], '%Y-%m-%d')
    except:
        nr['show_date'] = '2026-01-01'
    try:
        datetime.strptime(nr['booking_datetime'], '%Y-%m-%d %H:%M:%S')
    except:
        nr['booking_datetime'] = '2026-01-01 12:00:00'
    
    cleaned.append(nr)

L(f"Nulls/empty fixed: {null_fixed}")
L(f"Clean rows: {len(cleaned)}")

# Write clean
fieldnames = list(cleaned[0].keys())
with open(CLEAN, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(cleaned)

L(f"Wrote clean CSV to {CLEAN}")

# Summary
from collections import Counter
cities = Counter(r['city'] for r in cleaned)
L(f"Top cities: {cities.most_common(5)}")
revenue = sum(int(r['total_amount']) for r in cleaned if r['booking_status']=='Confirmed')
L(f"Confirmed revenue: INR {revenue:,}")

with open(LOG, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log) + '\n')

L(f"Log written to {LOG}")
