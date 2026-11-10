
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine


# Project paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


# Database configuration
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


def main():

    # Find latest World Bank Parquet file
    raw_path = PROJECT_ROOT / "data" / "raw" / "commodities"

    files = list(
        raw_path.rglob("world_bank_commodities.parquet")
    )

    if not files:
        raise FileNotFoundError(
            "No World Bank commodity data found."
        )

    latest_file = max(
        files,
        key=lambda path: path.stat().st_mtime
    )

    print(f"Loading: {latest_file}")

    df = pd.read_parquet(latest_file)

    print(f"Records found: {len(df):,}")

    # Connect to PostgreSQL
    engine = create_engine(DATABASE_URL)

    try:
        # Load into a separate table
        df.to_sql(
            name="world_bank_commodity_prices",
            con=engine,
            schema="public",
            if_exists="replace",
            index=False,
            chunksize=1000,
            method="multi"
        )

        # Verify records
        with engine.connect() as connection:
            result = connection.exec_driver_sql(
                """
                SELECT symbol, COUNT(*) AS total_records,
                       COUNT(close_price) AS valid_prices
                FROM public.world_bank_commodity_prices
                GROUP BY symbol
                ORDER BY symbol
                """
            )

            print("\nPostgreSQL verification:")
            print(pd.DataFrame(
                result.fetchall(),
                columns=result.keys()
            ))

        print("\nWorld Bank data successfully loaded.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
