from pathlib import Path
import time

import pandas as pd
import yfinance as yf
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "stocks.yaml"


def load_stocks():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config["stocks"]


def check_tickers():
    stocks = load_stocks()
    results = []

    print("=" * 65)
    print("INDONESIAN MINING STOCKS - DATA SOURCE VALIDATION")
    print("=" * 65)

    for stock in stocks:
        symbol = stock["symbol"]
        company = stock["company"]

        print(f"Checking {symbol}...", end=" ")

        try:
            ticker = yf.Ticker(symbol)
            history = ticker.history(
                period="5d",
                interval="1d",
                auto_adjust=False,
                timeout=20
            )

            if history.empty:
                status = "NO DATA"
                latest_date = None
                latest_price = None
            else:
                status = "AVAILABLE"
                latest_date = history.index[-1].strftime("%Y-%m-%d")
                latest_price = round(float(history["Close"].iloc[-1]), 2)

            results.append({
                "symbol": symbol,
                "company": company,
                "status": status,
                "latest_date": latest_date,
                "latest_price": latest_price
            })

            print(status)

        except Exception as error:
            results.append({
                "symbol": symbol,
                "company": company,
                "status": "ERROR",
                "latest_date": None,
                "latest_price": None
            })

            print(f"ERROR: {error}")

        time.sleep(1)

    result_df = pd.DataFrame(results)

    print("\nVALIDATION SUMMARY")
    print(result_df.to_string(index=False))

    available = (result_df["status"] == "AVAILABLE").sum()
    print(f"\nAvailable tickers: {available}/{len(result_df)}")


if __name__ == "__main__":
    check_tickers()
