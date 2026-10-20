# FX Market Intelligence Dashboard: Architecture

The logical flow, repository layout, data contracts and component boundaries of the FX pipeline, from source adapters to the Power BI semantic model.

## Table of Contents

- [Logical flow](#logical-flow)
- [Delivered implementation](#delivered-implementation)
- [Repository target](#repository-target)
- [Data contracts and grain](#data-contracts-and-grain)
- [Component boundaries](#component-boundaries)
- [Technology decisions](#technology-decisions)

---

## Logical flow

```text
BOT / FRED (P0) + ECB / BIS / BOT statistics (P1)
                    |
          Python source adapters
      authentication · retry · backoff · logs
                    |
       immutable raw JSON / Parquet
           + retrieval metadata
                    |
       validation and quarantine
          + canonical normalization
                    |
      DuckDB staging and star schema
                    |
         analytics marts / SQL views
              /              \
     Python metrics         Power BI model
              \              /
            reports and research
```

Raw data remains auditable. A failed validation records a quality issue and does not silently enter an analytics mart. Collection, transformation, analytical computation, and BI refresh are independently rerunnable. The local warehouse uses DuckDB; the incremental schedule is defined in Work package 12 and requires separate activation.

## Delivered implementation

The repository now has BOT and FRED collectors, canonical validation and quarantine, FX transformations, DuckDB facts/dimensions and analytical views, tested performance/risk/macro modules, a Power BI semantic model and six-page PBIP, and an incremental refresh orchestrator. Fixture-based end-to-end and clean-install evidence is in [QA_REPORT.md](QA_REPORT.md). The GitHub Actions schedule is a deployable definition; it is not active until a repository push and persistent runner configuration. Power BI Desktop refresh remains a separate user action. ECB, BIS and official NEER/REER remain planned extensions, not populated warehouse series.

## Repository target

```text
README.md                         # Work package 01: setup and project entry point
pyproject.toml                    # Work package 01: Python/dependency/tool configuration
.env.example                      # Work package 01: names only, never secrets
.github/workflows/                # Work package 01 CI; Work package 12 scheduling
config/sources/                   # Work package 02 source registry
config/indicators/                # Work package 02 financial metadata
config/validation/                # Work package 04 validation policy
data/raw/                         # Work package 03 local raw outputs (ignored)
data/processed/                   # Work package 05 outputs (ignored)
data/sample/                      # Small, licensed/anonymized test examples
src/fx_intelligence/ingestion/    # Work package 03
src/fx_intelligence/schemas/      # Work package 04
src/fx_intelligence/validation/   # Work package 04
src/fx_intelligence/transformation/ # Work package 05
src/fx_intelligence/warehouse/    # Work package 06
src/fx_intelligence/analytics/    # Work packages 07–09
src/fx_intelligence/orchestration/ # Work package 12
sql/staging/                      # Work package 06
sql/marts/                        # Work package 06
sql/validation/                   # Work packages 06, 13
dashboard/powerbi/               # Work packages 10–11
dashboard/screenshots/            # Work package 14
notebooks/                       # Work package 09 exploratory work
reports/                         # Work packages 09, 14
docs/                            # Specification and methods
tests/unit/                      # Deterministic behavior tests
tests/integration/               # Pipeline tests with fixtures
tests/fixtures/                  # Small controlled examples
```

Create directories only when their task needs them. Work package 01 creates the minimum package, test, CI, and documentation foundation; it does not scaffold empty future subsystems merely to match this diagram.

## Data contracts and grain

| Model | Grain | Required contract |
| --- | --- | --- |
| `dim_date` | one calendar date | date-valued `date_key`, year, month, day |
| `dim_currency` | one currency | `currency_code`, region |
| `dim_fx_pair` | one directed pair | `pair_id`, `base_ccy`, `quote_ccy` |
| `dim_indicator` | one macro series | `indicator_id`, unit, frequency |
| `dim_source` | one provider/source | `source_id`, provider, access/version notes |
| `fact_fx_rates` | pair × observation date × rate type × source | positive rate, quote direction, provider series ID, retrieval timestamp |
| `fact_macro` | indicator × observation period × vintage | value, unit, release date if supplied, retrieval timestamp |
| `fact_fx_analytics` | pair × date × metric × window | metric value, method/version, source lineage |
| `etl_run_log` | one pipeline run | status, counts, timestamps, errors |

These are target contracts for Work packages 02–06, not tables to implement during Work package 01. Define unique keys explicitly when implementing each fact. Keep published observation dates separate from timestamps at which information became available; never infer release date from observation date. Do not join monthly macro observations to daily FX rows on equal date alone.

## Component boundaries

- **Source adapters:** Fetch provider payloads and metadata; no business metric calculations.
- **Validation:** Check types, units, chronology, quote conventions, positive FX rates, duplicates, and missing fields; quarantine invalid rows.
- **Transformation:** Normalize pairs and rate types, invert quotes, derive cross-rates, align calendars and macro release availability.
- **Warehouse:** Persist dimensions/facts and versioned SQL views; reconcile row counts and provenance.
- **Analytics:** Compute performance, volatility/risk, then macro associations in separate task modules using explicit assumptions.
- **Presentation:** Power BI consumes stable marts; its measures reconcile to Python/SQL reference outputs. Display provenance and freshness.
- **Operations:** Schedule, log, retry, detect stale data, and provide recovery instructions without assuming Power BI refresh is automatic.

## Technology decisions

Python 3.13; pandas and NumPy for time series; DuckDB and Parquet for local analytical storage; pytest and Pandera for tests and data validation; Ruff and pre-commit for quality; Power BI Desktop for reporting; GitHub Actions for CI and later scheduling; Jupyter only for exploratory research. The exact package versions and provider access must be checked at implementation time. Store only safe sample data in Git; exclude credentials, local databases, raw downloads, and generated outputs by default.
