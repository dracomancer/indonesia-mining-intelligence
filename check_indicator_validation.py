
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL

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
    "YAHOO DAILY RETURN VALIDATION": """
        WITH validation AS (
            SELECT
                symbol,
                trading_date,
                daily_return_pct,
                (
                    (close_price / NULLIF(
                        LAG(close_price) OVER (
                            PARTITION BY symbol
                            ORDER BY price_timestamp
                        ), 0
                    ) - 1) * 100
                ) AS expected_return
            FROM analytics.int_commodity_indicators
        )
        SELECT
            symbol,
            COUNT(*) AS observations,
            COUNT(*) FILTER (
                WHERE ABS(daily_return_pct - expected_return) > 0.000001
            ) AS mismatches
        FROM validation
        WHERE expected_return IS NOT NULL
          AND daily_return_pct IS NOT NULL
        GROUP BY symbol
        ORDER BY symbol
    """,

    "YAHOO SMA VALIDATION": """
        WITH validation AS (
            SELECT
                symbol,
                trading_date,
                calculated_sma_20,
                calculated_sma_50,
                AVG(close_price) OVER (
                    PARTITION BY symbol
                    ORDER BY price_timestamp
                    ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
                ) AS expected_sma_20,
                AVG(close_price) OVER (
                    PARTITION BY symbol
                    ORDER BY price_timestamp
                    ROWS BETWEEN 49 PRECEDING AND CURRENT ROW
                ) AS expected_sma_50
            FROM analytics.int_commodity_indicators
        )
        SELECT
            symbol,
            COUNT(*) FILTER (
                WHERE ABS(calculated_sma_20 - expected_sma_20) > 0.000001
            ) AS sma20_mismatches,
            COUNT(*) FILTER (
                WHERE ABS(calculated_sma_50 - expected_sma_50) > 0.000001
            ) AS sma50_mismatches
        FROM validation
        GROUP BY symbol
        ORDER BY symbol
    """,

    "WORLD BANK MONTHLY RETURN VALIDATION": """
        WITH validation AS (
            SELECT
                symbol,
                trading_date,
                monthly_return_pct,
                (
                    (close_price / NULLIF(
                        LAG(close_price) OVER (
                            PARTITION BY symbol
                            ORDER BY trading_date
                        ), 0
                    ) - 1) * 100
                ) AS expected_return
            FROM analytics.int_world_bank_commodity_indicators
            WHERE close_price IS NOT NULL
        )
        SELECT
            symbol,
            COUNT(*) FILTER (
                WHERE ABS(monthly_return_pct - expected_return) > 0.000001
            ) AS mismatches
        FROM validation
        WHERE expected_return IS NOT NULL
          AND monthly_return_pct IS NOT NULL
        GROUP BY symbol
        ORDER BY symbol
    """,

    "YAHOO VOLATILITY VALIDATION": """
        WITH validation AS (
            SELECT
                symbol,
                trading_date,
                calculated_volatility_20d,
                STDDEV_SAMP(daily_return_pct) OVER (
                    PARTITION BY symbol
                    ORDER BY price_timestamp
                    ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
                ) AS expected_volatility
            FROM analytics.int_commodity_indicators
        )
        SELECT
            symbol,
            COUNT(*) FILTER (
                WHERE ABS(
                    calculated_volatility_20d - expected_volatility
                ) > 0.000001
            ) AS mismatches
        FROM validation
        WHERE calculated_volatility_20d IS NOT NULL
        AND expected_volatility IS NOT NULL
        GROUP BY symbol
        ORDER BY symbol
    """,

    "YAHOO INTRADAY RANGE VALIDATION": """
        WITH validation AS (
            SELECT
                symbol,
                trading_date,
                intraday_range_pct,
                (
                    (high_price - low_price)
                    / NULLIF(close_price, 0)
                ) * 100 AS expected_range
            FROM analytics.int_commodity_indicators
        )
        SELECT
            symbol,
            COUNT(*) FILTER (
                WHERE ABS(intraday_range_pct - expected_range) > 0.000001
            ) AS mismatches
        FROM validation
        WHERE intraday_range_pct IS NOT NULL
        AND expected_range IS NOT NULL
        GROUP BY symbol
        ORDER BY symbol
    """,

    "WORLD BANK VOLATILITY VALIDATION": """
        WITH validation AS (
            SELECT
                symbol,
                trading_date,
                volatility_3m,
                STDDEV_SAMP(monthly_return_pct) OVER (
                    PARTITION BY symbol
                    ORDER BY trading_date
                    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
                ) AS expected_volatility
            FROM analytics.int_world_bank_commodity_indicators
        )
        SELECT
            symbol,
            COUNT(*) FILTER (
                WHERE ABS(
                    volatility_3m - expected_volatility
                ) > 0.000001
            ) AS mismatches
        FROM validation
        WHERE volatility_3m IS NOT NULL
        AND expected_volatility IS NOT NULL
        GROUP BY symbol
        ORDER BY symbol
    """
}

try:
    with engine.connect() as connection:
        for title, query in queries.items():
            print(f"\n{'=' * 60}")
            print(title)
            print("=" * 60)

            result = connection.execute(text(query))

            for row in result.fetchall():
                print(row)

finally:
    engine.dispose()
