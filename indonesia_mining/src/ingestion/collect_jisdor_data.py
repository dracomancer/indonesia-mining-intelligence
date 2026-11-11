from pathlib import Path
from datetime import datetime, date, timezone
from calendar import monthrange
import xml.etree.ElementTree as ET

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "macro" / "jisdor"

API_URL = (
    "https://www.bi.go.id/biwebservice/"
    "wskursbi.asmx/getSubKursJisdor3"
)

START_DATE = date(2023, 1, 1)
CURRENCY = "USD"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/131.0.0.0 Safari/537.36"
    )
}


def get_month_ranges(start_date, end_date):
    """Generate monthly date ranges."""
    current = start_date

    while current <= end_date:
        last_day = monthrange(current.year, current.month)[1]
        month_end = min(
            date(current.year, current.month, last_day),
            end_date
        )

        yield current, month_end

        if month_end == end_date:
            break

        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)


def extract_table_records(xml_content):
    """Extract Table records from BI XML DataSet."""
    root = ET.fromstring(xml_content)

    rows = [
        element for element in root.iter()
        if element.tag.split("}")[-1] == "Table"
    ]

    records = []

    for row in rows:
        record = {
            child.tag.split("}")[-1]: (child.text or "").strip()
            for child in row
        }

        records.append(record)

    return records


def fetch_jisdor(start_date, end_date, session):
    """Fetch JISDOR records for one date range."""
    params = {
        "mts": CURRENCY,
        "startDate": start_date.strftime("%m/%d/%Y"),
        "endDate": end_date.strftime("%m/%d/%Y"),
    }

    response = session.get(
        API_URL,
        params=params,
        timeout=60
    )

    response.raise_for_status()

    return extract_table_records(response.content)


def validate_jisdor(df):
    """Validate raw JISDOR records."""
    required_columns = [
        "id_subkursasing",
        "lnk_subkursasing",
        "nil_subkursasing",
        "beli_subkursasing",
        "jual_subkursasing",
        "tgl_subkursasing",
        "mts_subkursasing",
    ]

    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required fields: {sorted(missing)}"
        )

    if df[required_columns].isnull().any().any():
        raise ValueError("Missing values found in JISDOR records.")

    df["trading_date"] = pd.to_datetime(
        df["tgl_subkursasing"],
        utc=True
    ).dt.tz_convert("Asia/Jakarta").dt.date

    df["exchange_rate"] = pd.to_numeric(
        df["beli_subkursasing"],
        errors="raise"
    )

    if (df["exchange_rate"] <= 0).any():
        raise ValueError("Invalid JISDOR exchange rate detected.")

    if (df["nil_subkursasing"].astype(float) <= 0).any():
        raise ValueError("Invalid currency nominal detected.")

    if (df["mts_subkursasing"].str.strip() != CURRENCY).any():
        raise ValueError("Unexpected currency found.")

    if df["trading_date"].duplicated().any():
        raise ValueError("Duplicate JISDOR dates detected.")

    if df["id_subkursasing"].duplicated().any():
        raise ValueError("Duplicate JISDOR IDs detected.")

    return df


def collect_jisdor_data():
    run_time = datetime.now(timezone.utc)
    run_id = run_time.strftime("%Y%m%dT%H%M%SZ")
    today = date.today()

    output_dir = (
        RAW_PATH
        / f"ingestion_date={run_time.date()}"
        / f"run_id={run_id}"
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    all_records = []

    print("=" * 60)
    print("BANK INDONESIA JISDOR INGESTION")
    print("=" * 60)

    with requests.Session() as session:
        session.headers.update(HEADERS)

        for start_date, end_date in get_month_ranges(
            START_DATE, today
        ):
            print(
                f"Collecting {start_date} to {end_date}..."
            )

            records = fetch_jisdor(
                start_date,
                end_date,
                session
            )

            print(f"Records collected: {len(records)}")

            all_records.extend(records)

    if not all_records:
        raise RuntimeError("No JISDOR data collected.")

    df = pd.DataFrame(all_records)

    df["source"] = "Bank Indonesia"
    df["ingested_at"] = run_time.isoformat()

    df = validate_jisdor(df)

    df = df.sort_values(
        "trading_date"
    ).reset_index(drop=True)

    output_file = output_dir / "jisdor_raw.parquet"
    df.to_parquet(output_file, index=False)

    print("\nINGESTION SUMMARY")
    print(f"Total records: {len(df)}")
    print(f"Unique dates: {df['trading_date'].nunique()}")
    print(f"Currency: {df['mts_subkursasing'].unique().tolist()}")
    print(f"Earliest date: {df['trading_date'].min()}")
    print(f"Latest date: {df['trading_date'].max()}")
    print(f"Output: {output_file}")
    print("Status: SUCCESS")


if __name__ == "__main__":
    collect_jisdor_data()
