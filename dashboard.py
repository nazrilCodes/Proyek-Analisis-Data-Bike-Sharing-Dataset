import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from babel.numbers import format_currency

sns.set(style='dark')
st.set_page_config(page_title="Bike Sharing Dashboard", layout="wide")

# --- Helper Functions ---
def create_daily_rent_df(df):
    daily_rent_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    })
    daily_rent_df = daily_rent_df.reset_index()
    return daily_rent_df

def create_by_season_df(df):
    # Data season di CSV sudah berupa teks, tidak butuh mapping lagi
    by_season_df = df.groupby(by="season").cnt.sum().reset_index()
    return by_season_df

def create_hourly_patterns_df(df):
    hourly_patterns_df = df.groupby(by=['workingday', 'hr']).cnt.mean().reset_index()
    return hourly_patterns_df

def create_monthly_df(df):
    monthly_df = df.copy()
    monthly_df["month"] = monthly_df["dteday"].dt.month_name()
    monthly_df = monthly_df.groupby(by="month").agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum"
    }).reset_index()
    return monthly_df

def create_weather_df(df):
    # Data weathersit di CSV sudah berupa teks
    weather_df = df.groupby(by="weathersit").cnt.mean().reset_index()
    return weather_df

def create_dow_df(df):
    # Data weekday di CSV sudah berupa teks (Mon, Tue, dst)
    dow_df = df.copy()
    dow_df["dayofweek"] = dow_df["weekday"]
    dow_df = dow_df.groupby(by="dayofweek").agg({
        "cnt": "mean",
        "casual": "mean",
        "registered": "mean"
    }).reset_index()
    order = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    dow_df["dayofweek"] = pd.Categorical(dow_df["dayofweek"], categories=order, ordered=True)
    dow_df = dow_df.sort_values("dayofweek")
    return dow_df

# --- Load Data ---
day_df = pd.read_csv("all_data_day.csv")
hour_df = pd.read_csv("all_data_hour.csv")

datetime_columns = ["dteday"]
day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)

for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])
    hour_df[column] = pd.to_datetime(hour_df[column])

min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

