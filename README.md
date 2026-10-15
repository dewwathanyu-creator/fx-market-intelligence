# FX Market Intelligence Dashboard

An auditable FX and macroeconomic analytics project centered on USD/THB and selected G10/Asia currencies. The planned system collects official time series, validates quote conventions and data availability, computes financial metrics, and presents six Power BI pages. **Current implementation:** engineering foundation, source registry, and fixture-tested BOT/FRED raw collectors. The warehouse, financial calculations, and dashboard are still planned.

## Local setup

Use Python 3.13:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -e ".[dev]"
.venv\Scripts\python -c "import fx_intelligence; print(fx_intelligence.__version__)"
.venv\Scripts\python -m pytest -q
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
```

On macOS/Linux, replace `.venv\Scripts\python` with `.venv/bin/python`. CI runs the same import, test, lint and formatting checks on Python 3.13. Optional local hooks: `python -m pre_commit install`.

## Project documents

- [Project specification](docs/PROJECT_SPEC.md): scope, data sources, financial methods and deliverables.
- [Architecture](docs/ARCHITECTURE.md): components, data grain and intended layout.
- [14-task roadmap](docs/TASK_ROADMAP.md): phased delivery and acceptance gates.

## Data and interpretation

BOT, FRED, ECB and BIS are proposed official sources. Exact series access, licensing and coverage are verified in Task 02. BOT rate types must remain distinct. USD/THB means THB per USD: a higher quote indicates THB depreciation. Data are reference/statistical observations, not necessarily executable market prices. Local credentials and downloaded data stay outside Git.

## Status

Tasks 01–02 provide packaging, quality checks, and the first source contract. Task 03 provides raw collectors. To test a provider locally, create a Git-ignored `.env` beside this README with `FRED_API_KEY=` and `BOT_API_KEY=`, then run, for example, `python -m fx_intelligence.ingestion.run fred_dgs2 --start 2026-01-01 --end 2026-01-31`. The output is written under ignored `data/raw/`. Live BOT parameters and source coverage must be checked with valid credentials before use. Numerical analytics, automated refresh and the Power BI report are later tasks.
