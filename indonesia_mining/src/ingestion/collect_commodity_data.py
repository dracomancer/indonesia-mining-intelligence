
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
import yaml
import yfinance as yf


# =====================================================
# CONFIGURATION
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CONFIG_PATH = PROJECT_ROOT / "config" / "commodities.yaml"
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw"

START_DATE = "2023-01-01"


# =====================================================
# LOAD COMMODITY CONFIGURATION
# =====================================================

def load_commodities():

    with open(CONFIG_PATH, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config["commodities"]


# =====================================================
# COLLECT COMMODITY DATA
# =====================================================

def collect_commodity_data():

    commodities = load_commodities()

    all_data = []

    for commodity in commodities:

        ticker_symbol = commodity.get("yahoo_ticker")

        if not ticker_symbol:
            print(
                f"SKIPPED: {commodity['name']} "
                f"(source: {commodity['source']})"
            )
            continue

        print(f"Downloading {commodity['name']}...")

        try:

            ticker = yf.Ticker(ticker_symbol)

            df = ticker.history(
                start=START_DATE,
                interval="1d",
                auto_adjust=False,
                actions=True,
                timeout=30
            )

            if df.empty:
                print(f"WARNING: No data for {commodity['name']}")
                continue

            df = df.reset_index()

            df["symbol"] = commodity["symbol"]
            df["commodity_name"] = commodity["name"]
            df["category"] = commodity["category"]
            df["unit"] = commodity["unit"]
            df["source"] = commodity["source"]
            df["ingested_at"] = datetime.now(
                timezone.utc
            ).isoformat()

            all_data.append(df)

            print(
                f"SUCCESS: {commodity['name']} "
                f"({len(df)} records)"
            )

        except Exception as error:

            print(
                f"ERROR: {commodity['name']} - {error}"
            )

    if not all_data:
        raise RuntimeError("No commodity data collected.")

    result = pd.concat(
        all_data,
        ignore_index=True
    )

    return result


# =====================================================
# SAVE RAW DATA
# =====================================================

def save_raw_data(df):

    ingestion_date = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    run_id = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    output_dir = (
        RAW_DATA_PATH
        / "commodities"
        / f"ingestion_date={ingestion_date}"
        / f"run_id={run_id}"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = output_dir / "commodity_data.parquet"

    df.to_parquet(
        output_file,
        index=False
    )

    print("\nCommodity ingestion completed.")
    print(f"Total records: {len(df)}")
    print(f"Saved to: {output_file}")


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    commodity_data = collect_commodity_data()

    save_raw_data(commodity_data)
