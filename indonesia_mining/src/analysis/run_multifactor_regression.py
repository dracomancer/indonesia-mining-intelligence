
from pathlib import Path
import os
import time

import pandas as pd
import statsmodels.api as sm
from dotenv import load_dotenv
from sqlalchemy import create_engine, URL

# 1. Database connection
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

database_url = URL.create(
    "postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", 5433)),
    database=os.getenv("DB_NAME"),
)

engine = create_engine(database_url)

# 2. Load data once
query = """
SELECT
    symbol, trading_date, calendar_gap_days,
    total_return_pct, brent_return_pct,
    copper_return_pct, gold_return_pct,
    jisdor_return_pct, bi_rate_change_bps
FROM analytics.int_mining_equity_regression_panel
ORDER BY symbol, trading_date
"""

print("Loading regression panel...", flush=True)
df = pd.read_sql(query, engine)
engine.dispose()

print(
    f"Loaded {len(df):,} observations | "
    f"{df['symbol'].nunique()} stocks",
    flush=True
)

TARGET = "total_return_pct"
FEATURES = [
    "brent_return_pct",
    "copper_return_pct",
    "gold_return_pct",
    "jisdor_return_pct",
    "bi_rate_change_bps",
    "calendar_gap_days",
]

OUTPUT_DIR = PROJECT_ROOT / "data" / "processed" / "regression"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# 3. Regression function
def run_regression(data, sample_name):
    coefficients = []
    summaries = []

    symbols = sorted(data["symbol"].dropna().unique())
    total = len(symbols)

    for index, symbol in enumerate(symbols, start=1):
        group = data.loc[data["symbol"] == symbol]
        model_data = group[[TARGET] + FEATURES].dropna()

        if len(model_data) <= len(FEATURES) + 10:
            print(f"[{index}/{total}] {symbol}: skipped", flush=True)
            continue

        X = sm.add_constant(model_data[FEATURES])
        y = model_data[TARGET]

        # Fit OLS once
        fitted = sm.OLS(y, X).fit()

        # HAC covariance calculated from existing OLS fit
        model = fitted.get_robustcov_results(
            cov_type="HAC",
            maxlags=5
        )

        ci = model.conf_int()

        for i, variable in enumerate(X.columns):
            coefficients.append({
                "sample": sample_name,
                "symbol": symbol,
                "variable": variable,
                "coefficient": model.params[i],
                "std_error": model.bse[i],
                "t_stat": model.tvalues[i],
                "p_value": model.pvalues[i],
                "ci_lower": ci[i, 0],
                "ci_upper": ci[i, 1],
            })

        summaries.append({
            "sample": sample_name,
            "symbol": symbol,
            "observations": int(model.nobs),
            "r_squared": fitted.rsquared,
            "adjusted_r_squared": fitted.rsquared_adj,
            "aic": fitted.aic,
        })

        print(
            f"[{index}/{total}] {symbol}: "
            f"{len(model_data)} observations completed",
            flush=True
        )

    return coefficients, summaries


# 4. Full sample
start = time.time()

print("\n=== FULL SAMPLE ===", flush=True)
full_coef, full_summary = run_regression(
    df, "full_sample"
)

# 5. Robustness sample
print("\n=== GAP <= 3 DAYS ===", flush=True)

short_df = df[df["calendar_gap_days"] <= 3].copy()

short_coef, short_summary = run_regression(
    short_df, "gap_le_3_days"
)

# 6. Export
coefficients = pd.DataFrame(full_coef + short_coef)
summaries = pd.DataFrame(full_summary + short_summary)

coefficients.to_csv(
    OUTPUT_DIR / "regression_coefficients.csv",
    index=False
)

summaries.to_csv(
    OUTPUT_DIR / "regression_model_summary.csv",
    index=False
)

elapsed = time.time() - start

print("\n=== REGRESSION COMPLETED ===", flush=True)
print(f"Total time: {elapsed:.2f} seconds")
print(f"Models completed: {len(summaries)}")
print(f"Results: {OUTPUT_DIR}")
