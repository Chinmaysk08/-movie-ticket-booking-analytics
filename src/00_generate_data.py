"""
00_generate_data.py -- Movie Ticket Booking Analytics, dataset v2
=================================================================

WHAT THIS SCRIPT DOES
---------------------
1. Builds a small fictional cinema business that is internally consistent:
      - 8 Indian cities
      - 16 multiplexes (2 per city), 5 screens each
      - 22 fictional movies (Hindi / Tamil / Telugu)
      - 3,200 registered customers
2. Simulates shows, then books seats show-by-show. This matters because
   occupancy can only be honest if we know how many seats the screen has
   and how many were actually sold for that specific show.
3. Injects realistic data-quality defects (duplicate rows, missing values,
   impossible prices / times / dates / ages) for the cleaning phase to find
   and fix. The defects are deliberate and documented.
4. Writes:
      data/raw/bookings_raw.csv          <- 10,300 rows (10,000 + 300 duplicates)
      reports/generation_summary.json    <- facts used to validate later steps

REPRODUCIBILITY
---------------
Everything uses random.seed(42). Re-running the script produces byte-identical
output on the same Python version.

IMPORTANT
---------
All data is SYNTHETIC. Movie titles, theatre names and customers are invented.
Nothing here describes real box-office performance, real cinemas or real people.

Run with:
    $env:PYTHONPATH = "D:\\chinmay\\movie-ticket-booking-analytics\\src"
    D:\\venvs\\cinema\\Scripts\\python.exe src\\00_generate_data.py
"""

import csv
import json
import random
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# 0. Paths and global settings
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
REPORTS_DIR = ROOT / "reports"
RAW_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

OUT_CSV = RAW_DIR / "bookings_raw.csv"
OUT_SUMMARY = REPORTS_DIR / "generation_summary.json"

SEED = 42
random.seed(SEED)

N_BOOKINGS = 10_000          # clean booking records we want
N_DUPLICATES = 300           # extra exact-duplicate rows appended to the raw file
N_CUSTOMERS = 4_200          # registered customer pool
N_SHOWS = 290                # shows to simulate (trimmed to N_BOOKINGS afterwards)
DATE_START = date(2025, 10, 1)
DATE_END = date(2026, 9, 30)  # one full year, all in the past

# ---------------------------------------------------------------------------
# 1. Cities and theatres
# ---------------------------------------------------------------------------
# Weights roughly follow the relative size of the multiplex market in each city.
# Unlike v1, Bengaluru is ONE city with ONE weight. Label variants are injected
# later as a data-quality issue, not as separate cities.
CITY_WEIGHTS = {
    "Mumbai": 0.20,
    "Delhi": 0.18,
    "Bengaluru": 0.15,
    "Hyderabad": 0.12,
    "Chennai": 0.10,
    "Pune": 0.09,
    "Kolkata": 0.08,
    "Ahmedabad": 0.08,
}
CITIES = list(CITY_WEIGHTS)
CITY_W = list(CITY_WEIGHTS.values())

# Fictional multiplex names so nobody mistakes this for real cinema data.
THEATRE_NAMES = {
    "Mumbai": ["Skyline Multiplex - Andheri", "Metro Cinema - Lower Parel"],
    "Delhi": ["Capital Screens - Saket", "Regal Multiplex - Dwarka"],
    "Bengaluru": ["Orion Cinemas - Koramangala", "CineVerse - Whitefield"],
    "Hyderabad": ["Deccan Talkies - Banjara Hills", "Nova Screens - Gachibowli"],
    "Chennai": ["Marina Movies - Velachery", "Anand Cinema - T. Nagar"],
    "Pune": ["Deccan Mall Cinemas - Baner", "Sunset Screens - Kothrud"],
    "Kolkata": ["Bengal Cinema - Salt Lake", "Riverside Multiplex - Howrah"],
    "Ahmedabad": ["Sabarmati Screens - SG Highway", "Heritage Cinema - Navrangpura"],
}

# Each multiplex has the same five-screen layout. Capacity ranges are realistic
# for Indian multiplex auditoriums (small 2D screen up to a large IMAX screen).
SCREEN_TEMPLATES = [
    ("Screen 1", "IMAX", (280, 340)),
    ("Screen 2", "3D", (180, 240)),
    ("Screen 3", "2D", (140, 200)),
    ("Screen 4", "2D", (120, 180)),
    ("Screen 5", "2D", (100, 160)),
]

THEATRES = []
for city in CITIES:
    for name in THEATRE_NAMES[city]:
        screens = []
        for screen_name, screen_format, (low, high) in SCREEN_TEMPLATES:
            capacity = random.randrange(low, high + 1, 10)  # multiples of 10
            screens.append(
                {"screen": screen_name, "format": screen_format, "capacity": capacity}
            )
        THEATRES.append({"name": name, "city": city, "screens": screens})

THEATRES_BY_CITY = defaultdict(list)
for theatre in THEATRES:
    THEATRES_BY_CITY[theatre["city"]].append(theatre)

