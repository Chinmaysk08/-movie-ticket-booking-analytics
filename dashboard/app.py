"""
Movie Ticket Booking Analytics -- Streamlit dashboard (dataset v2)
===================================================================

This is the runnable fallback for the Power BI report. It reads the Oracle star
schema through two views:

    V_BOOKING_DETAIL     one row per booking, all dimensions joined
    V_SHOW_PERFORMANCE   one row per show, occupancy derived

Run:
    $env:PYTHONPATH = "D:\\chinmay\\movie-ticket-booking-analytics\\src"
    D:\\venvs\\cinema\\Scripts\\streamlit.exe run dashboard/app.py

All data is synthetic. The dashboard demonstrates analytical method, not real
cinema performance.
"""

from pathlib import Path
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from db import get_conn  # noqa: E402

DAY_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

st.set_page_config(
    page_title="Movie Ticket Booking Analytics",
    layout="wide",
    page_icon="🎬",
)


@st.cache_data(ttl=300)
def load_bookings() -> pd.DataFrame:
    query = """
        SELECT booking_id, booking_datetime, booking_status,
               customer_id, customer_name, gender, age, age_group,
               customer_city, customer_type,
               movie_title, genre, language, rating,
               theatre_name, theatre_city, show_id, screen, format,
               show_date, show_time,
               payment_method, booking_channel,
               ticket_type, seats, ticket_price, convenience_fee,
               promo_code, discount_amount, total_amount
        FROM v_booking_detail
    """
    con = get_conn()
    cur = con.cursor()
    try:
        cur.execute(query)
        columns = [description[0].lower() for description in cur.description]
        frame = pd.DataFrame(cur.fetchall(), columns=columns)
    finally:
        cur.close()
        con.close()

    frame["show_date"] = pd.to_datetime(frame["show_date"])
    frame["booking_datetime"] = pd.to_datetime(frame["booking_datetime"])
    return frame


@st.cache_data(ttl=300)
def load_shows() -> pd.DataFrame:
    query = """
        SELECT show_id, movie_title, genre, language, rating,
               theatre_name, city, screen, format, seats_capacity,
               show_date, show_time, bookings, confirmed_seats,
               confirmed_revenue, occupancy_rate
        FROM v_show_performance
    """
    con = get_conn()
    cur = con.cursor()
    try:
        cur.execute(query)
        columns = [description[0].lower() for description in cur.description]
        frame = pd.DataFrame(cur.fetchall(), columns=columns)
    finally:
        cur.close()
        con.close()

    frame["show_date"] = pd.to_datetime(frame["show_date"])
    return frame


def money(value: float) -> str:
    return f"₹{value:,.0f}"


st.title("🎬 Movie Ticket Booking Analytics")
st.caption(
    "Oracle 26ai Free star schema · synthetic dataset v2 · 10,000 bookings, "
    "290 shows, 8 cities"
)

try:
    bookings = load_bookings()
    shows = load_shows()
except Exception as error:  # noqa: BLE001
    st.error(f"Could not load data from Oracle: {error}")
    st.stop()

# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------
st.sidebar.header("Filters")
st.sidebar.caption("City means the theatre's city, not the customer's.")

city_filter = st.sidebar.selectbox("City", ["All"] + sorted(bookings["theatre_city"].unique()))
genre_filter = st.sidebar.selectbox("Genre", ["All"] + sorted(bookings["genre"].unique()))
language_filter = st.sidebar.selectbox("Language", ["All"] + sorted(bookings["language"].unique()))
format_filter = st.sidebar.selectbox("Format", ["All"] + sorted(bookings["format"].unique()))

booking_view = bookings.copy()
show_view = shows.copy()

if city_filter != "All":
    booking_view = booking_view[booking_view["theatre_city"] == city_filter]
    show_view = show_view[show_view["city"] == city_filter]
if genre_filter != "All":
    booking_view = booking_view[booking_view["genre"] == genre_filter]
    show_view = show_view[show_view["genre"] == genre_filter]
if language_filter != "All":
    booking_view = booking_view[booking_view["language"] == language_filter]
    show_view = show_view[show_view["language"] == language_filter]
if format_filter != "All":
    booking_view = booking_view[booking_view["format"] == format_filter]
    show_view = show_view[show_view["format"] == format_filter]

if booking_view.empty:
    st.warning("No bookings match these filters.")
    st.stop()

confirmed = booking_view[booking_view["booking_status"] == "Confirmed"]
cancelled = booking_view[booking_view["booking_status"] == "Cancelled"]

# ---------------------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------------------
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
kpi1.metric("Bookings", f"{len(booking_view):,}")
kpi2.metric("Confirmed", f"{len(confirmed):,}")
kpi3.metric("Revenue", money(confirmed["total_amount"].sum()))
kpi4.metric("Avg booking value", money(confirmed["total_amount"].mean()))
kpi5.metric("Cancellation rate", f"{100 * len(cancelled) / len(booking_view):.2f}%")
kpi6.metric(
    "Mean show occupancy",
    f"{100 * show_view['occupancy_rate'].mean():.1f}%",
    help="Average of show-level occupancy, not of bookings.",
)

