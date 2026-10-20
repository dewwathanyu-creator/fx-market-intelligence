# FX Market Intelligence Dashboard

An auditable project for exploring official FX and macroeconomic observations. Python collects and validates Bank of Thailand (BOT) and FRED series, DuckDB stores the analytical model, and a six-page Power BI project presents the results. The report supports research; it does not execute trades or issue forecasts.

**Current scope:** USD/THB interbank, USD/THB and EUR/THB commercial-bank average quotes, plus five FRED macro series. The local Desktop snapshot shown below covers 5 January–30 September 2026 and was built on 16 October 2026. Source dates and warehouse build time are separate; this snapshot is not a live market feed. Official NEER/REER and P1 ECB/BIS series are not loaded.

## Review the result

Open [the editable Power BI project](dashboard/powerbi/FX%20Market%20Intelligence%20Dashboard.pbip) in Power BI Desktop. The six images are actual Desktop screenshots from the project package, rather than the illustrative [design mockups](dashboard/mockups/). They precede the later UI polish; the PBIP is the current editable version, and [the design system](docs/POWERBI_DESIGN_SYSTEM.md) records its visual rules:


| Page | Purpose | Evidence |
| --- | --- | --- |
| Market Overview | USD/THB interbank quote, change and volatility | [Screenshot](dashboard/screenshots/final/market-overview.png) |
| Currency Explorer | Comparable USD and EUR bank-average quotes | [Screenshot](dashboard/screenshots/final/currency-explorer.png) |
| Macro Drivers | Separate FX and FRED charts with explicit units | [Screenshot](dashboard/screenshots/final/macro-drivers.png) |
| Risk & Volatility | Observed-return volatility and quote drawdown | [Screenshot](dashboard/screenshots/final/risk-volatility.png) |
| Thailand FX Monitor | Bilateral THB quotes and pending NEER/REER | [Screenshot](dashboard/screenshots/final/thailand-fx-monitor.png) |
| Data Quality & Research | Coverage, lineage and freshness | [Screenshot](dashboard/screenshots/final/data-quality-research.png) |

The screenshots include the Power BI Desktop account name in the application chrome. Check this before republishing them outside your own environment. [Desktop interaction evidence](docs/DASHBOARD_QA.md) records slicer, tooltip, navigation, drillthrough and Back-button checks.

## Reproduce locally

Use Python 3.13 and Power BI Desktop on Windows. From the project root:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e '.[dev]'
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
```

The tests use controlled fixtures and need no credentials. They cover ingestion, validation, warehouse, financial calculations, BI parity, automation behavior and a complete sample pipeline. [End-to-end QA](docs/QA_REPORT.md) records a clean Python 3.13 installation and 68 passing tests before this packaging task.

For a **new live collection**, create a Git-ignored `.env` beside this README using names from [.env.example](.env.example): `FRED_API_KEY` and `BOT_API_KEY`. Do not commit or paste the values. Run `python -m fx_intelligence.orchestration.refresh refresh --root .` from the activated environment. It writes local raw data, the DuckDB warehouse and Power BI input workbook. Then open `dashboard/powerbi/FX Market Intelligence Dashboard.pbip` in Power BI Desktop, select **Home → Refresh**, and inspect all pages and source dates. [The runbook](docs/RUNBOOK.md) explains overlap, staleness alerts, failure recovery and the separate Power BI refresh. A local build does not automatically refresh Desktop or the Power BI service.

The committed PBIP contains the report and semantic-model definitions; its generated data workbook is intentionally Git-ignored. To recreate the displayed live snapshot, valid BOT/FRED access and provider observations are required. The offline fixture tests reproduce the pipeline behavior, not the exact historical screenshot values. The scheduled GitHub workflow also requires a persistent Windows runner, repository variable and secrets; it has not been activated by a push.

## Methods and interpretation

USD/THB is **THB per USD**: a rising quote means THB depreciation. The interbank rate and customer bank-average rate remain distinct. Performance uses observed quotes and explicit baselines; realized volatility uses sample standard deviation of daily log returns × √252 over observed-return windows. Missing raw dates are not filled. FRED observation dates do not establish release dates, so the project does not infer causal or historical release-aware macro effects from them. [Methodology](docs/METHODOLOGY.md), [data dictionary](docs/DATA_DICTIONARY.md), [architecture](docs/ARCHITECTURE.md) and [source registry](config/sources/registry.yaml) give the detailed contracts.

The [USD/THB case study](docs/CASE_STUDY.md) uses a dated local BOT extract with a reproducible query, hand-checkable arithmetic and a EUR/THB comparison. [Project summary](reports/PROJECT_SUMMARY.md) uses measured implementation facts only. [Project specification](docs/PROJECT_SPEC.md) and [roadmap](docs/TASK_ROADMAP.md) distinguish the original plan from delivered scope.
