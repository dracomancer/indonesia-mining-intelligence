from pathlib import Path
from datetime import datetime, timezone
import re
import html
import json

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "macro" / "bi_rate"

BI_URL = "https://www.bi.go.id/id/statistik/indikator/bi-rate.aspx"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
    )
}


def fetch_bi_rate():
    response = requests.get(
        BI_URL,
        headers=HEADERS,
        timeout=60
    )

    response.raise_for_status()

    match = re.search(
        r'<input[^>]*id="HiddenFieldChartData"[^>]*value="(.*?)"',
        response.text,
        re.S
    )

    if not match:
        raise ValueError("HiddenFieldChartData not found.")

    return json.loads(html.unescape(match.group(1)))


def transform_records(raw_data, run_time):
    records = []

    for timestamp_ms, rate, formatted_value in raw_data:
        records.append({
            "effective_date": pd.to_datetime(
                timestamp_ms,
                unit="ms",
                utc=True
            ).tz_convert("Asia/Jakarta").date(),
            "policy_rate": float(rate),
            "formatted_value": formatted_value,
            "source": "Bank Indonesia",
            "ingested_at": run_time.isoformat(),
        })

    return pd.DataFrame(records)


def validate_bi_rate(df):
    if df.empty:
        raise ValueError("No BI-Rate records found.")

    if df.isnull().any().any():
        raise ValueError("Missing BI-Rate values detected.")

    if (df["policy_rate"] <= 0).any():
        raise ValueError("Invalid BI-Rate values detected.")

    if df["effective_date"].duplicated().any():
        raise ValueError("Duplicate BI-Rate dates detected.")

    if not df["policy_rate"].between(0, 100).all():
        raise ValueError("BI-Rate outside expected percentage range.")

    return df


def collect_bi_rate_data():
    run_time = datetime.now(timezone.utc)
    run_id = run_time.strftime("%Y%m%dT%H%M%SZ")

    print("=" * 60)
    print("BANK INDONESIA BI-RATE INGESTION")
    print("=" * 60)

    raw_data = fetch_bi_rate()

    df = transform_records(raw_data, run_time)
    df = validate_bi_rate(df)

    df = df.sort_values(
        "effective_date"
    ).reset_index(drop=True)

    output_dir = (
        RAW_PATH
        / f"ingestion_date={run_time.date()}"
        / f"run_id={run_id}"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "bi_rate_raw.parquet"
    df.to_parquet(output_file, index=False)

    print("\nINGESTION SUMMARY")
    print(f"Total records: {len(df)}")
    print(f"Unique dates: {df['effective_date'].nunique()}")
    print(f"Earliest date: {df['effective_date'].min()}")
    print(f"Latest date: {df['effective_date'].max()}")
    print(f"Minimum rate: {df['policy_rate'].min()}%")
    print(f"Maximum rate: {df['policy_rate'].max()}%")
    print(f"Output: {output_file}")
    print("Status: SUCCESS")


if __name__ == "__main__":
    collect_bi_rate_data()