st.divider()

# ---------------------------------------------------------------------------
# Tabs mirror the four planned Power BI pages
# ---------------------------------------------------------------------------
overview_tab, movies_tab, customers_tab, operations_tab = st.tabs(
    ["Overview", "Movies & Formats", "Customers", "Operations"]
)

with overview_tab:
    left, right = st.columns(2)

    with left:
        st.subheader("Monthly revenue")
        monthly = (
            confirmed.assign(month=confirmed["show_date"].dt.strftime("%Y-%m"))
            .groupby("month", as_index=False)["total_amount"]
            .sum()
        )
        figure = px.line(
            monthly, x="month", y="total_amount", markers=True,
            labels={"month": "Month", "total_amount": "Revenue (INR)"},
            template="plotly_white",
        )
        figure.update_traces(line_color="#FF6B6B")
        st.plotly_chart(figure, width="stretch")

    with right:
        st.subheader("Revenue by day of week")
        daily = confirmed.assign(day=confirmed["show_date"].dt.day_name())
        daily = daily.groupby("day", as_index=False)["total_amount"].sum()
        daily["day"] = pd.Categorical(daily["day"], categories=DAY_ORDER, ordered=True)
        daily = daily.sort_values("day")
        figure = px.bar(
            daily, x="day", y="total_amount", color="total_amount",
            labels={"day": "Day", "total_amount": "Revenue (INR)"},
            template="plotly_white", color_continuous_scale="Blues",
        )
        st.plotly_chart(figure, width="stretch")

    st.subheader("City performance")
    city = (
        confirmed.groupby("theatre_city", as_index=False)
        .agg(revenue=("total_amount", "sum"), bookings=("booking_id", "count"))
        .sort_values("revenue", ascending=False)
    )
    city_occupancy = (
        show_view.groupby("city", as_index=False)["occupancy_rate"].mean()
        .rename(columns={"city": "theatre_city"})
    )
    city = city.merge(city_occupancy, on="theatre_city", how="left")
    city["occupancy_pct"] = (100 * city["occupancy_rate"]).round(1)
    figure = px.bar(
        city, x="theatre_city", y="revenue", color="occupancy_pct",
        labels={"theatre_city": "City", "revenue": "Revenue (INR)",
                "occupancy_pct": "Occupancy (%)"},
        template="plotly_white", color_continuous_scale="Viridis",
    )
    st.plotly_chart(figure, width="stretch")

with movies_tab:
    left, right = st.columns(2)

    with left:
        st.subheader("Top 10 movies by revenue (All Time)")
        top = (
            confirmed.groupby("movie_title", as_index=False)["total_amount"]
            .sum().nlargest(10, "total_amount")
        )
        figure = px.bar(
            top, x="total_amount", y="movie_title", orientation="h",
            labels={"total_amount": "Revenue (INR)", "movie_title": "Movie"},
            template="plotly_white", color="total_amount",
            color_continuous_scale="Reds",
        )
        figure.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(figure, width="stretch")

    with right:
        st.subheader("Genre mix")
        genre = confirmed.groupby("genre", as_index=False)["total_amount"].sum()
        figure = px.pie(
            genre, values="total_amount", names="genre", hole=0.4,
            template="plotly_white",
        )
        figure.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(figure, width="stretch")

    st.divider()
    st.subheader("Recent Movies (Last 30 Days)")
    max_date = confirmed["show_date"].max()
    start_d = max_date - pd.Timedelta(days=30)
    recent = confirmed[confirmed["show_date"] >= start_d]
    recent_movies = (
        recent.groupby("movie_title", as_index=False)
        .agg(Revenue=("total_amount", "sum"),
             Bookings=("booking_id", "count"),
             Tickets=("seats", "sum"))
        .sort_values("Revenue", ascending=False)
    )
    if recent_movies.empty:
        st.info("No confirmed bookings in the last 30 days of the dataset.")
    else:
        col_table, col_chart = st.columns([1, 1])
        with col_table:
            st.caption(
                f"Window: {start_d.strftime('%Y-%m-%d')} to "
                f"{max_date.strftime('%Y-%m-%d')} (end of dataset, not today)"
            )
            st.dataframe(recent_movies, width="stretch", hide_index=True)
        with col_chart:
            figure = px.bar(
                recent_movies.head(10), x="Revenue", y="movie_title", orientation="h",
                labels={"Revenue": "Revenue (INR)", "movie_title": "Movie"},
                template="plotly_white", color="Revenue",
                color_continuous_scale="Blues",
            )
            figure.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(figure, width="stretch")

    st.divider()
    left, right = st.columns(2)

    with left:
        st.subheader("Language revenue")
        language = confirmed.groupby("language", as_index=False)["total_amount"].sum()
        figure = px.bar(
            language, x="language", y="total_amount", color="language",
            labels={"language": "Language", "total_amount": "Revenue (INR)"},
            template="plotly_white",
        )
        st.plotly_chart(figure, width="stretch")

    with right:
        st.subheader("Format revenue")
        fmt = confirmed.groupby("format", as_index=False)["total_amount"].sum()
        figure = px.bar(
            fmt, x="format", y="total_amount", color="format",
            labels={"format": "Format", "total_amount": "Revenue (INR)"},
            template="plotly_white",
        )
        st.plotly_chart(figure, width="stretch")

