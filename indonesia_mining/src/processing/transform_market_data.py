
from pathlib import Path
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = PROJECT_ROOT / "data" / "raw"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed"


def transform_market_data():
    files = sorted(RAW_PATH.rglob("market_data.parquet"))

    if not files:
        raise FileNotFoundError("No raw Parquet files found.")

    source_file = files[-1]
    df = pd.read_parquet(source_file)

    print("Starting data transformation...")

    # 1. Convert and sort dates
    df["Date"] = pd.to_datetime(df["Date"], utc=True)

    df["trading_date"] = (
    df["Date"]
    .dt.tz_convert("Asia/Jakarta")
    .dt.date
)

    df = df.sort_values(["symbol", "Date"]).reset_index(drop=True)

    # 2. Validate price consistency
    invalid = (
        (df["High"] < df["Low"])
        | (df["High"] < df["Open"])
        | (df["High"] < df["Close"])
        | (df["Low"] > df["Open"])
        | (df["Low"] > df["Close"])
        | (df["Volume"] < 0)
        | (df[["Open", "High", "Low", "Close"]] <= 0).any(axis=1)
    )

    if invalid.any():
        raise ValueError(
            f"Found {invalid.sum()} records with invalid market values."
        )

    # 3. Remove duplicate stock-date records
    df = df.drop_duplicates(
        subset=["symbol", "Date"], keep="last"
    )

    # 4. Calculate daily return per stock
    df["daily_return_pct"] = (
        df.groupby("symbol")["Close"]
        .pct_change() * 100
    )

    # 5. Calculate intraday price range
    df["intraday_range_pct"] = (
        (df["High"] - df["Low"]) / df["Open"] * 100
    )

    # 6. Estimate daily trading value
    df["turnover_idr"] = df["Close"] * df["Volume"]

    # 7. Add sector mapping later from stocks.yaml
    df["market"] = "Indonesia"
    df["exchange"] = "IDX"
    df["currency"] = "IDR"

    # 8. Save transformed data
    relative_path = source_file.relative_to(RAW_PATH)
    output_file = PROCESSED_PATH / relative_path
    output_file.parent.mkdir(parents=True, exist_ok=True)

    df.to_parquet(output_file, index=False)

    print("\nTRANSFORMATION SUMMARY")
    print(f"Source records: {len(pd.read_parquet(source_file))}")
    print(f"Output records: {len(df)}")
    print(f"Stocks processed: {df['symbol'].nunique()}")
    print(f"Invalid records: {invalid.sum()}")
    print(f"Output: {output_file}")

    print("\nSample transformed data:")
    print(
        df[
            [
                "Date",
                "symbol",
                "Close",
                "daily_return_pct",
                "intraday_range_pct",
                "turnover_idr",
            ]
        ].head(10).to_string(index=False)
    )


if __name__ == "__main__":
    transform_market_data()
