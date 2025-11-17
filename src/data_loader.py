import sys
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from data_cleaning import get_clean_data
from pathlib import Path  
import toml              

def load_data_to_sql(df):
    
    # ---  LOAD SECRETS ---
  
    SECRETS_PATH = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"

    try:
        config = toml.load(SECRETS_PATH)
        db = config['database'] 
        
        DRIVER = db['driver']
        SERVER = db['server']
        DATABASE = db['database']
        USERNAME = db['username']
        PASSWORD = db['password']
        
    except FileNotFoundError:
        print(f"❌ Secrets file not found. I was looking for it at: {SECRETS_PATH}")
        print("   Please make sure '.streamlit/secrets.toml' exists in your project root.")
        sys.exit()
    except KeyError as e:
        print(f"❌ Error in secrets file: Could not find key {e}")
        print("   Make sure your secrets.toml has a [database] section with all keys.")
        sys.exit()

    TABLE_NAME = 'car_listings' 

    print(f"\n--- 4. STARTING DATA LOAD TO SQL (from secrets) ---")
    print(f"Connecting to: {SERVER}/{DATABASE} as {USERNAME}")

    try:
        connection_url = URL.create(
            "mssql+pyodbc",
            username=USERNAME,
            password=PASSWORD,
            host=SERVER,
            database=DATABASE,
            query={"driver": DRIVER}
        )
        engine = create_engine(connection_url)
        with engine.connect() as conn:
            print("✅ Connection engine created successfully.")
            
    except Exception as e:
        print(f"❌ Failed to create engine. Error: {e}")
        sys.exit()

    # ---  DUMP THE DATAFRAME TO THE SQL DB ---
    try:
        print(f"Attempting to write {len(df)} rows to table '{TABLE_NAME}'...")
        df.to_sql(
            TABLE_NAME,
            con=engine,
            if_exists='replace',
            index=False
        )
        print(f"✅ Success! Data dumped to '{TABLE_NAME}'.")
    except Exception as e:
        print(f"❌ Failed to dump data. Error: {e}")
        sys.exit()

    # ---  VERIFY DATA ---
    try:
        with engine.connect() as connection:
            query = f"SELECT TOP 5 * FROM {TABLE_NAME};"
            df_from_db = pd.read_sql(query, con=connection)
            print("\n✅ Verification complete. Read 5 rows back from DB:")
            print(df_from_db)
    except Exception as e:
        print(f"❌ Failed to read data back. Error: {e}")

if __name__ == '__main__':
    print("--- Running data_loader.py directly for testing... ---")
    

    csv_path = Path(__file__).parent.parent / "data" / "pakwheels_raw_data.csv"
    
    df = get_clean_data(csv_path) 
    load_data_to_sql(df)