# ---------------------------------------------------------------------------
# 2. Movies
# ---------------------------------------------------------------------------
# popularity is a relative demand multiplier used when choosing which movie
# plays on a show. rating is a critic/user score out of 10.
MOVIES = [
    # Hindi
    {"title": "Dilli Nights", "genre": "Thriller", "language": "Hindi",
     "rating": 8.1, "release": date(2025, 6, 20), "popularity": 1.15},
    {"title": "Rangmanch", "genre": "Drama", "language": "Hindi",
     "rating": 7.4, "release": date(2025, 8, 15), "popularity": 0.95},
    {"title": "Chandni Chowk Express", "genre": "Comedy", "language": "Hindi",
     "rating": 6.9, "release": date(2025, 9, 5), "popularity": 1.05},
    {"title": "Mehfil", "genre": "Romance", "language": "Hindi",
     "rating": 7.2, "release": date(2025, 11, 14), "popularity": 0.90},
    {"title": "Aakhri Raasta", "genre": "Action", "language": "Hindi",
     "rating": 7.8, "release": date(2026, 1, 23), "popularity": 1.25},
    {"title": "Dhoop Chhaon", "genre": "Drama", "language": "Hindi",
     "rating": 8.4, "release": date(2026, 3, 6), "popularity": 1.00},
    {"title": "Shor Macha", "genre": "Comedy", "language": "Hindi",
     "rating": 6.5, "release": date(2026, 6, 12), "popularity": 1.10},
    {"title": "Antariksh 2050", "genre": "Sci-Fi", "language": "Hindi",
     "rating": 7.5, "release": date(2026, 2, 6), "popularity": 1.05},
    # Tamil
    {"title": "Kanaka", "genre": "Action", "language": "Tamil",
     "rating": 7.2, "release": date(2025, 2, 21), "popularity": 1.00},
    {"title": "Vaanam", "genre": "Drama", "language": "Tamil",
     "rating": 8.0, "release": date(2025, 5, 30), "popularity": 0.95},
    {"title": "Kadal Nilavu", "genre": "Romance", "language": "Tamil",
     "rating": 7.1, "release": date(2025, 9, 19), "popularity": 0.85},
    {"title": "Pei Veedu", "genre": "Horror-Comedy", "language": "Tamil",
     "rating": 6.8, "release": date(2025, 10, 31), "popularity": 0.95},
    {"title": "Neruppu", "genre": "Action", "language": "Tamil",
     "rating": 8.2, "release": date(2025, 12, 12), "popularity": 1.20},
    {"title": "Thiruvizha", "genre": "Comedy", "language": "Tamil",
     "rating": 7.0, "release": date(2026, 1, 15), "popularity": 0.95},
    {"title": "Iravu Payanam", "genre": "Thriller", "language": "Tamil",
     "rating": 7.9, "release": date(2026, 4, 10), "popularity": 1.05},
    {"title": "Sivappu Manjal", "genre": "Drama", "language": "Tamil",
     "rating": 8.3, "release": date(2026, 7, 3), "popularity": 0.90},
    # Telugu
    {"title": "Manikya", "genre": "Drama", "language": "Telugu",
     "rating": 7.0, "release": date(2025, 3, 14), "popularity": 0.90},
    {"title": "Golconda", "genre": "Historical", "language": "Telugu",
     "rating": 8.1, "release": date(2025, 7, 11), "popularity": 1.10},
    {"title": "Vennela", "genre": "Romance", "language": "Telugu",
     "rating": 7.3, "release": date(2025, 10, 24), "popularity": 0.90},
    {"title": "Raktham", "genre": "Action", "language": "Telugu",
     "rating": 8.0, "release": date(2026, 2, 20), "popularity": 1.20},
    {"title": "Bhramaram", "genre": "Thriller", "language": "Telugu",
     "rating": 7.6, "release": date(2026, 5, 8), "popularity": 1.00},
    {"title": "Suryodayam", "genre": "Drama", "language": "Telugu",
     "rating": 7.8, "release": date(2026, 8, 14), "popularity": 0.95},
    # Recent Blockbusters
    {"title": "KGF Chapter 2", "genre": "Action", "language": "Kannada",
     "rating": 8.4, "release": date(2026, 4, 14), "popularity": 1.35},
    {"title": "Pushpa 2: The Rule", "genre": "Action", "language": "Telugu",
     "rating": 8.6, "release": date(2026, 5, 1), "popularity": 1.40},
    {"title": "War 2", "genre": "Action", "language": "Hindi",
     "rating": 8.2, "release": date(2026, 6, 20), "popularity": 1.30},
    {"title": "Animal", "genre": "Action", "language": "Hindi",
     "rating": 8.3, "release": date(2026, 7, 5), "popularity": 1.25},
]

