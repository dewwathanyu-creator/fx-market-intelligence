# Project summary

## Scope and results

The project turns official BOT FX and FRED macro observations into a traceable local warehouse and a six-page Power BI Desktop report. It lets an analyst inspect bilateral THB quotes, compare bank-average USD and EUR performance, review observed-return risk, and see data coverage and refresh context. The report is research support, not a trading or forecasting system.

The pipeline keeps provider IDs, series, quote direction, rate type, units, observation and retrieval dates. Validation rejects duplicate, nonpositive or incompatible FX data. Analytics use explicit baselines, observed-return windows and release-aware rules. The local snapshot has 543 FX rows (three BOT series × 181 observed dates) and 603 FRED macro rows (five series); those figures describe this one warehouse build, not ongoing scale or business impact. The [case study](../docs/CASE_STUDY.md) shows a hand-checkable USD/THB comparison.

## Implementation facts

- A Python and DuckDB pipeline covers three BOT FX series and five FRED macro series, retaining source lineage and separating interbank from commercial-bank average rates.
- A six-page Power BI Desktop report covers FX trends, currency comparison, macro context, volatility, Thailand monitoring and data quality; navigation, filters and drillthrough were checked in Desktop.
- Deterministic tests cover quote inversion, cross-rate compatibility, no-look-ahead macro alignment, warehouse reconciliation and end-to-end sample exports; a clean Python 3.13 check at the QA stage passed 68 tests.
- A scheduled refresh workflow, freshness alerts and a recovery runbook are provided, with the Power BI refresh tracked separately; the workflow still requires GitHub runner configuration before live scheduling.

See the [architecture](../docs/ARCHITECTURE.md), [methodology](../docs/METHODOLOGY.md) and [QA evidence](../docs/QA_REPORT.md) for details and limits. Not measured: trading returns, predictive accuracy, causal findings, live service publication, or production users.
