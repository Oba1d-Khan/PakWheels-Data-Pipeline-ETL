import matplotlib.pyplot as plt
import os
from utils.paths import get_data_path

def generate_all_plots(df, output_dir=None):
    print("--- 3. STARTING DATA ANALYSIS ---")
    
    # Create output directory if it doesn't exist
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(get_data_path('pakwheels_raw_data_.csv')), 'plots')
    os.makedirs(output_dir, exist_ok=True)

    # Filter outliers for cleaner plots
    df_filtered = df[df['price'] < 20000000] 

    # --- Plot 1: Price vs. Mileage ---
    plt.figure(figsize=(10, 6))
    plt.scatter(df_filtered['mileage'], df_filtered['price'], alpha=0.5)
    plt.title('Car Price vs. Mileage')
    plt.xlabel('Mileage (km)')
    plt.ylabel('Price (PKR)')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'price_vs_mileage.png'))
    print("Saved 'price_vs_mileage.png'")

    # --- Plot 2: Price vs. Year ---
    plt.figure(figsize=(10, 6))
    plt.scatter(df_filtered['year'], df_filtered['price'], alpha=0.5)
    plt.title('Car Price vs. Model Year')
    plt.xlabel('Model Year')
    plt.ylabel('Price (PKR)')
    plt.grid(True)
    plt.savefig(os.path.join(output_dir, 'price_vs_year.png'))
    print("Saved 'price_vs_year.png'")

    # --- Plot 3: Top Brands ---
    top_brands = df['brand'].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    top_brands.plot(kind='bar', color='skyblue')
    plt.title('Top 10 Most Common Car Brands')
    plt.xlabel('Brand')
    plt.ylabel('Number of Listings')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'brand_counts.png'))
    print("Saved 'brand_counts.png'")

    # --- Plot 4: Top Cities ---
    top_cities = df['location'].value_counts().head(10)
    plt.figure(figsize=(10, 6))
    top_cities.plot(kind='bar', color='lightgreen')
    plt.title('Top 10 Cities with Most Listings')
    plt.xlabel('City')
    plt.ylabel('Number of Listings')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'city_counts.png'))
    print("Saved 'city_counts.png'")

    # --- Plot 5: Fuel Types ---
    fuel_types = df['fuel_type'].value_counts()
    plt.figure(figsize=(10, 6))
    fuel_types.plot(kind='bar', color='salmon')
    plt.title('Listings by Fuel Type')
    plt.xlabel('Fuel Type')
    plt.ylabel('Number of Listings')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'fuel_types.png'))
    print("Saved 'fuel_types.png'")
    
    print(f"✅ Analysis complete. All plots saved in '{output_dir}'.")
