import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from db import get_conn

st.set_page_config(page_title="Movie Ticket Booking Analytics", layout="wide", page_icon="🎬")

@st.cache_data(ttl=300)
def load_data():
    con = get_conn()
    q = """
    SELECT f.booking_id, f.seats, f.ticket_price, f.convenience_fee, f.discount_amount, 
           f.total_amount, f.promo_code, f.booking_status, f.booking_datetime,
           c.customer_name, c.age, c.age_group, c.gender, c.city,
           m.movie_title, m.genre, m.language,
           s.screen, s.format, s.show_date, s.show_time,
           d.day_name, d.month_name, d.year, d.is_weekend,
           p.payment_method, p.booking_channel
    FROM fact_bookings f
    JOIN dim_customer c ON f.customer_key = c.customer_key
    JOIN dim_movie m ON f.movie_key = m.movie_key
    JOIN dim_show s ON f.show_key = s.show_key
    JOIN dim_date d ON f.date_key = d.date_key
    JOIN dim_payment p ON f.payment_key = p.payment_key
    """
    cur = con.cursor()
    cur.execute(q)
    cols = [d[0].lower() for d in cur.description]
    df = pd.DataFrame(cur.fetchall(), columns=cols)
    cur.close()
    con.close()
    df['show_date'] = pd.to_datetime(df['show_date'])
    df['booking_datetime'] = pd.to_datetime(df['booking_datetime'])
    return df

st.title("🎬 Movie Ticket Booking Analytics Dashboard")
st.markdown("**Interactive Analytics | Oracle 26ai + Streamlit + Plotly**")

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load data from Oracle: {e}")
    st.stop()

# Sidebar filters
st.sidebar.header("Filters")
cities = ['All'] + sorted(df['city'].unique().tolist())
city_filter = st.sidebar.selectbox("City", cities)
genres = ['All'] + sorted(df['genre'].unique().tolist())
genre_filter = st.sidebar.selectbox("Genre", genres)
languages = ['All'] + sorted(df['language'].unique().tolist())
lang_filter = st.sidebar.selectbox("Language", languages)
formats = ['All'] + sorted(df['format'].unique().tolist())
fmt_filter = st.sidebar.selectbox("Format", formats)

df_f = df.copy()
if city_filter != 'All':
    df_f = df_f[df_f['city'] == city_filter]
if genre_filter != 'All':
    df_f = df_f[df_f['genre'] == genre_filter]
if lang_filter != 'All':
    df_f = df_f[df_f['language'] == lang_filter]
if fmt_filter != 'All':
    df_f = df_f[df_f['format'] == fmt_filter]

confirmed = df_f[df_f['booking_status']=='Confirmed']
cancelled = df_f[df_f['booking_status']=='Cancelled']

# KPIs
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Bookings", f"{len(df_f):,}")
col2.metric("Confirmed", f"{len(confirmed):,}")
col3.metric("Cancelled", f"{len(cancelled):,}")
col4.metric("Total Revenue (INR)", f"₹{confirmed['total_amount'].sum():,.0f}")
col5.metric("Avg Booking Value", f"₹{confirmed['total_amount'].mean():,.0f}" if len(confirmed)>0 else "₹0")

st.divider()

# Row 1
c1, c2 = st.columns(2)
with c1:
    st.subheader("Monthly Revenue Trend")
    monthly = confirmed.groupby(confirmed['show_date'].dt.to_period('M'))['total_amount'].sum().reset_index()
    monthly['show_date'] = monthly['show_date'].astype(str)
    fig = px.line(monthly, x='show_date', y='total_amount', markers=True,
                  labels={'show_date':'Month', 'total_amount':'Revenue (INR)'},
                  template='plotly_white')
    fig.update_traces(line_color='#FF6B6B')
    st.plotly_chart(fig, width='stretch')

with c2:
    st.subheader("Revenue by Day of Week")
    dow = confirmed.groupby('day_name')['total_amount'].sum().reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']).reset_index()
    fig = px.bar(dow, x='day_name', y='total_amount', color='total_amount',
                 labels={'day_name':'Day', 'total_amount':'Revenue (INR)'},
                 template='plotly_white', color_continuous_scale='Blues')
    st.plotly_chart(fig, width='stretch')

# Row 2
c1, c2 = st.columns(2)
with c1:
    st.subheader("Top 10 Movies by Revenue")
    top_movies = confirmed.groupby('movie_title')['total_amount'].sum().nlargest(10).reset_index()
    fig = px.bar(top_movies, x='total_amount', y='movie_title', orientation='h',
                 labels={'total_amount':'Revenue (INR)', 'movie_title':'Movie'},
                 template='plotly_white', color='total_amount', color_continuous_scale='Reds')
    fig.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig, width='stretch')

with c2:
    st.subheader("City-wise Performance")
    city_rev = confirmed.groupby('city')['total_amount'].sum().sort_values(ascending=False).reset_index()
    fig = px.bar(city_rev, x='city', y='total_amount', color='total_amount',
                 labels={'city':'City', 'total_amount':'Revenue (INR)'},
                 template='plotly_white', color_continuous_scale='Viridis')
    st.plotly_chart(fig, width='stretch')

# Row 3
c1, c2 = st.columns(2)
with c1:
    st.subheader("Show Time Analysis")
    stime = confirmed.groupby('show_time')['total_amount'].sum().reset_index()
    fig = px.bar(stime, x='show_time', y='total_amount', color='total_amount',
                 labels={'show_time':'Show Time', 'total_amount':'Revenue (INR)'},
                 template='plotly_white', color_continuous_scale='Oranges')
    st.plotly_chart(fig, width='stretch')

with c2:
    st.subheader("Genre Distribution")
    genre_cnt = confirmed.groupby('genre')['total_amount'].sum().reset_index()
    fig = px.pie(genre_cnt, values='total_amount', names='genre', hole=0.4,
                 template='plotly_white')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, width='stretch')

# Row 4
c1, c2 = st.columns(2)
with c1:
    st.subheader("Payment Method Split")
    pay = df_f.groupby('payment_method').size().reset_index(name='count')
    fig = px.pie(pay, values='count', names='payment_method', template='plotly_white')
    fig.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig, width='stretch')

with c2:
    st.subheader("Booking Channel vs Cancellation Rate")
    chan = df_f.groupby('booking_channel').agg(total=('booking_id','count'), cancelled=('booking_status', lambda x: (x=='Cancelled').sum())).reset_index()
    chan['cancel_rate'] = (chan['cancelled']/chan['total']*100).round(2)
    fig = px.bar(chan, x='booking_channel', y='cancel_rate', color='cancel_rate',
                 labels={'booking_channel':'Channel', 'cancel_rate':'Cancellation Rate (%)'},
                 template='plotly_white', color_continuous_scale='Reds')
    st.plotly_chart(fig, width='stretch')

st.divider()
st.subheader("Age Group Analysis")
age = confirmed.groupby('age_group')['total_amount'].agg(['sum','count','mean']).reset_index()
age.columns = ['Age Group', 'Revenue', 'Bookings', 'Avg Spend']
age['Avg Spend'] = age['Avg Spend'].round(0)
st.dataframe(age, width='stretch', hide_index=True)

st.caption("Data Source: Oracle 26ai FREEPDB1 | Generated: 10,000 bookings | Project: Movie Ticket Booking Analytics")