# Language demand differs by city. These weights make the data more realistic
# and let us analyse language preferences by city later.
CITY_LANGUAGE_WEIGHTS = {
    "Mumbai": {"Hindi": 0.65, "Tamil": 0.15, "Telugu": 0.12, "Kannada": 0.08},
    "Delhi": {"Hindi": 0.70, "Tamil": 0.12, "Telugu": 0.10, "Kannada": 0.08},
    "Bengaluru": {"Hindi": 0.25, "Tamil": 0.25, "Telugu": 0.20, "Kannada": 0.30},
    "Hyderabad": {"Hindi": 0.18, "Tamil": 0.18, "Telugu": 0.52, "Kannada": 0.12},
    "Chennai": {"Hindi": 0.14, "Tamil": 0.65, "Telugu": 0.12, "Kannada": 0.09},
    "Pune": {"Hindi": 0.65, "Tamil": 0.15, "Telugu": 0.12, "Kannada": 0.08},
    "Kolkata": {"Hindi": 0.70, "Tamil": 0.12, "Telugu": 0.10, "Kannada": 0.08},
    "Ahmedabad": {"Hindi": 0.76, "Tamil": 0.10, "Telugu": 0.08, "Kannada": 0.06},
}

# ---------------------------------------------------------------------------
# 3. Show slots and pricing
# ---------------------------------------------------------------------------
SHOW_SLOTS = ["09:00", "12:15", "15:30", "18:45", "21:30", "23:45"]
SLOT_WEIGHTS = [0.10, 0.15, 0.18, 0.28, 0.22, 0.07]

# Multipliers applied to the base occupancy of 40%.
SLOT_OCC_MULT = {
    "09:00": 0.45, "12:15": 0.65, "15:30": 0.80,
    "18:45": 1.25, "21:30": 1.30, "23:45": 0.50,
}
SLOT_PREMIUM = {
    "09:00": 0, "12:15": 0, "15:30": 20,
    "18:45": 60, "21:30": 50, "23:45": 0,
}
FORMAT_OCC_MULT = {"2D": 1.00, "3D": 1.05, "IMAX": 1.15}

BASE_PRICE = {"2D": 220, "3D": 300, "IMAX": 480}
CITY_PRICE_MULT = {
    "Mumbai": 1.15, "Delhi": 1.10, "Bengaluru": 1.10, "Hyderabad": 1.00,
    "Chennai": 1.00, "Pune": 0.95, "Kolkata": 0.90, "Ahmedabad": 0.85,
}

TICKET_TYPES = ["Standard", "Premium", "Recliner"]
TICKET_TYPE_WEIGHTS = [0.60, 0.30, 0.10]
TICKET_TYPE_MULT = {"Standard": 1.0, "Premium": 1.4, "Recliner": 2.2}

SEAT_COUNTS = [1, 2, 3, 4, 5, 6]
SEAT_WEIGHTS = [0.25, 0.35, 0.20, 0.12, 0.05, 0.03]

PROMOS = ["NONE", "WEEKEND10", "STUDENT15", "FIRSTBUY5", "FAMILY20"]
PROMO_WEIGHTS = [0.70, 0.10, 0.07, 0.08, 0.05]
PROMO_RATES = {
    "NONE": 0.00, "WEEKEND10": 0.10, "STUDENT15": 0.15,
    "FIRSTBUY5": 0.05, "FAMILY20": 0.20,
}

PAYMENTS = ["UPI", "Credit Card", "Debit Card", "NetBanking", "Wallet"]
PAYMENT_WEIGHTS = [0.45, 0.20, 0.15, 0.10, 0.10]
CHANNELS = ["Website", "Mobile App", "Kiosk", "Third-Party"]
CHANNEL_WEIGHTS = [0.30, 0.45, 0.10, 0.15]
CHANNEL_CANCEL = {
    "Website": 0.07, "Mobile App": 0.06, "Kiosk": 0.09, "Third-Party": 0.13,
}

# Month seasonality: festivals and school holidays lift cinema demand.
MONTH_WEIGHT = {
    1: 0.95, 2: 0.90, 3: 1.00, 4: 1.10, 5: 1.15, 6: 1.05,
    7: 0.95, 8: 1.00, 9: 0.90, 10: 1.00, 11: 1.15, 12: 1.25,
}
# Fuller halls in the same months, not just more shows.
MONTH_OCC_MULT = {
    1: 0.95, 2: 0.92, 3: 1.00, 4: 1.06, 5: 1.10, 6: 1.04,
    7: 0.96, 8: 1.00, 9: 0.92, 10: 1.00, 11: 1.08, 12: 1.12,
}

