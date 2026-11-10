
from pathlib import Path
from datetime import datetime, timezone

import requests
import io
import pandas as pd
import certifi


# Project directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# World Bank Pink Sheet Excel source
WORLD_BANK_URL = (
    "https://thedocs.worldbank.org/en/doc/"
    "74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/"
    "related/CMO-Historical-Data-Monthly.xlsx"
)

# Output directory
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "commodities"


def collect_world_bank_data():
    print("Starting World Bank commodity data ingestion...")

    print("Downloading World Bank Pink Sheet data...")

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            )
        }

        response = requests.get(
            WORLD_BANK_URL,
            headers=headers,
            timeout=60,
            verify=certifi.where()
        )

        response.raise_for_status()

        excel_data = pd.ExcelFile(
            io.BytesIO(response.content),
            engine="openpyxl"
        )

        print("Available sheets:", excel_data.sheet_names)

        df = pd.read_excel(
            excel_data,
            sheet_name="Monthly Prices",
            header=4
        )

        print("Successfully downloaded World Bank data.")

        # Display available columns
        print("Available columns:")
        print(df.columns.tolist())

    except Exception as e:
        print(f"Failed to download World Bank data: {e}")
        return

    # Inspect the first rows before transformation

    # Transform World Bank data
    print("\nTransforming Nickel and Australian Coal data...")

    # Select required columns
    transformed_df = df[
        ["Unnamed: 0", "Nickel", "Coal, Australian"]
    ].copy()

    # Rename columns
    transformed_df = transformed_df.rename(
        columns={
            "Unnamed: 0": "period",
            "Nickel": "nickel_price",
            "Coal, Australian": "coal_price"
        }
    )

    # Remove unit row and invalid dates
    transformed_df = transformed_df[
        transformed_df["period"].astype(str).str.match(r"^\d{4}M\d{2}$")
    ].copy()

    # Convert YYYYMM period into datetime
    transformed_df["trading_date"] = pd.to_datetime(
        transformed_df["period"].str.replace("M", "-", regex=False) + "-01",
        format="%Y-%m-%d"
    )

    # Convert prices to numeric
    transformed_df["nickel_price"] = pd.to_numeric(
        transformed_df["nickel_price"], errors="coerce"
    )

    transformed_df["coal_price"] = pd.to_numeric(
        transformed_df["coal_price"], errors="coerce"
    )

    # Convert wide format to long format
    nickel_df = transformed_df[
        ["trading_date", "nickel_price"]
    ].rename(columns={"nickel_price": "close_price"})

    nickel_df["symbol"] = "NICKEL"
    nickel_df["commodity_name"] = "Nickel"
    nickel_df["unit"] = "USD/metric ton"

    coal_df = transformed_df[
        ["trading_date", "coal_price"]
    ].rename(columns={"coal_price": "close_price"})

    coal_df["symbol"] = "COAL"
    coal_df["commodity_name"] = "Australian Coal"
    coal_df["unit"] = "USD/metric ton"

    # Combine datasets
    final_df = pd.concat(
        [nickel_df, coal_df],
        ignore_index=True
    )

    # Sort data
    final_df = final_df.sort_values(
        ["symbol", "trading_date"]
    ).reset_index(drop=True)

    # Add metadata
    final_df["source"] = "World Bank Pink Sheet"
    final_df["frequency"] = "Monthly"
    final_df["ingested_at"] = datetime.now(timezone.utc)

    # Save as Parquet
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    ingestion_date = datetime.now().strftime("%Y-%m-%d")
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    output_path = (
        OUTPUT_DIR
        / f"ingestion_date={ingestion_date}"
        / f"run_id={run_id}"
    )

    output_path.mkdir(parents=True, exist_ok=True)

    file_path = output_path / "world_bank_commodities.parquet"

    final_df.to_parquet(file_path, index=False)

    print("\nWorld Bank ingestion completed!")
    print(f"Total records: {len(final_df):,}")
    print(f"Output: {file_path}")

    print("\nRecords per commodity:")
    print(final_df.groupby("symbol").size())

    print("\nLatest observations:")
    print(
        final_df.groupby("symbol").tail(5)[
            ["trading_date", "symbol", "close_price", "unit"]
        ]
    )

    print("\nMissing prices:")
    print(final_df.groupby("symbol")["close_price"].apply(
        lambda x: x.isna().sum()
    ))
if __name__ == "__main__":
    collect_world_bank_data()
