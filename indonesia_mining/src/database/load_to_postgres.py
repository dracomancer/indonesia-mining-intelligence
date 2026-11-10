
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL
import os

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Database configuration
database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5433")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(database_url)

def load_to_postgres():
    print("Starting PostgreSQL data loading...")

    # Find latest processed Parquet file
    files = sorted(PROCESSED_PATH.rglob("market_data.parquet"))

    if not files:
        raise FileNotFoundError("No processed Parquet file found.")

    source_file = files[-1]
    print(f"Source: {source_file}")

    # Read Parquet
    df = pd.read_parquet(source_file)

    # Convert trading_date to datetime for PostgreSQL
    df["trading_date"] = pd.to_datetime(df["trading_date"])

    print(f"Records to load: {len(df)}")

    # Load data into PostgreSQL
    df.to_sql(
        name="stock_prices",
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=1000,
        method="multi",
    )

    print("\nPOSTGRESQL LOADING SUMMARY")
    print(f"Records loaded: {len(df)}")
    print("Table: stock_prices")
    print("Status: SUCCESS")

    # Verify database record count
    with engine.connect() as connection:
        result = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM stock_prices"
        )
        print(f"Database records: {result.scalar()}")

if __name__ == "__main__":
    try:
        load_to_postgres()
    finally:
        engine.dispose()
