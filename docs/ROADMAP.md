# FX Market Intelligence Dashboard Roadmap

## Table of Contents

- [Global constraints](#global-constraints)
- [Review focus across work packages](#review-focus-across-work-packages)
- [Phase 1 — Project Foundation (M1: Work packages 01–02)](#phase-1--project-foundation-m1-work-packages-0102)
- [Phase 2 — Data Engineering (M2: Work packages 03–06)](#phase-2--data-engineering-m2-work-packages-0306)
- [Phase 3 — Financial Analytics (M3: Work packages 07–08; Work package 09 joins M4)](#phase-3--financial-analytics-m3-work-packages-0708-work-package-09-joins-m4)
- [Phase 4 — Business Intelligence (M4: Work packages 09–11)](#phase-4--business-intelligence-m4-work-packages-0911)
- [Phase 5 — Delivery & Documentation (M5: Work packages 12–14)](#phase-5--delivery--documentation-m5-work-packages-1214)
- [Milestone gates](#milestone-gates)

---

**Goal:** Deliver a reproducible official-source FX and macro analytics platform with a six-page Power BI dashboard.

**Architecture:** Python adapters collect official data into an auditable raw layer; validation and transformations feed DuckDB marts; tested analytics and a Power BI semantic model power the report. Source lineage and date availability travel through every layer.

**Tech Stack:** Python 3.13, pandas, NumPy, DuckDB, Parquet, Power BI Desktop, GitHub Actions, pytest, Pandera, Ruff, Git.

**Spec:** `docs/PROJECT_SPEC.md`; component boundaries and target data contracts: `docs/ARCHITECTURE.md`.

## Global constraints

- Treat BOT weighted-average interbank and average exchange rates as distinct series/rate types.
- Every FX observation needs directed pair, rate type, source, frequency, observation date, and retrieval metadata.
- Never fill missing raw observations automatically; preserve revisions and vintage where available.
- Align macro data by actual information availability; avoid future-data leakage.
- Interpret USD/THB correctly: a higher THB-per-USD quote means THB depreciation.
- Use official NEER/REER; no home-built trade-weighted MVP index.
- No trading execution, guaranteed forecasts, tick data, arbitrage execution, or derivatives pricing in MVP.
- Use deterministic tests and report skipped checks; never commit secrets or restricted raw data.

## Review focus across work packages

1. **Same-looking FX series with different rate types:** Work package 02 records metadata; Work package 04 rejects incompatible records; Work package 05 tests no silent mixing.
2. **Opposite pair directions:** Work packages 05 and 07 test inversion and currency-strength sign with hand-calculated values.
3. **Monthly data released after month-end:** Work packages 05 and 09 test release-aware alignment and no look-ahead.
4. **Missing, revised, or shortened histories:** Work packages 02–04 test coverage and vintages; Work package 08 tests risk metrics with gaps.
5. **ETL success while Power BI remains stale:** Work packages 10 and 12 reconcile refresh dates and surface failure/freshness.

## Phase 1 — Project Foundation (M1: Work packages 01–02)

### Work package 01 — Repository & Engineering Foundation

**Produces:** installable Python package skeleton, dependency configuration, Git baseline, CI, pytest/Ruff checks, README and safe environment template. **Acceptance:** package imports, tests pass, Ruff passes, and CI executes these checks. No source clients or financial calculations yet.

### Work package 02 — Source Registry & Financial Data Dictionary

**Produces:** machine-readable registry of all MVP datasets, exact series IDs, providers, access methods, units, frequencies, directed quote conventions, rate types, priority, coverage, revision/missing-data policy, and licensing/access notes. **Acceptance:** each MVP series has complete metadata and a verified retrieval path; tests detect missing/contradictory metadata. **Depends on:** Work package 01.

## Phase 2 — Data Engineering (M2: Work packages 03–06)

### Work package 03 — BOT & FRED Data Collectors

**Produces:** isolated API clients, historical backfill and incremental ingestion, retries/backoff, structured logs, and raw payload storage with provenance. **Acceptance:** controlled sample fetch and fixture-based rerun produce no duplicate logical observations; errors are observable. **Depends on:** Work package 02.

### Work package 04 — Canonical Schemas & Validation Engine

**Produces:** FX/macro canonical contracts and quality checks for nulls, duplicate keys, nonpositive rates, pair conventions, units, and chronology, with quarantine output. **Acceptance:** intentionally invalid fixtures are identified and excluded while valid records retain lineage. **Depends on:** Work package 03.

### Work package 05 — Transformation & Time Alignment

**Produces:** standardized directed FX series, inversion, cross-rates, frequency handling, and release-aware macro alignment. **Acceptance:** cross-rate identities match hand calculations and no future information appears in historical rows. **Depends on:** Work package 04.

### Work package 06 — SQL Warehouse & Data Marts

**Produces:** DuckDB dimensions/facts, staging/mart SQL, stable analytics-ready views, and reconciliation queries. **Acceptance:** fixture SQL results match expected values and row counts reconcile from input to marts. **Depends on:** Work package 05.

## Phase 3 — Financial Analytics (M3: Work packages 07–08; Work package 09 joins M4)

### Work package 07 — FX Performance Engine

**Produces:** simple/log returns, indexed performance, MTD/YTD and rolling returns, directed strength ranking, and cross-currency comparison. **Acceptance:** hand-calculated fixtures and quote-inversion sign tests pass. **Depends on:** Work package 06.

### Work package 08 — Risk & Volatility Engine

**Produces:** 20/60/120-observation realized volatility, rolling correlation, drawdown, historical volatility percentile, and comparable risk views. **Acceptance:** reference calculations match, with explicit annualization/calendar and correct handling of missing dates. **Depends on:** Work package 07.

### Work package 09 — Macro Factors & Statistical Research

**Produces:** rate spreads, correlation, lag analysis, exploratory regression with diagnostics and research limitations. **Acceptance:** tests show no look-ahead; regression is reproducible and findings avoid causal claims. **Depends on:** Work packages 05–08.

## Phase 4 — Business Intelligence (M4: Work packages 09–11)

### Work package 10 — Power BI Semantic Model

**Produces:** date table, relationships, DAX measures, slicers, and reconciliation checks against Python/SQL marts. **Acceptance:** chosen KPI fixtures agree within a documented tolerance. **Depends on:** Work packages 06–09.

### Work package 11 — Interactive Dashboard Development

**Produces:** all six specified pages, navigation, tooltips, drill-through, dynamic filters, and source/observation/refresh footer. **Acceptance:** each page answers its business question and passes visual and data QA. **Depends on:** Work package 10.

## Phase 5 — Delivery & Documentation (M5: Work packages 12–14)

### Work package 12 — Automation & Monitoring

**Produces:** scheduled ETL, freshness checks, failure logs, idempotent reruns, and recovery guide; separate Power BI refresh procedure. **Acceptance:** rerun does not corrupt data and a simulated refresh failure is detected. **Depends on:** Work packages 03–11.

### Work package 13 — End-to-End Quality Assurance

**Produces:** integrated pipeline, data-quality, performance, documentation, and clean-environment reproducibility checks. **Acceptance:** required suite passes and a fresh environment recreates the sample outputs. **Depends on:** Work packages 01–12.

### Work package 14 — Project Packaging & Case Study

**Produces:** final README, report screenshots, architecture and methodology documentation, one sourced USD/THB research case study, and an evidence-based project summary. **Acceptance:** a reviewer can understand value, methods, limitations, evidence, and reproduction steps from the repository. **Depends on:** Work package 13.

## Milestone gates

| Milestone | Tasks | Exit outcome |
| --- | --- | --- |
| M1 | 01–02 | Engineering foundation and verified data contract. |
| M2 | 03–06 | Auditable, repeatable data pipeline and warehouse. |
| M3 | 07–08 | Tested core FX analytics; Power BI work may begin. |
| M4 | 09–11 | Full analytical dashboard and macro research. |
| M5 | 12–14 | Reproducible, monitored deliverable. |

