# FX Market Intelligence Dashboard Roadmap

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

## Review focus across tasks

1. **Same-looking FX series with different rate types:** Task 02 records metadata; Task 04 rejects incompatible records; Task 05 tests no silent mixing.
2. **Opposite pair directions:** Tasks 05 and 07 test inversion and currency-strength sign with hand-calculated values.
3. **Monthly data released after month-end:** Tasks 05 and 09 test release-aware alignment and no look-ahead.
4. **Missing, revised, or shortened histories:** Tasks 02–04 test coverage and vintages; Task 08 tests risk metrics with gaps.
5. **ETL success while Power BI remains stale:** Tasks 10 and 12 reconcile refresh dates and surface failure/freshness.

## Phase 1 — Project Foundation (M1: Tasks 01–02)

### Task 01 — Repository & Engineering Foundation

**Produces:** installable Python package skeleton, dependency configuration, Git baseline, CI, pytest/Ruff checks, README and safe environment template. **Acceptance:** package imports, tests pass, Ruff passes, and CI executes these checks. No source clients or financial calculations yet.

### Task 02 — Source Registry & Financial Data Dictionary

**Produces:** machine-readable registry of all MVP datasets, exact series IDs, providers, access methods, units, frequencies, directed quote conventions, rate types, priority, coverage, revision/missing-data policy, and licensing/access notes. **Acceptance:** each MVP series has complete metadata and a verified retrieval path; tests detect missing/contradictory metadata. **Depends on:** Task 01.

## Phase 2 — Data Engineering (M2: Tasks 03–06)

### Task 03 — BOT & FRED Data Collectors

**Produces:** isolated API clients, historical backfill and incremental ingestion, retries/backoff, structured logs, and raw payload storage with provenance. **Acceptance:** controlled sample fetch and fixture-based rerun produce no duplicate logical observations; errors are observable. **Depends on:** Task 02.

### Task 04 — Canonical Schemas & Validation Engine

**Produces:** FX/macro canonical contracts and quality checks for nulls, duplicate keys, nonpositive rates, pair conventions, units, and chronology, with quarantine output. **Acceptance:** intentionally invalid fixtures are identified and excluded while valid records retain lineage. **Depends on:** Task 03.

### Task 05 — Transformation & Time Alignment

**Produces:** standardized directed FX series, inversion, cross-rates, frequency handling, and release-aware macro alignment. **Acceptance:** cross-rate identities match hand calculations and no future information appears in historical rows. **Depends on:** Task 04.

### Task 06 — SQL Warehouse & Data Marts

**Produces:** DuckDB dimensions/facts, staging/mart SQL, stable analytics-ready views, and reconciliation queries. **Acceptance:** fixture SQL results match expected values and row counts reconcile from input to marts. **Depends on:** Task 05.

## Phase 3 — Financial Analytics (M3: Tasks 07–08; Task 09 joins M4)

### Task 07 — FX Performance Engine

**Produces:** simple/log returns, indexed performance, MTD/YTD and rolling returns, directed strength ranking, and cross-currency comparison. **Acceptance:** hand-calculated fixtures and quote-inversion sign tests pass. **Depends on:** Task 06.

### Task 08 — Risk & Volatility Engine

**Produces:** 20/60/120-observation realized volatility, rolling correlation, drawdown, historical volatility percentile, and comparable risk views. **Acceptance:** reference calculations match, with explicit annualization/calendar and correct handling of missing dates. **Depends on:** Task 07.

### Task 09 — Macro Factors & Statistical Research

**Produces:** rate spreads, correlation, lag analysis, exploratory regression with diagnostics and research limitations. **Acceptance:** tests show no look-ahead; regression is reproducible and findings avoid causal claims. **Depends on:** Tasks 05–08.

## Phase 4 — Business Intelligence (M4: Tasks 09–11)

### Task 10 — Power BI Semantic Model

**Produces:** date table, relationships, DAX measures, slicers, and reconciliation checks against Python/SQL marts. **Acceptance:** chosen KPI fixtures agree within a documented tolerance. **Depends on:** Tasks 06–09.

### Task 11 — Interactive Dashboard Development

**Produces:** all six specified pages, navigation, tooltips, drill-through, dynamic filters, and source/observation/refresh footer. **Acceptance:** each page answers its business question and passes visual and data QA. **Depends on:** Task 10.

## Phase 5 — Delivery & Documentation (M5: Tasks 12–14)

### Task 12 — Automation & Monitoring

**Produces:** scheduled ETL, freshness checks, failure logs, idempotent reruns, and recovery guide; separate Power BI refresh procedure. **Acceptance:** rerun does not corrupt data and a simulated refresh failure is detected. **Depends on:** Tasks 03–11.

### Task 13 — End-to-End Quality Assurance

**Produces:** integrated pipeline, data-quality, performance, documentation, and clean-environment reproducibility checks. **Acceptance:** required suite passes and a fresh environment recreates the sample outputs. **Depends on:** Tasks 01–12.

### Task 14 — Project Packaging & Case Study

**Produces:** final README, report screenshots, architecture and methodology documentation, one sourced USD/THB research case study, and an evidence-based project summary. **Acceptance:** a reviewer can understand value, methods, limitations, evidence, and reproduction steps from the repository. **Depends on:** Task 13.

## Milestone gates

| Milestone | Tasks | Exit outcome |
| --- | --- | --- |
| M1 | 01–02 | Engineering foundation and verified data contract. |
| M2 | 03–06 | Auditable, repeatable data pipeline and warehouse. |
| M3 | 07–08 | Tested core FX analytics; Power BI work may begin. |
| M4 | 09–11 | Full analytical dashboard and macro research. |
| M5 | 12–14 | Reproducible, monitored deliverable. |

