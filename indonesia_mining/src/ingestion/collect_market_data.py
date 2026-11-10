
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import yaml
import yfinance as yf


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = PROJECT_ROOT / "config" / "stocks.yaml"
RAW_PATH = PROJECT_ROOT / "data" / "raw"


def load_stocks():
    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return [stock["symbol"] for stock in config["stocks"]]


def collect_market_data():
    symbols = load_stocks()

    run_time = datetime.now(timezone.utc)
    run_id = run_time.strftime("%Y%m%dT%H%M%SZ")

    output_dir = RAW_PATH / f"ingestion_date={run_time.date()}" / f"run_id={run_id}"
    output_dir.mkdir(parents=True, exist_ok=True)

    collected = []

    for symbol in symbols:
        print(f"Collecting {symbol}...")

        try:
            ticker = yf.Ticker(symbol)

            df = ticker.history(
                start="2023-01-01",
                interval="1d",
                auto_adjust=False,
                actions=True,
                timeout=30
            )

            if df.empty:
                print(f"WARNING: No data for {symbol}")
                continue

            df = df.reset_index()
            df["symbol"] = symbol
            df["source"] = "yfinance"
            df["ingested_at"] = run_time.isoformat()

            collected.append(df)

            print(f"SUCCESS: {symbol} - {len(df)} records")

        except Exception as error:
            print(f"ERROR: {symbol} - {error}")

    if not collected:
        raise RuntimeError("No market data collected.")

    final_df = pd.concat(collected, ignore_index=True)

    output_file = output_dir / "market_data.parquet"
    final_df.to_parquet(output_file, index=False)

    print("\nINGESTION SUMMARY")
    print(f"Total records: {len(final_df)}")
    print(f"Total symbols: {final_df['symbol'].nunique()}")
    print(f"Output: {output_file}")


if __name__ == "__main__":
    collect_market_data()
