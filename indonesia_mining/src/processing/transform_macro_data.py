from pathlib import Path
from datetime import datetime, timezone
from decimal import Decimal

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_ROOT = PROJECT_ROOT / "data" / "raw" / "macro"
PROCESSED_ROOT = PROJECT_ROOT / "data" / "processed" / "macro"


def latest_parquet(folder, filename):
    files = list(folder.rglob(filename))

    if not files:
        raise FileNotFoundError(
            f"No {filename} found in {folder}"
        )

    return max(files, key=lambda path: path.stat().st_mtime)


def load_jisdor():
    source_file = latest_parquet(
        RAW_ROOT / "jisdor",
        "jisdor_raw.parquet"
    )

    df = pd.read_parquet(source_file)

    required = [
        "trading_date",
        "mts_subkursasing",
        "nil_subkursasing",
        "beli_subkursasing",
        "jual_subkursasing",
        "source",
        "ingested_at",
    ]

    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(
            f"JISDOR missing columns: {sorted(missing)}"
        )

    processed = pd.DataFrame({
        "trading_date": pd.to_datetime(
            df["trading_date"]
        ).dt.date,
        "currency": df["mts_subkursasing"].str.strip(),
        "nominal": df["nil_subkursasing"].map(Decimal),
        "buy_rate": df["beli_subkursasing"].map(Decimal),
        "sell_rate": df["jual_subkursasing"].map(Decimal),
        "source": df["source"],
        "ingested_at": df["ingested_at"],
    })

    if not (processed["buy_rate"] == processed["sell_rate"]).all():
        raise ValueError(
            "JISDOR buy and sell rates are not identical."
        )

    processed["jisdor_rate"] = processed["buy_rate"]

    if (processed["jisdor_rate"] <= 0).any():
        raise ValueError("Invalid JISDOR rate.")

    if (processed["currency"] != "USD").any():
        raise ValueError("Unexpected JISDOR currency.")

    if processed.duplicated(
        subset=["trading_date", "currency"]
    ).any():
        raise ValueError("Duplicate JISDOR records.")

    return processed.sort_values(
        "trading_date"
    ).reset_index(drop=True), source_file


def load_bi_rate():
    source_file = latest_parquet(
        RAW_ROOT / "bi_rate",
        "bi_rate_raw.parquet"
    )

    df = pd.read_parquet(source_file)

    required = [
        "effective_date",
        "formatted_value",
        "source",
        "ingested_at",
    ]

    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(
            f"BI-Rate missing columns: {sorted(missing)}"
        )

    # Use the original formatted string to avoid float precision errors.
    policy_rates = (
        df["formatted_value"]
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False)
        .str.strip()
        .map(Decimal)
    )

    processed = pd.DataFrame({
        "effective_date": pd.to_datetime(
            df["effective_date"]
        ).dt.date,
        "policy_rate": policy_rates,
        "source": df["source"],
        "ingested_at": df["ingested_at"],
    })

    if (processed["policy_rate"] <= 0).any():
        raise ValueError("Invalid BI-Rate value.")

    if (processed["policy_rate"] > 100).any():
        raise ValueError("BI-Rate outside expected range.")

    if processed["effective_date"].duplicated().any():
        raise ValueError("Duplicate BI-Rate dates.")

    return processed.sort_values(
        "effective_date"
    ).reset_index(drop=True), source_file


def save_processed(df, dataset_name, filename, run_time):
    run_id = run_time.strftime("%Y%m%dT%H%M%SZ")

    output_dir = (
        PROCESSED_ROOT
        / dataset_name
        / f"processing_date={run_time.date()}"
        / f"run_id={run_id}"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / filename
    df.to_parquet(output_file, index=False)

    return output_file


def main():
    run_time = datetime.now(timezone.utc)

    print("=" * 60)
    print("MACRO DATA TRANSFORMATION")
    print("=" * 60)

    jisdor, jisdor_source = load_jisdor()
    bi_rate, bi_rate_source = load_bi_rate()

    jisdor_output = save_processed(
        jisdor,
        "jisdor",
        "jisdor_processed.parquet",
        run_time,
    )

    bi_rate_output = save_processed(
        bi_rate,
        "bi_rate",
        "bi_rate_processed.parquet",
        run_time,
    )

    print("\nJISDOR")
    print("Source:", jisdor_source)
    print("Records:", len(jisdor))
    print("Date range:", jisdor["trading_date"].min(),
          "to", jisdor["trading_date"].max())
    print("Output:", jisdor_output)

    print("\nBI-RATE")
    print("Source:", bi_rate_source)
    print("Records:", len(bi_rate))
    print("Date range:", bi_rate["effective_date"].min(),
          "to", bi_rate["effective_date"].max())
    print("Output:", bi_rate_output)

    print("\nStatus: SUCCESS")


if __name__ == "__main__":
    main()