# ---------------------------------------------------------------------------
# 4. Customer names (invented combinations)
# ---------------------------------------------------------------------------
FIRST_MALE = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Rohan", "Karan", "Rahul", "Vikram",
    "Siddharth", "Ankit", "Harsh", "Manish", "Nikhil", "Pranav", "Rajesh",
    "Sanjay", "Suresh", "Amit", "Gaurav", "Kunal", "Varun", "Yash", "Dev",
    "Ishaan", "Kabir", "Aryan", "Om", "Neel", "Rishi", "Tanmay",
]
FIRST_FEMALE = [
    "Aadhya", "Ananya", "Diya", "Ishita", "Kavya", "Meera", "Nisha", "Pooja",
    "Priya", "Riya", "Saanvi", "Shreya", "Sneha", "Tanvi", "Trisha",
    "Vaishnavi", "Zara", "Aishwarya", "Divya", "Fatima", "Gayatri", "Ira",
    "Jiya", "Khushi", "Lakshmi", "Myra", "Nandini", "Pari", "Rhea", "Sanya",
]
FIRST_NEUTRAL = ["Kiran", "Anmol", "Jyoti", "Dev", "Arya", "Sai", "Krishna"]
LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Agarwal", "Singh", "Yadav", "Kumar", "Reddy",
    "Rao", "Naidu", "Iyer", "Menon", "Nair", "Pillai", "Krishnan",
    "Subramanian", "Chatterjee", "Banerjee", "Mukherjee", "Das", "Bose",
    "Ghosh", "Patel", "Shah", "Mehta", "Desai", "Joshi", "Kulkarni",
    "Deshmukh", "Pawar", "Khan", "Ali", "Sheikh", "Ansari", "Qureshi",
    "Fernandes", "D'Souza", "Pereira", "Thomas", "Mathew", "George",
    "Varghese", "Jain", "Sethi", "Malhotra", "Kapoor", "Chopra", "Bansal",
    "Arora", "Bhatia", "Saxena", "Mishra", "Tiwari", "Pandey", "Dubey",
    "Trivedi", "Chauhan", "Rathore", "Thakur", "Nambiar", "Hegde", "Shetty",
    "Kamath", "Pai", "Bhat", "Gowda", "Naik", "Jadhav", "Shinde", "Patil",
    "More", "Chavan", "Kadam", "Bhandari", "Rana", "Rawat", "Bisht", "Negi",
    "Sengupta", "Dutta", "Roy", "Saha", "Mondal", "Islam", "Hossain",
]

AGE_BUCKETS = [
    (18, 24, 0.22), (25, 34, 0.32), (35, 44, 0.22),
    (45, 54, 0.15), (55, 68, 0.09),
]


# ---------------------------------------------------------------------------
# 5. Helper functions
# ---------------------------------------------------------------------------
def age_group(age: int) -> str:
    """Convert a numeric age into the reporting band used everywhere."""
    if age < 25:
        return "18-24"
    if age < 35:
        return "25-34"
    if age < 45:
        return "35-44"
    if age < 55:
        return "45-54"
    return "55+"


def random_age() -> int:
    low, high, weight = random.choices(AGE_BUCKETS, weights=[b[2] for b in AGE_BUCKETS])[0]
    return random.randint(low, high)


def build_customers() -> list:
    """Create the registered customer pool, split across cities."""
    customers = []
    used_names = set()
    used_phones = set()
    customer_number = 0

    for city in CITIES:
        n_for_city = round(N_CUSTOMERS * CITY_WEIGHTS[city])
        for _ in range(n_for_city):
            customer_number += 1
            gender = random.choices(
                ["Male", "Female", "Other"], weights=[0.48, 0.48, 0.04]
            )[0]

            if gender == "Male":
                first_pool = FIRST_MALE
            elif gender == "Female":
                first_pool = FIRST_FEMALE
            else:
                first_pool = FIRST_NEUTRAL

            first = random.choice(first_pool)
            last = random.choice(LAST_NAMES)
            name = f"{first} {last}"

            # Keep display names unique so joins on name are not ambiguous.
            attempts = 0
            while name in used_names:
                attempts += 1
                if attempts > 30:
                    name = f"{first} {last} {chr(65 + random.randint(0, 25))}."
                    break
                first = random.choice(first_pool)
                last = random.choice(LAST_NAMES)
                name = f"{first} {last}"
            used_names.add(name)

            while True:
                phone = random.choice("6789") + "".join(
                    str(random.randint(0, 9)) for _ in range(9)
                )
                if phone not in used_phones:
                    used_phones.add(phone)
                    break

            email_local = f"{first}.{last}{customer_number}".lower()
            email_local = email_local.replace(" ", "").replace("'", "")
            email = f"{email_local}@example.com"

            customers.append(
                {
                    "customer_id": f"CUS{customer_number:05d}",
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "age": random_age(),
                    "gender": gender,
                    "city": city,
                    # Heavy-tailed weight: most customers book a few times,
                    # a small group books often. This makes loyalty analysis
                    # meaningful instead of every customer booking exactly once.
                    "weight": min(random.paretovariate(1.6), 12.0),
                }
            )

    return customers


def recency_boost(movie: dict, show_date: date) -> float:
    """
    New releases take a larger share of screens in their opening weeks.

    Real multiplexes give a fresh blockbuster most of the prime slots for
    roughly six weeks, then rotate it down as the next release arrives. Without
    this, a film that releases late in the year only has a few show slots left
    and looks artificially unpopular.
    """
    days_since_release = (show_date - movie["release"]).days
    if days_since_release <= 14:
        return 5.0
    if days_since_release <= 45:
        return 3.0
    if days_since_release <= 90:
        return 1.6
    return 1.0


def choose_movie(city: str, show_date: date) -> dict:
    """Pick a movie that has already released and suits the city's languages."""
    eligible = [m for m in MOVIES if m["release"] <= show_date]
    language_weights = CITY_LANGUAGE_WEIGHTS[city]
    weights = [
        language_weights[m["language"]]
        * m["popularity"]
        * recency_boost(m, show_date)
        for m in eligible
    ]
    return random.choices(eligible, weights=weights, k=1)[0]


