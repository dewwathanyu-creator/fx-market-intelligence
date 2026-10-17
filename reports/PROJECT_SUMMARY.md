# Project summary

## What this project demonstrates

The project turns official BOT FX and FRED macro observations into a traceable local warehouse and a six-page Power BI Desktop report. It lets an analyst inspect bilateral THB quotes, compare bank-average USD and EUR performance, review observed-return risk, and see data coverage and refresh context. The report is research support, not a trading or forecasting system.

The pipeline keeps provider IDs, series, quote direction, rate type, units, observation and retrieval dates. Validation rejects duplicate, nonpositive or incompatible FX data. Analytics use explicit baselines, observed-return windows and release-aware rules. The local snapshot has 543 FX rows (three BOT series × 181 observed dates) and 603 FRED macro rows (five series); those figures describe this one warehouse build, not ongoing scale or business impact. The [case study](../docs/CASE_STUDY.md) shows a hand-checkable USD/THB comparison.

## Highlights

- Built a Python and DuckDB pipeline for three BOT FX series and five FRED macro series, retaining source lineage and separating interbank from commercial-bank average rates.
- Developed a six-page Power BI Desktop report covering FX trends, currency comparison, macro context, volatility, Thailand monitoring and data quality; checked navigation, filters and drillthrough in Desktop.
- Implemented deterministic tests for quote inversion, cross-rate compatibility, no-look-ahead macro alignment, warehouse reconciliation and end-to-end sample exports; the Task 13 clean Python 3.13 check passed 68 tests.
- Added a scheduled refresh workflow design, freshness alerts and a recovery runbook, with the Power BI refresh tracked separately; the workflow still requires GitHub runner configuration before live scheduling.

See the [architecture](../docs/ARCHITECTURE.md), [methodology](../docs/METHODOLOGY.md) and [QA evidence](../docs/QA_REPORT.md) for details and limits. Not measured: trading returns, predictive accuracy, causal findings, live service publication, or production users.