# --- Sidebar ---
with st.sidebar:
    st.image("D:\CodingCampDBS2026\Python\Submission\logo.jpg")
    
    start_date, end_date = st.date_input(
        label='Date Range',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    st.divider()
    st.subheader("Filters")
    
    # Nama cuaca disesuaikan persis dengan yang ada di dataset
    weather_options = ['All', 'Clear', 'Misty/Cloudy', 'Light Snow/Rain', 'Heavy Rain/Ice']
    selected_weather = st.selectbox("Weather Condition", weather_options)
    
    season_options = ['All', 'Spring', 'Summer', 'Fall', 'Winter']
    selected_season = st.selectbox("Season", season_options)
    
    show_comparison = st.checkbox("Compare User Types", value=True)

# --- Filter Data ---
main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

hourly_main_df = hour_df[(hour_df["dteday"] >= str(start_date)) & 
                         (hour_df["dteday"] <= str(end_date))]

# Memfilter langsung string-nya, tidak perlu translate lewat dictionary
if selected_weather != 'All':
    main_df = main_df[main_df['weathersit'] == selected_weather]

if selected_season != 'All':
    main_df = main_df[main_df['season'] == selected_season]

# --- Create Main DataFrames ---
daily_rent_df = create_daily_rent_df(main_df)
by_season_df = create_by_season_df(main_df)
hourly_patterns_df = create_hourly_patterns_df(hourly_main_df)
monthly_df = create_monthly_df(main_df)
weather_df = create_weather_df(main_df)
dow_df = create_dow_df(main_df)

# --- Main Page Dashboard ---
st.header('Bike Sharing Dashboard')

st.subheader('Key Metrics')
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_rentals = daily_rent_df.cnt.sum()
    st.metric("Total Rentals", value=f"{total_rentals:,}")

with col2:
    avg_daily = daily_rent_df.cnt.mean()
    # Mencegah error jika data kosong akibat filter
    st.metric("Avg Daily Rentals", value=f"{avg_daily:,.0f}" if pd.notna(avg_daily) else "0")

with col3:
    casual_pct = (daily_rent_df.casual.sum() / total_rentals * 100) if total_rentals > 0 else 0
    st.metric("Casual Users (%)", value=f"{casual_pct:.1f}%")

with col4:
    registered_pct = (daily_rent_df.registered.sum() / total_rentals * 100) if total_rentals > 0 else 0
    st.metric("Registered Users (%)", value=f"{registered_pct:.1f}%")

# --- Visualizations ---
with st.expander("📈 Daily Trends", expanded=True):
    fig = px.line(
        daily_rent_df, 
        x="dteday", 
        y="cnt",
        title='Daily Bike Rentals Trend',
        labels={'dteday': 'Date', 'cnt': 'Total Rentals'}
    )
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    with st.expander("🍂 Seasonal Performance"):
        fig = px.bar(
            by_season_df.sort_values(by="cnt", ascending=True),
            x="cnt",
            y="season",
            orientation='h',
            color="cnt",
            title='Rentals by Season',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    with st.expander("⛅ Weather Impact"):
        fig = px.bar(
            weather_df.sort_values(by="cnt", ascending=True),
            x="cnt",
            y="weathersit",
            orientation='h',
            color="cnt",
            title='Average Rentals by Weather',
            color_continuous_scale='Blues'
        )
        fig.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    with st.expander("📅 Day of Week Pattern"):
        fig = px.bar(
            dow_df,
            x="dayofweek",
            y="cnt",
            color="cnt",
            title='Average Rentals by Day of Week',
            color_continuous_scale='Oranges'
        )
        fig.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    with st.expander("💰 User Type Comparison"):
        if show_comparison:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=dow_df["dayofweek"],
                y=dow_df["casual"],
                name='Casual',
                marker_color='#FF6B6B'
            ))
            fig.add_trace(go.Bar(
                x=dow_df["dayofweek"],
                y=dow_df["registered"],
                name='Registered',
                marker_color='#4ECDC4'
            ))
            fig.update_layout(
                title='Casual vs Registered Users by Day',
                template="plotly_dark",
                barmode='group',
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)

with st.expander("⏰ Hourly Patterns (Working Day vs Weekend)"):
    hourly_patterns_df['workingday'] = hourly_patterns_df['workingday'].map({0: 'Holiday/Weekend', 1: 'Working Day'})
    
    fig = px.line(
        hourly_patterns_df,
        x='hr',
        y='cnt',
        color='workingday',
        markers=True,
        title='Average Hourly Rentals',
        labels={'hr': 'Hour (0-23)', 'cnt': 'Average Count', 'workingday': 'Day Type'}
    )
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

with st.expander("🌡️ Temperature vs Rentals"):
    # Plotly mewajibkan parameter size menggunakan data numerik, jadi diubah ke hum (kelembapan)
    fig = px.scatter(
        main_df,
        x="temp",
        y="cnt",
        color="season",
        size="hum", 
        hover_data=["dteday", "cnt", "weathersit"],
        title='Temperature vs Rentals by Season (Size based on Humidity)',
        labels={'temp': 'Normalized Temperature', 'cnt': 'Total Rentals'}
    )
    fig.update_layout(template="plotly_dark", height=400)
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    with st.expander("📊 Monthly Distribution"):
        month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                      'July', 'August', 'September', 'October', 'November', 'December']
        monthly_df["month"] = pd.Categorical(monthly_df["month"], categories=month_order, ordered=True)
        monthly_df = monthly_df.sort_values("month")
        
        fig = px.pie(
            monthly_df,
            values="cnt",
            names="month",
            title='Monthly Rentals Distribution',
            hole=0.3
        )
        fig.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    with st.expander("🔗 Correlation Heatmap"):
        corr_cols = ['temp', 'atemp', 'hum', 'windspeed', 'cnt', 'casual', 'registered']
        corr_df = main_df[corr_cols].corr()
        
        fig = px.imshow(
            corr_df,
            x=corr_df.columns,
            y=corr_df.columns,
            color_continuous_scale='RdBu',
            title='Feature Correlations'
        )
        fig.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig, use_container_width=True)

st.caption('Copyright (c) Nazril Abi Widiasto 2026')