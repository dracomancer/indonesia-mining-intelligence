
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os


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

    # Find latest processed commodity data
    processed_path = PROJECT_ROOT / "data" / "processed" / "commodities"

    files = list(
        processed_path.rglob("commodity_data.parquet")
    )

    if not files:
        raise FileNotFoundError(
            "No processed commodity data found."
        )

    latest_file = max(
        files,
        key=lambda path: path.stat().st_mtime
    )

    print(f"Loading: {latest_file}")

    df = pd.read_parquet(latest_file)

    # Connect to PostgreSQL
    engine = create_engine(DATABASE_URL)

    # Initial load: replace existing table
    df.to_sql(
        name="commodity_prices",
        con=engine,
        schema="public",
        if_exists="replace",
        index=False,
        chunksize=1000,
        method="multi"
    )

    # Verify loaded records
    with engine.connect() as connection:
        result = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM public.commodity_prices"
        )
        count = result.scalar()

    print("\nCommodity data successfully loaded.")
    print(f"Records in PostgreSQL: {count}")

    engine.dispose()


if __name__ == "__main__":
    main()
