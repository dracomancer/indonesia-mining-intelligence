
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = PROJECT_ROOT / "data" / "raw"


def validate_raw():
    files = sorted(RAW_PATH.rglob("market_data.parquet"))

    if not files:
        raise FileNotFoundError("No Parquet files found.")

    latest_file = files[-1]
    df = pd.read_parquet(latest_file)

    print("=" * 55)
    print("RAW DATA VALIDATION")
    print("=" * 55)

    print(f"\nFile: {latest_file}")
    print(f"Total records: {len(df)}")
    print(f"Total columns: {len(df.columns)}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nRecords per stock:")
    print(df.groupby("symbol").size())

    print("\nMissing values:")
    print(df.isnull().sum())

    print("\nDuplicate records:")
    print(df.duplicated(subset=["symbol", "Date"]).sum())

    print("\nSample data:")
    print(df.head(5).to_string(index=False))


if __name__ == "__main__":
    validate_raw()