def build_months() -> list:
    """List (year, month) pairs covering the dataset period."""
    months = []
    year, month = DATE_START.year, DATE_START.month
    while (year, month) <= (DATE_END.year, DATE_END.month):
        months.append((year, month))
        month += 1
        if month == 13:
            month = 1
            year += 1
    return months


MONTHS = build_months()
MONTH_W = [MONTH_WEIGHT[m] for _, m in MONTHS]


def build_cells() -> list:
    """
    Split the shows across city x month cells.

    Without this, a random sample of only ~280 shows produces large accidental
    swings (one month could get twice as many shows as another). Stratifying
    keeps the designed seasonality and city weights visible, which makes the
    later analysis explainable instead of noisy.
    """
    cells = []
    for city in CITIES:
        for year, month in MONTHS:
            cells.append(
                {
                    "city": city,
                    "year": year,
                    "month": month,
                    "weight": CITY_WEIGHTS[city] * MONTH_WEIGHT[month],
                }
            )

    # Give every city at least one show per month, then distribute the rest
    # in proportion to city size x seasonal demand.
    total_weight = sum(cell["weight"] for cell in cells)
    remaining = N_SHOWS - len(cells)
    raw_share = [remaining * cell["weight"] / total_weight for cell in cells]
    allocation = [1 + int(share) for share in raw_share]

    leftover = N_SHOWS - sum(allocation)
    order = sorted(
        range(len(cells)),
        key=lambda i: raw_share[i] - int(raw_share[i]),
        reverse=True,
    )
    for index in order[:leftover]:
        allocation[index] += 1

    for cell, shows in zip(cells, allocation):
        cell["shows"] = shows
    return cells


def random_date_in_month(year: int, month: int) -> date:
    """Pick a random calendar day inside one month."""
    if month == 12:
        next_month = date(year + 1, 1, 1)
    else:
        next_month = date(year, month + 1, 1)
    days_in_month = (next_month - date(year, month, 1)).days
    return date(year, month, random.randint(1, days_in_month))


def make_show(show_number: int, city: str, year: int, month: int, used_slots: set) -> dict:
    """Create one show with a target occupancy based on slot/day/movie/screen."""
    while True:
        theatre = random.choice(THEATRES_BY_CITY[city])
        screen = random.choice(theatre["screens"])
        show_date = random_date_in_month(year, month)
        show_time = random.choices(SHOW_SLOTS, weights=SLOT_WEIGHTS, k=1)[0]

        # A physical screen cannot run two shows at the same date and time.
        slot_key = (theatre["name"], screen["screen"], show_date, show_time)
        if slot_key not in used_slots:
            used_slots.add(slot_key)
            break

    movie = choose_movie(city, show_date)

    is_weekend = show_date.weekday() >= 5
    occupancy = (
        0.40
        * SLOT_OCC_MULT[show_time]
        * (1.30 if is_weekend else 1.00)
        * (0.85 + 0.15 * movie["popularity"])
        * FORMAT_OCC_MULT[screen["format"]]
        * MONTH_OCC_MULT[month]
        * random.lognormvariate(0, 0.35)
    )
    occupancy = min(max(occupancy, 0.06), 0.97)

    return {
        "show_id": f"SH{show_number:06d}",
        "city": city,
        "theatre_name": theatre["name"],
        "screen": screen["screen"],
        "format": screen["format"],
        "seats_capacity": screen["capacity"],
        "movie_title": movie["title"],
        "genre": movie["genre"],
        "language": movie["language"],
        "rating": movie["rating"],
        "show_date": show_date,
        "show_time": show_time,
        "occupancy_target": occupancy,
    }


