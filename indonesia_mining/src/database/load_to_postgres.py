
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, MetaData, Table
from sqlalchemy.dialects.postgresql import insert


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
    print("Starting PostgreSQL UPSERT...")

    # Find latest processed Parquet file
    files = sorted(PROCESSED_PATH.rglob("market_data.parquet"))

    if not files:
        raise FileNotFoundError("No processed Parquet file found.")

    source_file = files[-1]
    print(f"Source: {source_file}")

    df = pd.read_parquet(source_file)

    required_columns = [
        "symbol", "trading_date", "Date",
        "Open", "High", "Low", "Close",
        "Adj Close", "Volume", "Dividends",
        "Stock Splits", "source", "ingested_at",
        "daily_return_pct", "intraday_range_pct",
        "turnover_idr", "market", "exchange", "currency",
    ]

    missing = set(required_columns) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    df["trading_date"] = pd.to_datetime(df["trading_date"]).dt.date

    # Remove duplicate keys inside the incoming batch
    df = df.drop_duplicates(
        subset=["symbol", "trading_date"],
        keep="last",
    )

    records = df[required_columns].to_dict(orient="records")

    metadata = MetaData()
    stock_table = Table(
        "stock_prices",
        metadata,
        schema="public",
        autoload_with=engine,
    )

    table_columns = {column.name for column in stock_table.columns}
    unknown_columns = set(required_columns) - table_columns

    if unknown_columns:
        raise ValueError(
            f"Columns missing from PostgreSQL table: {sorted(unknown_columns)}"
        )

    update_columns = {
        column: getattr(insert(stock_table).excluded, column)
        for column in required_columns
        if column not in ["symbol", "trading_date"]
    }

    total_affected = 0
    batch_size = 1000

    with engine.begin() as connection:
        for start in range(0, len(records), batch_size):
            batch = records[start:start + batch_size]

            stmt = insert(stock_table).values(batch)

            stmt = stmt.on_conflict_do_update(
                index_elements=[
                    stock_table.c.symbol,
                    stock_table.c.trading_date,
                ],
                set_=update_columns,
            )

            result = connection.execute(stmt)
            total_affected += result.rowcount

        total_rows = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM public.stock_prices"
        ).scalar_one()

        total_symbols = connection.exec_driver_sql(
            "SELECT COUNT(DISTINCT symbol) FROM public.stock_prices"
        ).scalar_one()

        total_rows = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM public.stock_prices"
        ).scalar_one()

        total_symbols = connection.exec_driver_sql(
            "SELECT COUNT(DISTINCT symbol) FROM public.stock_prices"
        ).scalar_one()

    print("\nPOSTGRESQL UPSERT SUMMARY")
    print(f"Input records: {len(df)}")
    print(f"Database rows affected: {total_affected}")
    print(f"Total database records: {total_rows}")
    print(f"Total stocks: {total_symbols}")
    print("Status: SUCCESS")


if __name__ == "__main__":
    try:
        load_to_postgres()
    finally:
        engine.dispose()
