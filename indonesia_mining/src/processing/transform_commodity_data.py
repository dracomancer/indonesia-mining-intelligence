
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd


# =====================================================
# PATH CONFIGURATION
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_PATH = PROJECT_ROOT / "data" / "raw" / "commodities"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "commodities"


# =====================================================
# LOAD LATEST RAW DATA
# =====================================================

def load_raw_data():

    files = list(RAW_PATH.rglob("commodity_data.parquet"))

    if not files:
        raise FileNotFoundError("No raw commodity data found.")

    latest_file = max(
        files,
        key=lambda path: path.stat().st_mtime
    )

    print(f"Loading: {latest_file}")

    return pd.read_parquet(latest_file)


# =====================================================
# TRANSFORM DATA
# =====================================================

def transform_data(df):

    df = df.copy()

    df["Date"] = pd.to_datetime(df["Date"])

    df = df.sort_values(
        ["symbol", "Date"]
    ).reset_index(drop=True)

    grouped = df.groupby("symbol", group_keys=False)

    # Daily price movement
    df["price_change"] = grouped["Close"].diff()

    df["daily_return_pct"] = (
        grouped["Close"].pct_change() * 100
    )

    # Intraday price range
    df["intraday_range_pct"] = (
        (df["High"] - df["Low"])
        / df["Close"].replace(0, pd.NA)
        * 100
    )

    # Moving averages
    df["sma_20"] = grouped["Close"].transform(
        lambda x: x.rolling(20, min_periods=20).mean()
    )

    df["sma_50"] = grouped["Close"].transform(
        lambda x: x.rolling(50, min_periods=50).mean()
    )

    # 20-day historical volatility
    df["volatility_20d"] = grouped["daily_return_pct"].transform(
        lambda x: x.rolling(20, min_periods=20).std()
    )

    # Metadata
    df["market"] = "Global Commodity Market"
    df["ingestion_processed_at"] = datetime.now(
        timezone.utc
    ).isoformat()

    return df


# =====================================================
# DATA QUALITY CHECK
# =====================================================

def validate_data(df):

    required_columns = [
        "Date",
        "symbol",
        "Close",
        "daily_return_pct",
        "sma_20",
        "sma_50"
    ]

    missing = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    if df["Close"].isna().any():
        raise ValueError("Null closing prices detected.")

    if (df["Close"] <= 0).any():
        raise ValueError("Non-positive closing prices detected.")

    print("Data quality checks passed.")


# =====================================================
# SAVE PROCESSED DATA
# =====================================================

def save_processed_data(df):

    ingestion_date = datetime.now(
        timezone.utc
    ).strftime("%Y-%m-%d")

    run_id = datetime.now(
        timezone.utc
    ).strftime("%Y%m%dT%H%M%SZ")

    output_dir = (
        PROCESSED_PATH
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

    print("\nTransformation completed.")
    print(f"Records: {len(df)}")
    print(f"Saved: {output_file}")


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    raw_data = load_raw_data()

    transformed_data = transform_data(raw_data)

    validate_data(transformed_data)

    save_processed_data(transformed_data)