def make_booking(show: dict, seats: int) -> dict:
    """Create one booking for a given show and seat count."""
    show_time_obj = datetime.strptime(show["show_time"], "%H:%M").time()
    show_dt = datetime.combine(show["show_date"], show_time_obj)

    ticket_type = random.choices(
        TICKET_TYPES, weights=TICKET_TYPE_WEIGHTS, k=1
    )[0]

    is_weekend = show["show_date"].weekday() >= 5
    price = (
        BASE_PRICE[show["format"]] * CITY_PRICE_MULT[show["city"]]
        + SLOT_PREMIUM[show["show_time"]]
        + (40 if is_weekend else 0)
    ) * TICKET_TYPE_MULT[ticket_type]
    price *= random.uniform(0.92, 1.08)
    price = max(120, int(round(price / 5) * 5))

    convenience_fee = random.randint(20, 45)
    promo = random.choices(PROMOS, weights=PROMO_WEIGHTS, k=1)[0]
    discount = int(round(price * seats * PROMO_RATES[promo]))
    total_amount = price * seats + convenience_fee - discount

    channel = random.choices(CHANNELS, weights=CHANNEL_WEIGHTS, k=1)[0]
    if channel == "Kiosk":
        payment = random.choices(
            ["Credit Card", "Debit Card", "UPI"], weights=[0.45, 0.35, 0.20], k=1
        )[0]
    else:
        payment = random.choices(PAYMENTS, weights=PAYMENT_WEIGHTS, k=1)[0]

    # How far in advance was the booking made?
    roll = random.random()
    if roll < 0.40:                       # same day
        lead_time = timedelta(hours=random.uniform(2, 10))
    elif roll < 0.65:                     # one day before
        lead_time = timedelta(days=1, hours=random.uniform(0, 12))
    elif roll < 0.85:                     # 2-7 days before
        lead_time = timedelta(days=random.randint(2, 7), hours=random.uniform(0, 24))
    else:                                 # 8-30 days before
        lead_time = timedelta(days=random.randint(8, 30), hours=random.uniform(0, 24))

    booking_dt = (show_dt - lead_time).replace(microsecond=0)
    days_ahead = (show_dt.date() - booking_dt.date()).days

    cancel_probability = CHANNEL_CANCEL[channel]
    if days_ahead >= 14:
        cancel_probability += 0.04
    elif days_ahead <= 1:
        cancel_probability -= 0.02
    status = "Cancelled" if random.random() < cancel_probability else "Confirmed"

    return {
        "booking_id": None,           # assigned after sorting by booking time
        "customer_id": None,          # filled after all bookings exist
        "customer_name": None,
        "customer_email": None,
        "phone": None,
        "age": None,
        "age_group": None,
        "gender": None,
        "city": show["city"],
        "theatre_name": show["theatre_name"],
        "screen": show["screen"],
        "seats_capacity": show["seats_capacity"],
        "movie_title": show["movie_title"],
        "genre": show["genre"],
        "language": show["language"],
        "rating": show["rating"],
        "format": show["format"],
        "show_id": show["show_id"],
        "show_date": show["show_date"].strftime("%Y-%m-%d"),
        "show_time": show["show_time"],
        "ticket_type": ticket_type,
        "seats": seats,
        "ticket_price": price,
        "convenience_fee": convenience_fee,
        "promo_code": promo,
        "discount_amount": discount,
        "total_amount": total_amount,
        "payment_method": payment,
        "booking_channel": channel,
        "booking_status": status,
        "booking_datetime": booking_dt.strftime("%Y-%m-%d %H:%M:%S"),
    }


def weighted_sample_without_replacement(items: list, weights: list, k: int) -> list:
    """
    Pick k items without replacement, respecting weights.

    Uses the Efraimidis-Spirakis method: each item gets a random key
    u ** (1 / weight); the k largest keys win. This is useful because
    random.choices() samples WITH replacement, which could put the same
    customer on the same show twice.
    """
    if k >= len(items):
        return list(items)
    keyed = [(random.random() ** (1.0 / w), item) for item, w in zip(items, weights)]
    keyed.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in keyed[:k]]


def generate_bookings(customers: list) -> list:
    """Generate shows and fill them with bookings, then trim to N_BOOKINGS."""
    customers_by_city = defaultdict(list)
    for customer in customers:
        customers_by_city[customer["city"]].append(customer)

    bookings = []
    show_number = 0
    used_slots = set()

    for cell in build_cells():
        for _ in range(cell["shows"]):
            show_number += 1
            show = make_show(
                show_number, cell["city"], cell["year"], cell["month"], used_slots
            )
            capacity = show["seats_capacity"]
            target_seats = int(round(show["occupancy_target"] * capacity))
            target_seats = max(1, min(target_seats, capacity))

            seats_sold = 0
            while seats_sold < target_seats:
                seats = random.choices(SEAT_COUNTS, weights=SEAT_WEIGHTS, k=1)[0]
                if seats_sold + seats > capacity:
                    seats = capacity - seats_sold
                if seats <= 0:
                    break
                bookings.append(make_booking(show, seats))
                seats_sold += seats

    # The 280 simulated shows produce a little more than 10,000 bookings.
    # Remove the excess at random so no single city or month is distorted.
    if len(bookings) > N_BOOKINGS:
        random.shuffle(bookings)
        bookings = bookings[:N_BOOKINGS]

    # Real transaction logs are usually chronological. Sorting also makes
    # booking_id a stable, meaningful sequence.
    bookings.sort(key=lambda booking: booking["booking_datetime"])
    for number, booking in enumerate(bookings, start=1):
        booking["booking_id"] = f"BK{number:07d}"

    # Assign customers per show, all from the show's city, without repeats
    # within the same show.
    bookings_by_show = defaultdict(list)
    for booking in bookings:
        bookings_by_show[booking["show_id"]].append(booking)

    for show_id, group in bookings_by_show.items():
        city = group[0]["city"]
        pool = customers_by_city[city]
        weights = [c["weight"] for c in pool]
        chosen = weighted_sample_without_replacement(pool, weights, len(group))
        for booking, customer in zip(group, chosen):
            booking["customer_id"] = customer["customer_id"]
            booking["customer_name"] = customer["name"]
            booking["customer_email"] = customer["email"]
            booking["phone"] = customer["phone"]
            booking["age"] = customer["age"]
            booking["age_group"] = age_group(customer["age"])
            booking["gender"] = customer["gender"]

    return bookings


