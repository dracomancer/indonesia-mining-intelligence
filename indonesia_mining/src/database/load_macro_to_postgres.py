from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    URL,
    MetaData,
    Table,
)
from sqlalchemy.dialects.postgresql import insert


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "macro"

load_dotenv(PROJECT_ROOT / ".env")

database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5433")),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(database_url)


def latest_parquet(folder, filename):
    files = list(folder.rglob(filename))

    if not files:
        raise FileNotFoundError(
            f"No {filename} found in {folder}"
        )

    return max(files, key=lambda path: path.stat().st_mtime)


def upsert_dataframe(connection, table, df, key_columns):
    records = df.to_dict(orient="records")

    if not records:
        raise ValueError(f"No records to load into {table.name}.")

    update_columns = {
        column: getattr(insert(table).excluded, column)
        for column in df.columns
        if column not in key_columns
    }

    total_affected = 0
    batch_size = 1000

    for start in range(0, len(records), batch_size):
        batch = records[start:start + batch_size]

        statement = insert(table).values(batch)

        statement = statement.on_conflict_do_update(
            index_elements=[
                table.c[column] for column in key_columns
            ],
            set_=update_columns,
        )

        result = connection.execute(statement)
        total_affected += result.rowcount

    return total_affected


def load_macro_to_postgres():
    print("=" * 60)
    print("MACRO DATA POSTGRESQL LOADER")
    print("=" * 60)

    jisdor_file = latest_parquet(
        PROCESSED_PATH / "jisdor",
        "jisdor_processed.parquet",
    )

    bi_rate_file = latest_parquet(
        PROCESSED_PATH / "bi_rate",
        "bi_rate_processed.parquet",
    )

    print("JISDOR source:", jisdor_file)
    print("BI-Rate source:", bi_rate_file)

    jisdor_df = pd.read_parquet(jisdor_file)
    bi_rate_df = pd.read_parquet(bi_rate_file)

    jisdor_columns = [
        "trading_date",
        "currency",
        "nominal",
        "jisdor_rate",
        "buy_rate",
        "sell_rate",
        "source",
        "ingested_at",
    ]

    bi_rate_columns = [
        "effective_date",
        "policy_rate",
        "source",
        "ingested_at",
    ]

    for name, df, required in [
        ("JISDOR", jisdor_df, jisdor_columns),
        ("BI-Rate", bi_rate_df, bi_rate_columns),
    ]:
        missing = set(required) - set(df.columns)

        if missing:
            raise ValueError(
                f"{name} missing columns: {sorted(missing)}"
            )

        if df[required].isnull().any().any():
            raise ValueError(
                f"{name} contains missing values."
            )

    jisdor_df = jisdor_df[jisdor_columns].copy()
    bi_rate_df = bi_rate_df[bi_rate_columns].copy()

    metadata = MetaData()

    jisdor_table = Table(
        "jisdor_rates",
        metadata,
        schema="public",
        autoload_with=engine,
    )

    bi_rate_table = Table(
        "bi_policy_rates",
        metadata,
        schema="public",
        autoload_with=engine,
    )

    with engine.begin() as connection:
        jisdor_affected = upsert_dataframe(
            connection,
            jisdor_table,
            jisdor_df,
            ["trading_date", "currency"],
        )

        bi_rate_affected = upsert_dataframe(
            connection,
            bi_rate_table,
            bi_rate_df,
            ["effective_date"],
        )

        jisdor_total = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM public.jisdor_rates"
        ).scalar_one()

        bi_rate_total = connection.exec_driver_sql(
            "SELECT COUNT(*) FROM public.bi_policy_rates"
        ).scalar_one()

    print("\nPOSTGRESQL UPSERT SUMMARY")
    print("JISDOR input records:", len(jisdor_df))
    print("JISDOR affected rows:", jisdor_affected)
    print("JISDOR database total:", jisdor_total)

    print("\nBI-Rate input records:", len(bi_rate_df))
    print("BI-Rate affected rows:", bi_rate_affected)
    print("BI-Rate database total:", bi_rate_total)

    print("\nStatus: SUCCESS")


if __name__ == "__main__":
    try:
        load_macro_to_postgres()
    finally:
        engine.dispose()
