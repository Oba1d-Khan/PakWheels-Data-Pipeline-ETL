import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
import pyodbc 


# --- 1. SET UP THE PAGE ---
st.set_page_config(page_title="PakWheels Dashboard", layout="wide")
st.title("🚗 PakWheels Car Listings Dashboard")
st.write("Data loaded directly from your SQL Server database.")


TABLE_NAME = 'car_listings'


@st.cache_resource
def get_engine():
    try:
        db_creds = st.secrets["database"]
        connection_url = URL.create(
             "mssql+pyodbc",
            # Read all credentials securely from st.secrets
            username=db_creds["username"],
            password=db_creds["password"],
            host=db_creds["server"],
            database=db_creds["database"],
            query={"driver": db_creds["driver"]}
)
        engine = create_engine(connection_url)
        st.success("Connected to SQL Server!")
        return engine
    except Exception as e:
        st.error(f"Failed to connect to SQL Server: {e}")
        return None

engine = get_engine()

# --- 3. LOAD DATA FROM SQL ---
@st.cache_data
def load_data(query, _con):
    try:
        df = pd.read_sql(query, con=_con)
        # Convert types again, as SQL doesn't store 'Int64'
        df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        df['mileage'] = pd.to_numeric(df['mileage'], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Error reading data from SQL: {e}")
        return pd.DataFrame() # Return empty dataframe on error

if engine:
    query = f"SELECT * FROM {TABLE_NAME}"
    df = load_data(query, engine)
    
    if not df.empty:
        # --- 4. CREATE SIDEBAR FILTERS ---
        st.sidebar.header("Filter Your Data")

        # Filter by Brand
        brands = sorted(df['brand'].dropna().unique())
        selected_brands = st.sidebar.multiselect('Car Brand', brands, default=brands[:5])

        # Filter by Price
        min_price = int(df['price'].dropna().min())
        max_price = int(df['price'].dropna().max())
        price_range = st.sidebar.slider("Price Range (PKR)", 
                                        min_price, max_price, 
                                        (min_price, max_price))

        # Filter by Year
        min_year = int(df['year'].dropna().min())
        max_year = int(df['year'].dropna().max())
        year_range = st.sidebar.slider("Model Year", 
                                       min_year, max_year, 
                                       (min_year, max_year))

        # --- 5. APPLY FILTERS TO DATAFRAME ---
        df_filtered = df.dropna(subset=['brand', 'price', 'year'])[
            (df['brand'].isin(selected_brands)) &
            (df['price'] >= price_range[0]) &
            (df['price'] <= price_range[1]) &
            (df['year'] >= year_range[0]) &
            (df['year'] <= year_range[1])
        ]

        # --- 6. DISPLAY KEY METRICS (Analysis 3) ---
        st.header("Dashboard Key Metrics")
        st.write("These metrics update based on your filters.")
        
        col1, col2, col3 = st.columns(3)
        try:
            avg_price = f"PKR {df_filtered['price'].mean():,.0f}"
        except:
            avg_price = "N/A"
            
        try:
            avg_mileage = f"{df_filtered['mileage'].mean():,.0f} km"
        except:
            avg_mileage = "N/A"

        col1.metric("Total Listings Found", len(df_filtered))
        col2.metric("Average Price", avg_price)
        col3.metric("Average Mileage", avg_mileage)

        # --- 7. DISPLAY INTERACTIVE PLOTS (The 5 Analyses) ---
        st.header("Interactive Data Analysis")

        # Create two columns for plots
        fig_col1, fig_col2 = st.columns(2)

        with fig_col1:
            st.subheader("Top Brands")
            brand_counts = df_filtered['brand'].value_counts().head(10)
            st.bar_chart(brand_counts, use_container_width=True)

            st.subheader("Price vs. Mileage")
            st.scatter_chart(df_filtered, x='mileage', y='price', use_container_width=True)

        with fig_col2:
            st.subheader("Top Locations")
            city_counts = df_filtered['location'].value_counts().head(10)
            st.bar_chart(city_counts, use_container_width=True)

            st.subheader("Price vs. Model Year")
            st.scatter_chart(df_filtered, x='year', y='price', use_container_width=True)
        
        st.subheader("Listings by Fuel Type")
        fuel_counts = df_filtered['fuel_type'].value_counts()
        st.bar_chart(fuel_counts, use_container_width=True)

        # --- 8. DISPLAY THE RAW DATA TABLE ---
        st.header("Filtered Car Listings (Raw Data)")
        st.dataframe(df_filtered)

    else:
        st.warning("No data loaded from the database.")
else:
    st.error("Cannot create dashboard, database connection failed.")