# ---------------------------------------------------------------------------
# 6. Data-quality defects (deliberate, documented, and repairable)
# ---------------------------------------------------------------------------
def inject_defects(bookings: list) -> tuple:
    """
    Turn clean bookings into a realistic raw file.

    Every defect below is designed to be recoverable during cleaning:
      - duplicates        -> drop by booking_id
      - missing email/phone -> copy from the same customer's other booking
      - missing age_group -> re-derive from age
      - missing promo     -> infer from the discount rate
      - bad price         -> recover from total_amount = price*seats + fee - discount
      - bad show_time/date-> use the most common value for the same show_id
      - bad rating        -> use the most common rating for the same movie
      - bad age           -> use the customer's age from another booking
    """
    rows = []
    for booking in bookings:
        row = dict(booking)

        # City label inconsistencies: a real booking system often has several
        # spellings. Bengaluru keeps one canonical weight; the variants are
        # only labels, so cleaning can merge them without changing the share.
        if row["city"] == "Bengaluru" and random.random() < 0.08:
            row["city"] = random.choice(["Bangalore", "Banglore"])
        elif random.random() < 0.015:
            row["city"] = random.choice(
                [row["city"].upper(), f" {row['city']} ", row["city"].lower()]
            )

        rows.append(row)

    show_counts = Counter(r["show_id"] for r in rows)
    customer_counts = Counter(r["customer_id"] for r in rows)
    defects = Counter()

    # --- 6a. Missing values -------------------------------------------------
    def pick_indices(candidates, limit, key=None):
        """Pick up to `limit` indices, at most one per key (if given)."""
        random.shuffle(candidates)
        chosen, seen = [], set()
        for index in candidates:
            if key is not None:
                value = rows[index][key]
                if value in seen:
                    continue
                seen.add(value)
            chosen.append(index)
            if len(chosen) >= limit:
                break
        return chosen

    repeat_customers = [
        i for i, r in enumerate(rows) if customer_counts[r["customer_id"]] >= 2
    ]
    for index in pick_indices(repeat_customers[:], 60, key="customer_id"):
        rows[index]["customer_email"] = ""
        defects["missing_email"] += 1

    for index in pick_indices(repeat_customers[:], 60, key="customer_id"):
        rows[index]["phone"] = ""
        defects["missing_phone"] += 1

    all_indices = list(range(len(rows)))
    for index in pick_indices(all_indices[:], 50):
        rows[index]["age_group"] = ""
        defects["missing_age_group"] += 1

    for index in pick_indices(all_indices[:], 50):
        rows[index]["promo_code"] = ""
        defects["missing_promo_code"] += 1

    # --- 6b. Impossible ticket prices ---------------------------------------
    for index in random.sample(range(len(rows)), 50):
        rows[index]["ticket_price"] = random.choice([0, -50, -100])
        defects["bad_ticket_price"] += 1

    # --- 6c. Impossible show times (one per show, so the mode can repair) ----
    eligible_shows = [i for i, r in enumerate(rows) if show_counts[r["show_id"]] >= 3]
    random.shuffle(eligible_shows)
    used_shows = set()
    for index in eligible_shows:
        show_id = rows[index]["show_id"]
        if show_id in used_shows:
            continue
        used_shows.add(show_id)
        rows[index]["show_time"] = random.choice(["25:30", "99:00", "abc"])
        defects["bad_show_time"] += 1
        if len(used_shows) >= 30:
            break

    # --- 6d. Future / impossible show dates --------------------------------
    random.shuffle(eligible_shows)
    used_shows = set()
    for index in eligible_shows:
        show_id = rows[index]["show_id"]
        if show_id in used_shows:
            continue
        used_shows.add(show_id)
        rows[index]["show_date"] = "2027-12-31"
        defects["bad_show_date"] += 1
        if len(used_shows) >= 20:
            break

    # --- 6e. Out-of-range movie ratings ------------------------------------
    movies_seen = set()
    for index in random.sample(range(len(rows)), len(rows)):
        title = rows[index]["movie_title"]
        if title in movies_seen:
            continue
        movies_seen.add(title)
        rows[index]["rating"] = random.choice([12.5, -1.0])
        defects["bad_rating"] += 1
        if len(movies_seen) >= 10:
            break

    # --- 6f. Impossible ages (recoverable from the customer's other rows) ---
    eligible_ages = [
        i for i, r in enumerate(rows) if customer_counts[r["customer_id"]] >= 2
    ]
    for index in pick_indices(eligible_ages, 10, key="customer_id"):
        rows[index]["age"] = random.choice([150, -5])
        defects["bad_age"] += 1

    # --- 6g. Exact duplicate rows ------------------------------------------
    base_rows = list(rows)
    for _ in range(N_DUPLICATES):
        rows.append(dict(random.choice(base_rows)))
        defects["duplicate_rows"] += 1

    return rows, defects


