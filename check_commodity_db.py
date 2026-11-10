
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL

# Load database credentials
load_dotenv(Path("indonesia_mining") / ".env")

url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5433")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(url)

queries = {
    "PUBLIC TABLE": """
        SELECT
            COUNT(*) AS total,
            COUNT(daily_return_pct) AS daily_return,
            COUNT(intraday_range_pct) AS intraday_range,
            COUNT(sma_20) AS sma_20,
            COUNT(sma_50) AS sma_50
        FROM public.commodity_prices
    """,

    "DBT INTERMEDIATE": """
        SELECT
            COUNT(*) AS total,
            COUNT(daily_return_pct) AS daily_return,
            COUNT(intraday_range_pct) AS intraday_range,
            COUNT(calculated_volatility_20d) AS volatility,
            COUNT(calculated_sma_20) AS sma_20
        FROM analytics.int_commodity_indicators
    """,

    "RECENT GOLD DATA": """
        SELECT
            trading_date,
            close_price,
            daily_return_pct,
            intraday_range_pct,
            calculated_sma_20,
            calculated_sma_50,
            calculated_volatility_20d
        FROM analytics.int_commodity_indicators
        WHERE symbol = 'GOLD'
        ORDER BY trading_date DESC
        LIMIT 10
    """
}

try:
    with engine.connect() as connection:
        for name, query in queries.items():
            print(f"\n===== {name} =====")
            result = connection.execute(text(query))

            for row in result.fetchall():
                print(row)

finally:
    engine.dispose()
