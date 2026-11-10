# Data Dictionary

## Indonesia Mining Intelligence

**Project:** Indonesia Mining Intelligence
**Database:** PostgreSQL
**Schema:** public, analytics
**Documentation Date:** November 10, 2026

---

# 1. Data Architecture

The project integrates financial market and commodity datasets from multiple sources.

| Data Source           | Instruments                   | Frequency |
| --------------------- | ----------------------------- | --------- |
| Yahoo Finance         | Gold, Copper, Brent Crude Oil | Daily     |
| World Bank Pink Sheet | Nickel, Australian Coal       | Monthly   |

The data is processed through Python ingestion and transformation scripts, stored in PostgreSQL, and modeled using dbt.

---

# 2. Yahoo Finance Commodity Data

**Database Table:** `public.commodity_prices`
**dbt Model:** `analytics.int_commodity_indicators`

## 2.1 Raw and Staging Fields

| Column                 | Description                                                | Unit            |
| ---------------------- | ---------------------------------------------------------- | --------------- |
| price_timestamp        | Original market timestamp                                  | Timestamp       |
| trading_date           | Trading date adjusted to New York market timezone          | Date            |
| symbol                 | Commodity ticker identifier                                | Text            |
| commodity_name         | Commodity name                                             | Text            |
| category               | Commodity classification                                   | Text            |
| unit                   | Price measurement unit                                     | USD per unit    |
| open_price             | Opening price                                              | USD             |
| high_price             | Highest observed price                                     | USD             |
| low_price              | Lowest observed price                                      | USD             |
| close_price            | Closing price                                              | USD             |
| adjusted_close         | Adjusted closing price                                     | USD             |
| volume                 | Trading volume                                             | Contract volume |
| dividends              | Dividend information                                       | Source-defined  |
| stock_splits           | Stock split information                                    | Source-defined  |
| price_change           | Difference between current and previous closing price      | USD             |
| daily_return_pct       | Percentage change in closing price                         | Percentage      |
| intraday_range_pct     | Difference between high and low relative to closing price  | Percentage      |
| sma_20                 | 20-observation simple moving average                       | USD             |
| sma_50                 | 50-observation simple moving average                       | USD             |
| volatility_20d         | Rolling 20-observation standard deviation of daily returns | Percentage      |
| source                 | Original data provider                                     | Text            |
| ingested_at            | Original ingestion timestamp                               | Timestamp       |
| ingestion_processed_at | Processing timestamp                                       | Timestamp       |
| market                 | Market classification                                      | Text            |

## 2.2 Intermediate Analytical Fields

**Model:** `analytics.int_commodity_indicators`

| Column                    | Description                                                             | Unit       |
| ------------------------- | ----------------------------------------------------------------------- | ---------- |
| calculated_sma_20         | Rolling average of the latest 20 closing prices                         | USD        |
| calculated_sma_50         | Rolling average of the latest 50 closing prices                         | USD        |
| calculated_volatility_20d | Rolling sample standard deviation of daily returns over 20 observations | Percentage |
| high_20d                  | Highest high price within the latest 20 observations                    | USD        |
| low_20d                   | Lowest low price within the latest 20 observations                      | USD        |

---

# 3. World Bank Commodity Data

**Database Table:** `public.world_bank_commodity_prices`
**dbt Model:** `analytics.int_world_bank_commodity_indicators`

## 3.1 Source Fields

| Column         | Description                           | Unit               |
| -------------- | ------------------------------------- | ------------------ |
| trading_date   | Monthly observation date              | Date               |
| symbol         | Commodity identifier (COAL or NICKEL) | Text               |
| commodity_name | Commodity name                        | Text               |
| close_price    | Monthly benchmark price               | USD per metric ton |
| unit           | Price measurement unit                | Text               |
| data_source    | Original data provider                | Text               |
| frequency      | Observation frequency                 | Text               |

## 3.2 Intermediate Analytical Fields

| Column             | Description                                                                  | Unit               |
| ------------------ | ---------------------------------------------------------------------------- | ------------------ |
| monthly_return_pct | Percentage change in monthly closing price                                   | Percentage         |
| sma_3m             | Three-month simple moving average                                            | USD per metric ton |
| sma_6m             | Six-month simple moving average                                              | USD per metric ton |
| volatility_3m      | Rolling sample standard deviation of monthly returns over three observations | Percentage         |
| high_12m           | Highest price within the latest 12 observations                              | USD per metric ton |
| low_12m            | Lowest price within the latest 12 observations                               | USD per metric ton |

---

# 4. Commodity Performance Metrics

The project uses the following metrics to support commodity market analysis.

| Metric         | Formula                                                          | Analytical Purpose        |
| -------------- | ---------------------------------------------------------------- | ------------------------- |
| Daily Return   | (Current Close / Previous Close - 1) × 100                       | Daily price movement      |
| Monthly Return | (Current Close / Previous Close - 1) × 100                       | Monthly price movement    |
| SMA 20         | Average of the latest 20 closing prices                          | Short-term trend          |
| SMA 50         | Average of the latest 50 closing prices                          | Medium-term trend         |
| SMA 3M         | Average of the latest 3 monthly closing prices                   | Short-term monthly trend  |
| SMA 6M         | Average of the latest 6 monthly closing prices                   | Medium-term monthly trend |
| Volatility 20D | Sample standard deviation of daily returns over 20 observations  | Daily price variability   |
| Volatility 3M  | Sample standard deviation of monthly returns over 3 observations | Monthly price variability |
| Intraday Range | (High - Low) / Close × 100                                       | Daily trading range       |

---

# 5. Data Source and Instrument Mapping

## 5.1 Yahoo Finance

| Symbol | Commodity       | Category          | Frequency |
| ------ | --------------- | ----------------- | --------- |
| GC=F   | Gold            | Precious Metals   | Daily     |
| HG=F   | Copper          | Industrial Metals | Daily     |
| BZ=F   | Brent Crude Oil | Energy            | Daily     |

## 5.2 World Bank Pink Sheet

| Symbol | Commodity       | Benchmark             | Frequency |
| ------ | --------------- | --------------------- | --------- |
| NICKEL | Nickel          | World Bank Pink Sheet | Monthly   |
| COAL   | Australian Coal | World Bank Pink Sheet | Monthly   |

**Important:** Australian Coal is used as a global benchmark proxy. It does not represent the exact Indonesian domestic coal price or a specific Newcastle futures contract.

---

# 6. Analytical Interpretation

The indicators are used to support the following analytical activities:

- Commodity price trend monitoring.
- Short-term and medium-term price comparisons.
- Commodity volatility assessment.
- Historical price performance analysis.
- Supporting analysis of Indonesian mining equities.

The metrics are descriptive analytical indicators and should not be interpreted as standalone investment recommendations.

---

# 7. Documentation Limitations

1. Some raw database field types and precision specifications are not listed because this document focuses on analytical meaning and units.
2. Yahoo Finance futures prices may differ from spot market prices.
3. World Bank commodity data is published at monthly frequency.
4. Missing historical observations are retained as NULL where applicable.
5. Indicator calculations depend on the available historical observations and their respective rolling windows.