# ---------------------------------------------------------------------------
# 7. Summary statistics (used to validate every later layer)
# ---------------------------------------------------------------------------
def build_summary(bookings: list, defects: Counter) -> dict:
    confirmed = [b for b in bookings if b["booking_status"] == "Confirmed"]

    show_capacity = {}
    confirmed_seats = defaultdict(int)
    for b in bookings:
        show_capacity[b["show_id"]] = b["seats_capacity"]
        if b["booking_status"] == "Confirmed":
            confirmed_seats[b["show_id"]] += b["seats"]

    total_capacity = sum(show_capacity.values())
    total_confirmed_seats = sum(confirmed_seats.values())

    customer_bookings = Counter(b["customer_id"] for b in bookings)
    customer_types = Counter()
    for cid, count in customer_bookings.items():
        if count == 1:
            customer_types["New"] += 1
        elif count <= 3:
            customer_types["Returning"] += 1
        else:
            customer_types["Loyal"] += 1

    monthly = Counter(b["show_date"][:7] for b in bookings)
    by_city = Counter(b["city"] for b in bookings)
    by_language = Counter(b["language"] for b in bookings)
    by_ticket_type = Counter(b["ticket_type"] for b in bookings)

    return {
        "seed": SEED,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "period": {"start": DATE_START.isoformat(), "end": DATE_END.isoformat()},
        "rows_written_to_raw": len(bookings) + N_DUPLICATES,
        "clean_bookings": len(bookings),
        "unique_booking_ids": len({b["booking_id"] for b in bookings}),
        "unique_customers": len(customer_bookings),
        "unique_shows": len(show_capacity),
        "theatres": len(THEATRES),
        "screens": len(THEATRES) * len(SCREEN_TEMPLATES),
        "movies": len(MOVIES),
        "tickets_confirmed": total_confirmed_seats,
        "revenue_confirmed_inr": sum(b["total_amount"] for b in confirmed),
        "avg_booking_value_inr": round(
            sum(b["total_amount"] for b in confirmed) / len(confirmed), 2
        ),
        "cancellation_rate_pct": round(
            100 * (len(bookings) - len(confirmed)) / len(bookings), 2
        ),
        "aggregate_occupancy_pct": round(100 * total_confirmed_seats / total_capacity, 2),
        "customers_by_type": dict(customer_types),
        "bookings_by_type": {
            "New": sum(1 for b in bookings if customer_bookings[b["customer_id"]] == 1),
            "Returning": sum(
                1 for b in bookings if 2 <= customer_bookings[b["customer_id"]] <= 3
            ),
            "Loyal": sum(1 for b in bookings if customer_bookings[b["customer_id"]] >= 4),
        },
        "bookings_by_city": dict(by_city),
        "bookings_by_language": dict(by_language),
        "bookings_by_ticket_type": dict(by_ticket_type),
        "bookings_by_month": dict(sorted(monthly.items())),
        "injected_defects": dict(defects),
    }


# ---------------------------------------------------------------------------
# 8. Main
# ---------------------------------------------------------------------------
FIELDS = [
    "booking_id", "customer_id", "customer_name", "customer_email", "phone",
    "age", "age_group", "gender", "city", "theatre_name", "screen",
    "seats_capacity", "movie_title", "genre", "language", "rating", "format",
    "show_id", "show_date", "show_time", "ticket_type", "seats", "ticket_price",
    "convenience_fee", "promo_code", "discount_amount", "total_amount",
    "payment_method", "booking_channel", "booking_status", "booking_datetime",
]


def main():
    print("Building customers...")
    customers = build_customers()
    print(f"  {len(customers)} customers across {len(CITIES)} cities")

    print("Generating shows and bookings...")
    bookings = generate_bookings(customers)
    print(f"  {len(bookings)} bookings")

    print("Injecting realistic data-quality defects...")
    rows, defects = inject_defects(bookings)
    print(f"  {len(rows)} raw rows ({defects['duplicate_rows']} duplicates)")

    print("Writing raw CSV...")
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row[field] for field in FIELDS})

    summary = build_summary(bookings, defects)
    with open(OUT_SUMMARY, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)

    print(f"\nWrote {len(rows):,} rows to {OUT_CSV}")
    print(f"Wrote summary to {OUT_SUMMARY}\n")
    print("=== GENERATION SUMMARY (clean base, before duplicates) ===")
    for key in [
        "clean_bookings", "unique_customers", "unique_shows", "theatres",
        "movies", "tickets_confirmed", "revenue_confirmed_inr",
        "avg_booking_value_inr", "cancellation_rate_pct",
        "aggregate_occupancy_pct",
    ]:
        value = summary[key]
        if isinstance(value, int):
            value = f"{value:,}"
        print(f"  {key:28s} {value}")
    print(f"  customers_by_type            {summary['customers_by_type']}")
    print(f"  bookings_by_city             {summary['bookings_by_city']}")
    print(f"  bookings_by_language         {summary['bookings_by_language']}")
    print(f"  bookings_by_ticket_type      {summary['bookings_by_ticket_type']}")
    print(f"  injected_defects             {summary['injected_defects']}")


if __name__ == "__main__":
    main()
