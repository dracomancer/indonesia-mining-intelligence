
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL

# Database connection
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

checks = {
    "YAHOO COMMODITY MISSING VALUES": """
        SELECT
            symbol,
            COUNT(*) AS total_rows,
            COUNT(*) FILTER (WHERE close_price IS NULL) AS missing_close,
            COUNT(*) FILTER (WHERE daily_return_pct IS NULL) AS missing_return,
            COUNT(*) FILTER (WHERE intraday_range_pct IS NULL) AS missing_range,
            COUNT(*) FILTER (WHERE calculated_sma_20 IS NULL) AS missing_sma20,
            COUNT(*) FILTER (WHERE calculated_sma_50 IS NULL) AS missing_sma50,
            COUNT(*) FILTER (WHERE calculated_volatility_20d IS NULL) AS missing_volatility
        FROM analytics.int_commodity_indicators
        GROUP BY symbol
        ORDER BY symbol
    """,

    "YAHOO COMMODITY DUPLICATES": """
        SELECT
            symbol,
            trading_date,
            COUNT(*) AS duplicate_count
        FROM analytics.int_commodity_indicators
        GROUP BY symbol, trading_date
        HAVING COUNT(*) > 1
        ORDER BY symbol, trading_date
    """,

    "WORLD BANK MISSING VALUES": """
        SELECT
            symbol,
            COUNT(*) AS total_rows,
            COUNT(*) FILTER (WHERE close_price IS NULL) AS missing_close,
            COUNT(*) FILTER (WHERE monthly_return_pct IS NULL) AS missing_return,
            COUNT(*) FILTER (WHERE sma_3m IS NULL) AS missing_sma3m,
            COUNT(*) FILTER (WHERE sma_6m IS NULL) AS missing_sma6m,
            COUNT(*) FILTER (WHERE volatility_3m IS NULL) AS missing_volatility
        FROM analytics.int_world_bank_commodity_indicators
        GROUP BY symbol
        ORDER BY symbol
    """,

    "WORLD BANK DUPLICATES": """
        SELECT
            symbol,
            trading_date,
            COUNT(*) AS duplicate_count
        FROM analytics.int_world_bank_commodity_indicators
        GROUP BY symbol, trading_date
        HAVING COUNT(*) > 1
        ORDER BY symbol, trading_date
    """,

    "COAL MISSING DATE ANALYSIS": """
        SELECT
            EXTRACT(YEAR FROM trading_date) AS year,
            COUNT(*) AS total_observations,
            COUNT(*) FILTER (
                WHERE close_price IS NULL
            ) AS missing_prices,
            COUNT(*) FILTER (
                WHERE close_price IS NOT NULL
            ) AS valid_prices
        FROM analytics.int_world_bank_commodity_indicators
        WHERE symbol = 'COAL'
        GROUP BY EXTRACT(YEAR FROM trading_date)
        ORDER BY year
    """,

    "COAL MISSING DATE RANGE": """
        SELECT
            MIN(trading_date) FILTER (
                WHERE close_price IS NULL
            ) AS first_missing_date,
            MAX(trading_date) FILTER (
                WHERE close_price IS NULL
            ) AS last_missing_date,
            MIN(trading_date) FILTER (
                WHERE close_price IS NOT NULL
            ) AS first_valid_date,
            MAX(trading_date) FILTER (
                WHERE close_price IS NOT NULL
            ) AS last_valid_date
        FROM analytics.int_world_bank_commodity_indicators
        WHERE symbol = 'COAL'
    """,

    "YAHOO COMMODITY DATE RANGE": """
        SELECT
            symbol,
            MIN(trading_date) AS first_date,
            MAX(trading_date) AS latest_date,
            COUNT(DISTINCT trading_date) AS unique_dates,
            COUNT(*) AS total_rows,
            COUNT(*) FILTER (
                WHERE trading_date > CURRENT_DATE
            ) AS future_dates
        FROM analytics.int_commodity_indicators
        GROUP BY symbol
        ORDER BY symbol
    """,

    "WORLD BANK COMMODITY DATE RANGE": """
        SELECT
            symbol,
            MIN(trading_date) AS first_date,
            MAX(trading_date) AS latest_date,
            COUNT(DISTINCT trading_date) AS unique_dates,
            COUNT(*) AS total_rows,
            COUNT(*) FILTER (
                WHERE trading_date > CURRENT_DATE
            ) AS future_dates
        FROM analytics.int_world_bank_commodity_indicators
        GROUP BY symbol
        ORDER BY symbol
    """

}

try:
    with engine.connect() as connection:
        for title, query in checks.items():
            print(f"\n{'=' * 60}")
            print(title)
            print("=" * 60)

            result = connection.execute(text(query))
            rows = result.fetchall()

            if rows:
                for row in rows:
                    print(row)
            else:
                print("No issues found.")

finally:
    engine.dispose()
