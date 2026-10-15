# FX Market Intelligence Dashboard

An auditable FX and macroeconomic analytics project centered on USD/THB and selected G10/Asia currencies. The planned system collects official time series, validates quote conventions and data availability, computes financial metrics, and presents six Power BI pages. **Current implementation:** Task 01 engineering foundation only. No ingestion, warehouse, financial calculations, or dashboard exists yet.

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

Task 01 provides packaging, tests, linting and CI. The first data contract is Task 02; provider access, numerical analytics, automated refresh and the Power BI report are later tasks. See the roadmap for their acceptance criteria.
