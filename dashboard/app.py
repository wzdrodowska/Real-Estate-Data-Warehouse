from pathlib import Path
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st


# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Real Estate Analytics",
    page_icon=":house:",
    layout="wide",
)


# =====================================
# DATABASE
# =====================================

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "real_estate.db"


@st.cache_data
def load_data(db_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    with sqlite3.connect(db_path) as conn:
        fact_sales = pd.read_sql_query(
            """
            SELECT
                f.SaleID,
                f.SalePrice,
                f.PricePerM2,
                c.CityName,
                p.AreaM2 AS Area,
                p.Rooms
            FROM FactSales f
            JOIN DimCity c
            ON f.CityID = c.CityID
            JOIN DimProperty p
            ON f.PropertyID = p.PropertyID
            """,
            conn,
        )

        city_prices = pd.read_sql_query(
            """
            SELECT
                c.CityName,
                ROUND(AVG(f.PricePerM2), 2) AS AvgPricePerM2
            FROM FactSales f
            JOIN DimCity c
            ON f.CityID = c.CityID
            GROUP BY c.CityName
            ORDER BY AvgPricePerM2 DESC
            """,
            conn,
        )

    return fact_sales, city_prices


# =====================================
# TITLE
# =====================================

st.title("Real Estate Analytics Platform")
st.caption("Data Engineering & Analytics Project")


# =====================================
# LOAD DATA
# =====================================

if not DB_PATH.exists():
    st.error(f"Database not found: {DB_PATH}")
    st.stop()

fact_sales, city_prices = load_data(str(DB_PATH))

if fact_sales.empty or city_prices.empty:
    st.warning("No sales data found in the warehouse database.")
    st.stop()


# =====================================
# TABS
# =====================================

tab1, tab2 = st.tabs(
    ["Market Overview", "City Analysis"]
)


# =====================================
# MARKET OVERVIEW
# =====================================

with tab1:
    avg_price = round(
        fact_sales["SalePrice"].mean(),
        0,
    )

    avg_price_m2 = round(
        fact_sales["PricePerM2"].mean(),
        0,
    )

    listings = len(fact_sales)

    most_expensive_city = city_prices.iloc[0]["CityName"]

    cheapest_city = city_prices.iloc[-1]["CityName"]

    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric(
        "Average Sale Price",
        f"{avg_price:,.0f} PLN",
    )

    col2.metric(
        "Average Price per m2",
        f"{avg_price_m2:,.0f} PLN",
    )

    col3.metric(
        "Properties Analyzed",
        listings,
    )

    col4.metric(
        "Most Expensive City",
        most_expensive_city,
    )

    col5.metric(
        "Cheapest City",
        cheapest_city,
    )

    left, right = st.columns(2)

    with left:
        fig = px.bar(
            city_prices,
            x="CityName",
            y="AvgPricePerM2",
            title="Average Price per m2 by City",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:
        fig = px.pie(
            city_prices,
            names="CityName",
            values="AvgPricePerM2",
            title="Market Share by City",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    st.subheader("City Ranking")

    st.dataframe(
        city_prices,
        use_container_width=True,
    )


# =====================================
# CITY ANALYSIS
# =====================================

with tab2:
    selected_city = st.selectbox(
        "Select City",
        city_prices["CityName"].tolist(),
    )

    city_df = fact_sales[
        fact_sales["CityName"] == selected_city
    ]

    avg_price = round(
        city_df["SalePrice"].mean(),
        0,
    )

    avg_price_m2 = round(
        city_df["PricePerM2"].mean(),
        0,
    )

    avg_area = round(
        city_df["Area"].mean(),
        1,
    )

    listings = len(city_df)

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Average Price",
        f"{avg_price:,.0f} PLN",
    )

    c2.metric(
        "Average Price per m2",
        f"{avg_price_m2:,.0f} PLN",
    )

    c3.metric(
        "Average Area",
        f"{avg_area} m2",
    )

    c4.metric(
        "Listings",
        listings,
    )

    left, right = st.columns(2)

    with left:
        fig = px.histogram(
            city_df,
            x="SalePrice",
            nbins=20,
            title=f"Price Distribution - {selected_city}",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    with right:
        fig = px.scatter(
            city_df,
            x="Area",
            y="SalePrice",
            color="Rooms",
            title=f"Area vs Price - {selected_city}",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    rooms_city = (
        city_df
        .groupby("Rooms")["SalePrice"]
        .mean()
        .reset_index()
    )

    fig = px.line(
        rooms_city,
        x="Rooms",
        y="SalePrice",
        markers=True,
        title=f"Average Price by Number of Rooms - {selected_city}",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.subheader("City Data")

    st.dataframe(
        city_df,
        use_container_width=True,
    )
