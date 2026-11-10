from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, URL, text

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

url = URL.create(
    "postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5433")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(url)

with engine.connect() as conn:
    print("DATABASE SCHEMA")
    result = conn.execute(text("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'stock_prices'
        ORDER BY ordinal_position
    """))

    for row in result:
        print(row)

    print("\nSTOCK DISTRIBUTION")
    result = conn.execute(text("""
        SELECT symbol, COUNT(*) AS total_records
        FROM stock_prices
        GROUP BY symbol
        ORDER BY symbol
    """))

    for row in result:
        print(row)

    print("\nDATE RANGE")
    result = conn.execute(text("""
        SELECT MIN(trading_date), MAX(trading_date)
        FROM stock_prices
    """))

    print(result.fetchone())

engine.dispose()