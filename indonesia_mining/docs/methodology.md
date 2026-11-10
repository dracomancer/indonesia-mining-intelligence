# Data Processing Methodology

## Indonesia Mining Intelligence

**Project:** Indonesia Mining Intelligence
**Documentation Date:** November 10, 2026
**Database:** PostgreSQL
**Transformation Framework:** dbt
**Programming Language:** Python

---

# 1. Project Overview

Indonesia Mining Intelligence is a financial market analytics project designed to monitor Indonesian mining-related equities and their relationship with global commodity market movements.

The project integrates historical stock market data, global commodity benchmarks, and macroeconomic indicators to support financial market monitoring and analytical research.

The current commodity analytics implementation focuses on five instruments:

- Gold
- Copper
- Brent Crude Oil
- Nickel
- Australian Coal

The platform is designed to provide historical price monitoring, trend analysis, return measurement, and volatility assessment.

---

# 2. Data Pipeline Architecture

The project follows a multi-stage data engineering architecture.

## 2.1 Data Ingestion

Data is collected from external financial and economic data providers.

| Source                | Dataset                       | Frequency |
| --------------------- | ----------------------------- | --------- |
| Yahoo Finance         | Gold, Copper, Brent Crude Oil | Daily     |
| World Bank Pink Sheet | Nickel, Australian Coal       | Monthly   |

Python scripts are used to retrieve and prepare the source datasets.

The ingestion process stores raw data in Parquet format to maintain a structured and reproducible data storage workflow.

## 2.2 Data Processing

Raw datasets undergo several processing operations:

1. Data type conversion.
2. Date and timestamp standardization.
3. Missing value handling.
4. Sorting observations by instrument and date.
5. Calculation of price-based indicators.
6. Data validation.
7. Storage of processed datasets in Parquet format.

Missing commodity prices are retained as NULL when source observations are unavailable. Artificial price imputation is not applied.

## 2.3 Data Warehousing

Processed datasets are loaded into PostgreSQL.

The database separates raw source tables from analytical models.

| Layer            | Purpose                              |
| ---------------- | ------------------------------------ |
| Public Schema    | Stores ingested commodity datasets   |
| Analytics Schema | Stores transformed analytical models |

The database serves as the central data source for analytical queries and dashboard visualizations.

## 2.4 Data Transformation

dbt is used to transform source tables into analytical datasets.

The transformation architecture consists of:

- Staging models
- Intermediate models
- Mart models

Staging models standardize source fields and naming conventions.

Intermediate models calculate technical and statistical indicators.

Mart models prepare summarized datasets for dashboard consumption.

---

# 3. Commodity Indicator Methodology

## 3.1 Daily Price Return

Daily return measures the percentage change between consecutive closing prices.

Formula:

Daily Return (%) = ((P_t / P_t-1) - 1) × 100

Where:

- P_t = Current closing price
- P_t-1 = Previous observed closing price

This metric is used to evaluate daily commodity price movements.

## 3.2 Monthly Price Return

Monthly return measures the percentage change between consecutive monthly closing prices.

Formula:

Monthly Return (%) = ((P_t / P_t-1) - 1) × 100

The metric is calculated using monthly World Bank observations.

## 3.3 Simple Moving Average

Simple Moving Average is used to identify historical price trends.

The project implements:

- SMA 20 and SMA 50 for daily commodity data.
- SMA 3M and SMA 6M for monthly commodity data.

Formula:

SMA_n = (P_t + P_t-1 + ... + P_t-n+1) / n

Moving averages help compare short-term and medium-term price trends.

## 3.4 Rolling Volatility

Volatility measures the historical variability of commodity returns.

The project uses sample standard deviation.

Daily volatility:

- Calculated over a 20-observation rolling window.

Monthly volatility:

- Calculated over a 3-observation rolling window.

The calculation uses return percentages rather than raw commodity prices.

Volatility is used to assess historical price variability, not to predict future market movements.

## 3.5 Intraday Range

Intraday range measures the relative difference between the daily high and low prices.

Formula:

Intraday Range (%) = ((High - Low) / Close) × 100

This metric provides an indication of daily trading price dispersion.

---

# 4. Trend Classification

The commodity performance model classifies price trends using moving average relationships.

For Yahoo Finance instruments:

- Short-term moving average: SMA 20.
- Long-term moving average: SMA 50.

For World Bank instruments:

- Short-term moving average: SMA 3M.
- Long-term moving average: SMA 6M.

The World Bank trend classification uses the following logic:

**Bullish**

Current closing price > SMA 3M > SMA 6M.

**Bearish**

Current closing price < SMA 3M < SMA 6M.

**Neutral**

Other combinations of price and moving average relationships.

Trend signals are descriptive indicators and should not be interpreted as standalone investment recommendations.

---

# 5. Historical Performance Analysis

The platform provides historical price analysis across multiple observation periods.

The dashboard supports:

- 3 Months
- 6 Months
- 1 Year
- All History

Historical observations are filtered based on the selected period.

Price charts visualize closing prices and their corresponding moving averages.

Historical performance tables provide access to individual observations and calculated indicators.

---

# 6. Data Quality and Validation

Data validation is performed at multiple stages.

## 6.1 Completeness Checks

Missing values are assessed across important price and indicator fields.

Expected missing values caused by unavailable source observations or insufficient rolling windows are documented rather than automatically imputed.

## 6.2 Duplicate Checks

Records are checked using commodity symbol and observation date.

No duplicate commodity observations were identified in the current validation.

## 6.3 Date Consistency

The validation checks:

- Earliest observation date.
- Latest observation date.
- Unique observation dates.
- Future-dated records.

No future-dated observations were identified in the current validation.

## 6.4 Mathematical Validation

Stored indicators are recalculated using SQL window functions and compared against their stored values.

The validation covers:

- Daily return.
- Monthly return.
- SMA 20.
- SMA 50.
- Volatility 20D.
- Volatility 3M.
- Intraday range.

All tested indicators produced zero mismatches within a numerical tolerance of 0.000001.

Refer to `data_quality_report.md` for detailed results.

---

# 7. Dashboard and Analytical Consumption

Streamlit is used to provide an interactive dashboard for market monitoring.

The commodity analytics section includes:

1. Global Commodity Market Overview.
2. Commodity performance indicators.
3. Historical price development.
4. Moving average visualization.
5. Historical commodity data tables.

The dashboard retrieves analytical datasets from PostgreSQL through SQL queries.

The visualizations are designed to support market monitoring and historical analysis.

---

# 8. Methodological Limitations

1. Yahoo Finance futures observations may differ from spot commodity prices.
2. World Bank Pink Sheet observations are monthly and cannot represent daily market movements.
3. Australian Coal is a global benchmark proxy rather than an exact Indonesian domestic coal price.
4. Historical volatility describes past variability and does not guarantee future volatility.
5. Moving averages are lagging indicators.
6. Trend classifications are rule-based and do not incorporate all market fundamentals.
7. Mathematical validation confirms calculation consistency but does not independently verify source data accuracy.

---

# 9. Future Development

Potential extensions include:

- Integration of USD/IDR JISDOR exchange rate data.
- Cross-market analysis between Indonesian mining equities and global commodity prices.
- Commodity-equity correlation analysis.
- Rolling correlation analysis.
- Macroeconomic indicator integration.
- Automated data quality monitoring.
- AI-assisted financial market intelligence.

These extensions aim to improve the platform's ability to identify relationships between commodity markets, Indonesian equities, and macroeconomic conditions.
