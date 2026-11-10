# Indonesia Mining Intelligence

**A Financial Market Data Engineering & Analytics Platform**

Indonesia Mining Intelligence is a data engineering and analytics project designed to monitor Indonesian mining-related equities and global commodity markets.

The platform integrates historical stock market data and international commodity benchmarks into a centralized analytical database. It transforms raw financial data into structured indicators and interactive visualizations to support financial market monitoring and research.

The project explores how commodity price movements can provide additional context for understanding Indonesia's mining sector.

---

## Project Objectives

The project aims to:

- Build an end-to-end financial market data pipeline.
- Integrate Indonesian mining equities with global commodity benchmarks.
- Develop structured financial datasets for analytical consumption.
- Calculate historical performance and market indicators.
- Provide an interactive dashboard for market monitoring.
- Establish a foundation for cross-market and macroeconomic analysis.

---

## Key Features

### 1. Indonesian Mining Equity Monitoring

Historical stock price data from selected Indonesian mining and energy-related companies.

Selected companies:

| Ticker  | Company                     | Sector        |
| ------- | --------------------------- | ------------- |
| ADRO.JK | Alamtri Resources Indonesia | Coal          |
| PTBA.JK | Bukit Asam                  | Coal          |
| ITMG.JK | Indo Tambangraya Megah      | Coal          |
| ANTM.JK | Aneka Tambang               | Nickel & Gold |
| INCO.JK | Vale Indonesia              | Nickel        |
| NCKL.JK | Trimegah Bangun Persada     | Nickel        |
| MDKA.JK | Merdeka Copper Gold         | Gold & Copper |
| BRMS.JK | Bumi Resources Minerals     | Gold & Copper |
| AMMN.JK | Amman Mineral Internasional | Copper & Gold |
| MEDC.JK | Medco Energi Internasional  | Oil & Gas     |

### 2. Global Commodity Intelligence

The platform integrates five commodity instruments from two data providers.

| Commodity       | Data Source           | Frequency |
| --------------- | --------------------- | --------- |
| Gold            | Yahoo Finance         | Daily     |
| Copper          | Yahoo Finance         | Daily     |
| Brent Crude Oil | Yahoo Finance         | Daily     |
| Nickel          | World Bank Pink Sheet | Monthly   |
| Australian Coal | World Bank Pink Sheet | Monthly   |

The combination of daily and monthly observations supports both short-term market monitoring and long-term commodity trend analysis.

### 3. Financial Market Indicators

The analytical pipeline calculates:

- Daily and monthly returns.
- Simple Moving Averages.
- Rolling historical volatility.
- Intraday price range.
- Historical price highs and lows.
- Rule-based trend classification.
- Historical performance comparisons.

### 4. Interactive Dashboard

The Streamlit dashboard currently provides five main sections:

1. Market Overview
2. Equity Analysis
3. Stock Performance Comparison
4. Commodity Intelligence
5. Pipeline Information

---

## Data Architecture

The project follows a layered data engineering workflow.

```text
External Data Sources
        |
        v
Python Data Ingestion
        |
        v
Raw Data Storage (Parquet)
        |
        v
Data Processing
        |
        v
PostgreSQL Data Warehouse
        |
        v
dbt Transformation
        |
        v
Analytical Data Models
        |
        v
Streamlit Dashboard
```

### Technology Stack

| Component            | Technology                 |
| -------------------- | -------------------------- |
| Programming Language | Python                     |
| Data Collection      | yfinance, Requests, Pandas |
| Data Processing      | Pandas, NumPy              |
| Storage Format       | Parquet                    |
| Database             | PostgreSQL                 |
| Data Transformation  | dbt                        |
| Dashboard            | Streamlit                  |
| Visualization        | Plotly                     |
| Version Control      | Git & GitHub               |

---

## Data Warehouse Design

The database separates source datasets and analytical models.

### Source Tables

| Schema | Table                       | Description                          |
| ------ | --------------------------- | ------------------------------------ |
| public | stock_prices                | Historical Indonesian equity prices  |
| public | commodity_prices            | Daily commodity futures observations |
| public | world_bank_commodity_prices | Monthly World Bank commodity prices  |

### Analytical Models

The dbt project uses staging, intermediate, and mart layers.

**Staging**

- `stg_stock_prices`
- `stg_commodity_prices`
- `stg_world_bank_commodity_prices`

**Intermediate**

- `int_stock_indicators`
- `int_commodity_indicators`
- `int_world_bank_commodity_indicators`

