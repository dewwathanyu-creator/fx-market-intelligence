# Task 13 — End-to-end quality assurance

Date: 17 October 2026 (Asia/Bangkok). Scope: offline sample path, package installation, regression suite and documented Desktop evidence. This report does not claim a new live BOT/FRED fetch or a Power BI service refresh.

## Reproducible sample path

`tests/fixtures/sample_pipeline.json` contains controlled, synthetic BOT-shaped USD/THB interbank, USD/THB bank-average, EUR/THB bank-average and FRED-shaped DGS2 observations. The sample is for testing, not a historical market quotation. `tests/integration/test_pipeline_e2e.py` takes the fixture through source normalization, schema/duplicate validation, quote inversion and compatibility checks, transactional DuckDB warehouse build, Python analytics CSV export, and typed Power BI Excel workbook export.

| Check | Observed result |
| --- | --- |
| Grain and lineage | 9 FX facts, 2 macro facts, 2 directed FX pairs and 3 latest source rows. The 9 FX business keys are unique, and each row retains source, provider series, pair, rate type, date, unit and retrieval time. |
| Quote reconciliation | USD/THB interbank 40 → 44 gives index 110 and +10% simple quote return; this means THB depreciation for THB per USD. Inversion reconciles to one. Mixing interbank with bank-average rates or two different source IDs is rejected for cross-rate derivation. |
| Information availability | FRED fixture has a vintage but no release date. The analytics path returns no historical paired observations until availability can be established. Even with a hypothetical 10 January release, its 1 February vintage is unavailable on 31 January. |
| BI parity | CSV FX/macro counts equal DuckDB counts; the `fact_fx_rates` workbook sheet has 9 data rows. Existing parity tests compare exported metrics with Python reference calculations and volatility convention. |
| Repeatability | Two builds in separate empty directories produce byte-identical observation CSVs. `refresh_metadata.csv` is excluded from byte comparison because it intentionally contains the build time; generated workbook ZIP bytes are not asserted identical, while its typed contents are inspected. |
| Small-sample performance | Three end-to-end tests completed in 6.70 seconds in the isolated environment. Slowest case built/exported the sample twice in 2.79 seconds. This is only a small-fixture smoke measurement, not a production capacity benchmark. |

## Clean Python 3.13 check

A separate Python 3.13.5 virtual environment was created outside the repository and the package was installed with `python -m pip install -e '.[dev]'`. This uncovered an undeclared `pytz` dependency needed by the installed DuckDB 1.5.6 when fetching timezone-bearing rows. `pyproject.toml` now declares `pytz>=2024`. After reinstalling:

```text
python --version                                  -> Python 3.13.5
python -c "import fx_intelligence; ..."          -> 0.1.0
python -m pip check                              -> No broken requirements found
python -m pytest -q --basetemp=.pytest_task13_fresh2 -> 68 passed
python -m ruff check .                           -> All checks passed
python -m ruff format --check .                  -> 74 files already formatted
git diff --check                                 -> passed
```

The sandbox initially blocked Python's default temporary directory and its ordinary network route. A writable temporary directory enabled `ensurepip`; the approved dependency download route completed the isolated installation. Those environment restrictions were resolved for this check. The virtual environment is temporary and is not part of the repository.

## Dashboard and operational evidence

The Task 11 Desktop QA in `docs/DASHBOARD_QA.md` records all six pages visually reviewed, then date slicer, tooltip, navigation, drillthrough and Back interactions checked by the user. At Task 13 the screenshots were local and uncommitted; Task 14 selected six final-page images for the local branch, with the visible account-name caveat recorded in the README. Task 12 fixture tests simulate idempotent refresh, a stale macro source, a provider failure with a secret-like string, and an independent Power BI refresh failure. Its scheduled workflow is committed but cannot run until it is pushed to GitHub and a persistent Windows runner, project-root variable and API secrets are configured.

## Remaining checks and limits

- No new live API call was required for the offline acceptance gate. Actual current BOT/FRED freshness and provider availability must be checked in a supervised run with valid credentials.
- No Power BI service publication or service refresh was attempted. Desktop screenshots confirm rendering and interaction; they do not certify service behavior.
- The fixture covers short daily histories and one FRED series. It cannot benchmark large datasets or every provider schema variant.
- Release dates missing from FRED observations stay unknown. This project does not make a causal or historical release-aware claim from observation dates alone.
- The README was subsequently updated in Task 14 with the delivered project state and reproduction path.
