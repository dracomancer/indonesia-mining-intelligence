# Data Sources Documentation

## Indonesia Mining Intelligence

**Documentation Date:** November 10, 2026

---

# 1. Overview

Indonesia Mining Intelligence integrates financial market and commodity price datasets from external data providers.

The current commodity analytics pipeline uses two primary data sources:

1. Yahoo Finance
2. World Bank Commodity Price Data (Pink Sheet)

Each source provides different market perspectives and observation frequencies.

Yahoo Finance provides daily futures market observations, while the World Bank Pink Sheet provides monthly international commodity benchmark prices.

---

# 2. Yahoo Finance

## 2.1 Source Description

Yahoo Finance is used to retrieve historical commodity futures market data.

The project uses Yahoo Finance data through the `yfinance` Python library.

Source website:

https://finance.yahoo.com/

Python library:

https://github.com/ranaroussi/yfinance

## 2.2 Instrument Mapping

| Symbol | Commodity       | Market Instrument       | Unit           | Frequency |
| ------ | --------------- | ----------------------- | -------------- | --------- |
| GC=F   | Gold            | Gold Futures            | USD/troy ounce | Daily     |
| HG=F   | Copper          | Copper Futures          | USD/pound      | Daily     |
| BZ=F   | Brent Crude Oil | Brent Crude Oil Futures | USD/barrel     | Daily     |

## 2.3 Data Fields

The ingestion process retrieves the following information where available:

- Open price
- High price
- Low price
- Close price
- Adjusted close
- Trading volume
- Dividends
- Stock splits

Additional analytical indicators are calculated during processing.

## 2.4 Data Coverage

The historical collection starts from January 2023.

The latest available observation depends on the source's market data availability and trading calendar.

The current validated dataset contains:

| Commodity       |   Records |
| --------------- | --------: |
| Gold            |       970 |
| Copper          |       970 |
| Brent Crude Oil |       970 |
| **Total**       | **2,910** |

Data coverage:

January 3, 2023 – November 9, 2026.

## 2.5 Data Considerations

Yahoo Finance futures data has several limitations:

1. Futures prices may differ from spot market prices.
2. Trading dates follow the relevant futures market calendar.
3. Trading volume represents the reported futures market volume, not Indonesian physical commodity transactions.
4. Historical observations may be subject to source revisions or availability changes.

The dataset is therefore used as a market benchmark for historical commodity price analysis.

---

# 3. World Bank Commodity Price Data (Pink Sheet)

## 3.1 Source Description

The World Bank Commodity Price Data, commonly known as the Pink Sheet, provides historical international commodity price information.

The project uses the monthly historical price workbook published by the World Bank.

Source page:

https://www.worldbank.org/en/research/commodity-markets

Historical workbook:

https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx

## 3.2 Instrument Mapping

| Symbol | Commodity       | Benchmark               | Unit           | Frequency |
| ------ | --------------- | ----------------------- | -------------- | --------- |
| NICKEL | Nickel          | World Bank Nickel Price | USD/metric ton | Monthly   |
| COAL   | Australian Coal | Coal, Australian        | USD/metric ton | Monthly   |

## 3.3 Data Fields

The ingestion process extracts:

- Observation date
- Commodity symbol
- Commodity name
- Closing price
- Measurement unit
- Data source
- Observation frequency

The monthly observation dates are standardized to the first day of each month for database storage.

## 3.4 Data Coverage

The historical dataset covers January 1960 to October 2026.

| Commodity       | Total Records | Valid Prices |
| --------------- | ------------: | -----------: |
| Nickel          |           802 |          802 |
| Australian Coal |           802 |          682 |
| **Total**       |     **1,604** |    **1,484** |

Australian Coal observations are unavailable from January 1960 through December 1969.

These unavailable observations are retained as NULL rather than being artificially estimated.

## 3.5 Data Considerations

The World Bank Pink Sheet provides monthly benchmark prices rather than daily exchange-traded futures prices.

Important considerations:

1. Monthly data cannot capture daily price fluctuations.
2. Australian Coal is used as an international coal benchmark proxy.
3. The Australian Coal benchmark should not be interpreted as the exact Indonesian domestic coal selling price.
4. Historical benchmark prices may differ from prices negotiated in individual physical commodity contracts.

The dataset is primarily used for long-term commodity trend and historical performance analysis.

---

# 4. Data Source Comparison

| Characteristic      | Yahoo Finance                | World Bank Pink Sheet              |
| ------------------- | ---------------------------- | ---------------------------------- |
| Data Type           | Futures market observations  | International commodity benchmarks |
| Frequency           | Daily                        | Monthly                            |
| Historical Coverage | 2023–2026                    | 1960–2026                          |
| Commodities         | Gold, Copper, Brent          | Nickel, Australian Coal            |
| Main Use            | Short-term market monitoring | Long-term price analysis           |
| Storage Format      | Parquet                      | Parquet                            |
| Database            | PostgreSQL                   | PostgreSQL                         |

The two sources complement each other by providing different perspectives on commodity market behavior.

However, their observations should not be directly compared without considering differences in market instruments, measurement units, and observation frequencies.

---

# 5. Data Storage and Lineage

The ingestion workflow stores raw datasets in Parquet format before loading them into PostgreSQL.

The current storage structure separates the source datasets by provider and commodity category.

Database tables:

| Database Table                     | Source                |
| ---------------------------------- | --------------------- |
| public.commodity_prices            | Yahoo Finance         |
| public.world_bank_commodity_prices | World Bank Pink Sheet |

Analytical models are maintained in the `analytics` schema through dbt transformations.

This structure maintains traceability between the original data source and the resulting analytical datasets.

---

# 6. Source Reliability and Limitations

The project uses publicly accessible datasets for analytical and educational purposes.

The following considerations apply:

- Data availability depends on the original provider.
- Historical observations may be revised by the source.
- Different providers may use different pricing conventions.
- Commodity benchmarks do not necessarily represent actual transaction prices.
- Analytical results should be interpreted within the limitations of each dataset.

The project does not claim to provide official exchange settlement data or real-time institutional trading information.

---

# 7. Future Data Source Integration

The project is designed to support additional financial and macroeconomic datasets.

Potential future integrations include:

| Data Source              | Dataset                          | Analytical Purpose         |
| ------------------------ | -------------------------------- | -------------------------- |
| Bank Indonesia           | JISDOR USD/IDR                   | Exchange rate monitoring   |
| Indonesia Stock Exchange | Listed company market data       | Indonesian equity analysis |
| World Bank               | Additional commodity benchmarks  | Commodity market expansion |
| BPS                      | Macroeconomic indicators         | Economic context           |
| Bank Indonesia           | Monetary and economic indicators | Monetary policy analysis   |

These integrations are planned extensions and are not considered part of the currently implemented commodity pipeline.