**Marts**

- `mart_stock_performance`
- `mart_stock_history`
- `mart_historical_performance`
- `mart_commodity_performance`
- `mart_world_bank_commodity_performance`

---

## Data Coverage

Current validated datasets:

| Dataset                    | Records | Frequency |
| -------------------------- | ------: | --------- |
| Indonesian Mining Equities |   8,974 | Daily     |
| Yahoo Finance Commodities  |   2,910 | Daily     |
| World Bank Commodities     |   1,604 | Monthly   |

**Coverage period:**

- Equity data: January 2023 – November 2026.
- Yahoo Finance commodities: January 2023 – November 2026.
- World Bank commodities: January 1960 – October 2026.

Record counts represent the current collected datasets and may change as new observations are ingested.

---

## Data Quality & Validation

The project includes dedicated data quality checks covering:

- Missing observations.
- Duplicate records.
- Date consistency.
- Historical coverage.
- Indicator calculation accuracy.

The current commodity validation identified no duplicate observations or future-dated records.

All tested commodity indicators produced zero calculation mismatches within a numerical tolerance of 0.000001.

Missing historical observations are retained as NULL when source data is unavailable.

For detailed results, see:

- [Data Quality Report](indonesia_mining/docs/data_quality_report.md)
- [Data Dictionary](indonesia_mining/docs/data_dictionary.md)
- [Methodology](indonesia_mining/docs/methodology.md)
- [Data Sources](indonesia_mining/docs/data_sources.md)

---

## Repository Structure

```text

financial-market-idr-monitoring/
|
|-- indonesia_mining/
|   |-- config/
|   |-- data/
|   |   |-- raw/
|   |   |-- processed/
|   |   |-- warehouse/
|   |-- dashboard/
|   |   |-- app.py
|   |-- docs/
|   |-- src/
|   |   |-- ingestion/
|   |   |-- processing/
|   |   |-- database/
|   |-- tests/
|   |-- notebooks/
|   |-- requirements.txt
|
|-- mining_analytics/
|   |-- models/
|   |   |-- staging/
|   |   |-- intermediate/
|   |   |-- marts/
|   |-- tests/
|   |-- dbt_project.yml
|
|-- check_commodity_db.py
|-- check_data_quality.py
|-- check_indicator_validation.py
|-- .gitignore
|-- README.md
```

---

## Getting Started

### Prerequisites

- Python 3.13
- PostgreSQL 16
- Git
- dbt
- Streamlit

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/financial-market-idr-monitoring.git
cd financial-market-idr-monitoring
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate the environment.

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r indonesia_mining/requirements.txt
```

### 4. Configure Environment Variables

Create an `.env` file inside the `indonesia_mining` directory.

Configure the following variables according to your local PostgreSQL setup:

```env
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5433
DB_NAME=mining_market
```

Never commit your actual database credentials to GitHub.

### 5. Run the Dashboard

From the repository root:

```bash
streamlit run indonesia_mining/dashboard/app.py
```

The dashboard will be available at:

```text
http://localhost:8501
```

Additional ingestion and transformation instructions will be documented as the project setup is finalized.

---

## Methodological Limitations

- Yahoo Finance futures prices may differ from spot commodity prices.
- World Bank Pink Sheet data is monthly rather than daily.
- Australian Coal is used as a global benchmark proxy, not an Indonesian domestic coal price.
- Historical volatility and moving averages are descriptive indicators, not standalone forecasting tools.
- Mathematical validation confirms calculation consistency, not independent source accuracy.
- Commodity and equity observations come from different markets and calendars.

---

## Roadmap

| Feature                               | Status      |
| ------------------------------------- | ----------- |
| Indonesian mining equity ingestion    | Implemented |
| Yahoo Finance commodity ingestion     | Implemented |
| World Bank commodity ingestion        | Implemented |
| PostgreSQL data warehouse             | Implemented |
| dbt analytical models                 | Implemented |
| Streamlit dashboard                   | Implemented |
| Commodity data quality validation     | Implemented |
| USD/IDR JISDOR integration            | Planned     |
| Commodity-equity correlation analysis | Planned     |
| Rolling correlation analysis          | Planned     |
| Macroeconomic data integration        | Planned     |
| Automated pipeline orchestration      | Planned     |

---

## Disclaimer

This project is developed for educational, analytical, and portfolio purposes.

It does not provide investment advice, trading signals, or guaranteed market forecasts.

All market observations are subject to the availability, methodology, and limitations of their original data providers.
