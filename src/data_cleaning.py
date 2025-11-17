# src/data_cleaning.py

import pandas as pd
import numpy as np
from utils.paths import get_data_path


def clean_price(price_str):
    """Convert PKR prices with lacs/crore into numeric PKR."""
    if pd.isna(price_str):
        return np.nan

    price_str = str(price_str).lower()
    price_str = price_str.replace('pkr', '').replace(',', '').strip()

    # Lacs
    if 'lacs' in price_str:
        try:
            num = float(price_str.replace('lacs', '').strip())
            return num * 100000
        except:
            return np.nan

    # Crore
    if 'crore' in price_str:
        try:
            num = float(price_str.replace('crore', '').strip())
            return num * 10000000
        except:
            return np.nan

    # Plain numeric
    try:
        return float(price_str)
    except:
        return np.nan


def get_clean_data(csv_path=None):
    """Load raw CSV → clean → return DataFrame."""

    if csv_path is None:
        csv_path = get_data_path('pakwheels_raw_data_.csv')

    print("--- 1. Loading and Cleaning Data ---")

    try:
        df = pd.read_csv(csv_path, na_values=['None', 'none'])
    except FileNotFoundError:
        print(f"❌ ERROR: CSV not found at: {csv_path}")
        return None

    # --- Clean Columns ---
    df['price'] = df['price'].apply(clean_price)

 

    df['mileage'] = (
        df['mileage'].astype(str).str.replace(',', '').str.extract(r'(\d+)').astype(float)
    )

    df['engine_cc'] = (
        df['engine_cc'].astype(str).str.extract(r'(\d+)').astype(float)
    )

    df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')

    # Brand = first word of name
    df['brand'] = df['name'].str.split(' ').str[0]

    print("✅ Data cleaned. Summary:")
    print(df.info())

    return df


if __name__ == "__main__":
    # If someone runs this file directly
    csv_path = get_data_path('pakwheels_raw_data_.csv')
    df = get_clean_data(csv_path)

    if df is not None:
        print("\n--- Preview Cleaned Data ---")
        print(df.head())