with customers_tab:
    left, right = st.columns(2)

    with left:
        st.subheader("Customer segments")
        segments = (
            confirmed.groupby("customer_type", as_index=False)
            .agg(
                customers=("customer_id", "nunique"),
                bookings=("booking_id", "count"),
                revenue=("total_amount", "sum"),
            )
        )
        segments["revenue_per_customer"] = (
            segments["revenue"] / segments["customers"]
        ).round(0)
        segments = segments.sort_values("revenue", ascending=False)
        st.dataframe(segments, width="stretch", hide_index=True)

        figure = px.bar(
            segments, x="customer_type", y="revenue", color="customer_type",
            labels={"customer_type": "Segment", "revenue": "Revenue (INR)"},
            template="plotly_white",
        )
        st.plotly_chart(figure, width="stretch")

    with right:
        st.subheader("Payment method mix")
        payment = (
            booking_view.groupby("payment_method", as_index=False)
            .agg(bookings=("booking_id", "count"))
            .sort_values("bookings", ascending=False)
        )
        figure = px.pie(
            payment, values="bookings", names="payment_method",
            template="plotly_white",
        )
        figure.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(figure, width="stretch")

    st.subheader("Age group")
    age = (
        confirmed.groupby("age_group", as_index=False)
        .agg(
            bookings=("booking_id", "count"),
            revenue=("total_amount", "sum"),
            avg_booking_value=("total_amount", "mean"),
        )
        .sort_values("age_group")
    )
    age["avg_booking_value"] = age["avg_booking_value"].round(0)
    st.dataframe(age, width="stretch", hide_index=True)

    st.subheader("Ticket type")
    ticket = (
        confirmed.groupby("ticket_type", as_index=False)
        .agg(
            bookings=("booking_id", "count"),
            tickets=("seats", "sum"),
            revenue=("total_amount", "sum"),
        )
    )
    ticket["revenue_per_ticket"] = (ticket["revenue"] / ticket["tickets"]).round(0)
    st.dataframe(ticket, width="stretch", hide_index=True)

with operations_tab:
    left, right = st.columns(2)

    with left:
        st.subheader("Occupancy by show time")
        slot = (
            show_view.groupby("show_time", as_index=False)
            .agg(
                shows=("show_id", "count"),
                avg_occupancy=("occupancy_rate", "mean"),
            )
        )
        slot["occupancy_pct"] = (100 * slot["avg_occupancy"]).round(1)
        figure = px.bar(
            slot, x="show_time", y="occupancy_pct", color="occupancy_pct",
            labels={"show_time": "Show time", "occupancy_pct": "Occupancy (%)"},
            template="plotly_white", color_continuous_scale="Oranges",
        )
        st.plotly_chart(figure, width="stretch")

    with right:
        st.subheader("Cancellation rate by channel")
        channel = (
            booking_view.groupby("booking_channel", as_index=False)
            .agg(
                bookings=("booking_id", "count"),
                cancelled=("booking_status", lambda values: (values == "Cancelled").sum()),
            )
        )
        channel["cancellation_pct"] = (
            100 * channel["cancelled"] / channel["bookings"]
        ).round(2)
        figure = px.bar(
            channel, x="booking_channel", y="cancellation_pct",
            color="cancellation_pct",
            labels={"booking_channel": "Channel",
                    "cancellation_pct": "Cancellation rate (%)"},
            template="plotly_white", color_continuous_scale="Reds",
        )
        st.plotly_chart(figure, width="stretch")

    st.subheader("Theatre performance")
    theatre = (
        show_view.groupby(["theatre_name", "city"], as_index=False)
        .agg(
            shows=("show_id", "count"),
            confirmed_seats=("confirmed_seats", "sum"),
            revenue=("confirmed_revenue", "sum"),
            occupancy=("occupancy_rate", "mean"),
        )
        .sort_values("revenue", ascending=False)
    )
    theatre["occupancy_pct"] = (100 * theatre["occupancy"]).round(1)
    theatre = theatre[["theatre_name", "city", "shows", "confirmed_seats",
                       "revenue", "occupancy_pct"]]
    st.dataframe(theatre, width="stretch", hide_index=True)

    st.subheader("Promo codes")
    promo = (
        confirmed.groupby("promo_code", as_index=False)
        .agg(
            bookings=("booking_id", "count"),
            revenue=("total_amount", "sum"),
            discount=("discount_amount", "sum"),
        )
        .sort_values("revenue", ascending=False)
    )
    st.dataframe(promo, width="stretch", hide_index=True)

st.divider()
st.caption(
    "Source: Oracle 26ai Free (FREEPDB1) · views V_BOOKING_DETAIL and "
    "V_SHOW_PERFORMANCE · all data synthetic."
)
