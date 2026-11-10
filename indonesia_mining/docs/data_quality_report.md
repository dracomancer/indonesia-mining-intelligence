# Data Quality Report

## Indonesia Mining Intelligence

**Validation Date:** November 10, 2026
**Project:** Indonesia Mining Intelligence
**Database:** PostgreSQL
**Transformation Framework:** dbt

---

## 1. Executive Summary

This report documents the data quality assessment and mathematical validation performed on the commodity datasets used in the Indonesia Mining Intelligence project.

The assessment covers two primary data sources:

- Yahoo Finance: Gold, Copper, and Brent Crude Oil.
- World Bank Pink Sheet: Nickel and Australian Coal.

The validation process focuses on data completeness, duplicate records, date consistency, and mathematical accuracy of calculated indicators.

All tested mathematical indicators produced zero mismatches against their corresponding SQL recalculations.

---

## 2. Data Coverage

### 2.1 Yahoo Finance

| Commodity       | First Observation | Latest Observation | Records |
| --------------- | ----------------- | ------------------ | ------: |
| Brent Crude Oil | 2023-01-03        | 2026-11-09         |     970 |
| Copper          | 2023-01-03        | 2026-11-09         |     970 |
| Gold            | 2023-01-03        | 2026-11-09         |     970 |

Frequency: Daily.

### 2.2 World Bank Pink Sheet

| Commodity       | First Observation | Latest Observation | Records |
| --------------- | ----------------- | ------------------ | ------: |
| Australian Coal | 1960-01-01        | 2026-10-01         |     802 |
| Nickel          | 1960-01-01        | 2026-10-01         |     802 |

Frequency: Monthly.

Note: Australian Coal represents a global commodity benchmark proxy, not an Indonesian domestic coal price or an exact Newcastle futures contract price.

---

## 3. Missing Value Assessment

### 3.1 Yahoo Finance

| Commodity | Total Rows | Missing Return | Missing Range | Missing SMA 20 | Missing SMA 50 | Missing Volatility |
| --------- | ---------: | -------------: | ------------: | -------------: | -------------: | -----------------: |
| Brent     |        970 |              1 |             0 |              0 |              0 |                  2 |
| Copper    |        970 |              1 |             0 |              0 |              0 |                  2 |
| Gold      |        970 |              1 |             0 |              0 |              0 |                  2 |

The missing daily return values are consistent with the absence of a previous observation for the first record.

The initial volatility values require previous return observations to calculate the rolling standard deviation.

### 3.2 World Bank

| Commodity       | Total Rows | Missing Close | Missing Return | Missing SMA 3M | Missing SMA 6M | Missing Volatility |
| --------------- | ---------: | ------------: | -------------: | -------------: | -------------: | -----------------: |
| Australian Coal |        802 |           120 |            121 |            120 |            120 |                122 |
| Nickel          |        802 |             0 |              1 |              0 |              0 |                  2 |

#### Australian Coal Missing Data

The 120 missing closing prices are concentrated entirely between January 1960 and December 1969.

- First valid price observation: January 1970.
- Latest valid price observation: October 2026.
- Total valid closing prices: 682.
- Total missing closing prices: 120.

These missing values originate from unavailable observations in the source dataset.

**Treatment:** Missing values are retained as NULL. No artificial price imputation is performed.

---

## 4. Duplicate Record Validation

Duplicate records were checked using the combination of:

- Commodity symbol
- Trading date

Results:

| Dataset               | Duplicate Records |
| --------------------- | ----------------: |
| Yahoo Finance         |                 0 |
| World Bank Pink Sheet |                 0 |

No duplicate observations were identified.

---

## 5. Date Consistency Validation

The date validation checks:

- Minimum observation date.
- Maximum observation date.
- Number of unique dates.
- Total record count.
- Observations with future dates.

Results:

- All instruments have unique observation dates.
- No duplicate dates were identified.
- No future-dated observations were found.
- Yahoo Finance contains 970 daily observations per instrument.
- World Bank contains 802 monthly observations per instrument.

---

## 6. Mathematical Validation

Calculated indicators were independently recalculated using SQL window functions and compared against the stored values.

The accepted numerical tolerance was 0.000001.

### 6.1 Daily Return

Formula:

Daily Return (%) = ((Current Close / Previous Close) - 1) × 100

Result:

| Commodity | Observations Tested | Mismatches |
| --------- | ------------------: | ---------: |
| Brent     |                 969 |          0 |
| Copper    |                 969 |          0 |
| Gold      |                 969 |          0 |

### 6.2 Simple Moving Average

Indicators tested:

- SMA 20
- SMA 50

All three Yahoo Finance instruments produced zero mismatches for both indicators.

### 6.3 Monthly Return

Formula:

Monthly Return (%) = ((Current Close / Previous Close) - 1) × 100

| Commodity       | Mismatches |
| --------------- | ---------: |
| Australian Coal |          0 |
| Nickel          |          0 |

### 6.4 Volatility

The validation compared stored rolling sample standard deviations against recalculated values.

Indicators tested:

- Yahoo Finance: 20-day rolling volatility.
- World Bank: 3-month rolling volatility.

All tested instruments produced zero mismatches.

### 6.5 Intraday Range

Formula:

Intraday Range (%) = ((High - Low) / Close) × 100

Brent, Copper, and Gold all produced zero mismatches.

---

## 7. Validation Summary

| Validation Area              | Result   |
| ---------------------------- | -------- |
| Yahoo Finance Missing Values | Reviewed |
| World Bank Missing Values    | Reviewed |
| Duplicate Records            | Passed   |
| Date Consistency             | Passed   |
| Daily Return                 | Passed   |
| Monthly Return               | Passed   |
| SMA 20 and SMA 50            | Passed   |
| Volatility 20D               | Passed   |
| Volatility 3M                | Passed   |
| Intraday Range               | Passed   |

All tested mathematical calculations produced zero mismatches.

---

## 8. Known Limitations

1. Yahoo Finance data represents futures market observations and may not represent real-time market quotations.
2. World Bank Pink Sheet data is monthly, so it cannot capture daily commodity price movements.
3. Australian Coal is used as a global benchmark proxy and should not be interpreted as the exact Indonesian coal market price.
4. Missing historical observations are retained as NULL rather than artificially imputed.
5. Mathematical validation confirms calculation consistency but does not independently establish the accuracy of the original market data sources.
6. The current validation covers the commodity datasets and indicators listed in this report, not every component of the entire project pipeline.

---

## 9. Conclusion

The commodity datasets used in Indonesia Mining Intelligence have undergone initial data quality and mathematical validation.

No duplicate records or future-dated observations were identified.

All tested mathematical indicators produced zero mismatches against their SQL recalculations.

Known missing values have been investigated and documented, particularly the unavailable Australian Coal observations between 1960 and 1969.

The datasets are considered suitable for the current commodity analytics implementation, subject to the limitations documented in this report.
