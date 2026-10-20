# FX Refresh Runbook

Operating procedures for the scheduled FX refresh: what it updates, how to read its status and how to recover from a failure.

## Table of Contents

- [Operating model](#operating-model)
- [First setup](#first-setup)
- [Manual refresh and recovery](#manual-refresh-and-recovery)
- [Separate Power BI refresh](#separate-power-bi-refresh)
- [Safety notes](#safety-notes)

---

## Operating model

The scheduled job updates the local raw envelopes, DuckDB warehouse, Power BI CSV files and workbook. It does **not** refresh an open Power BI Desktop report or a published semantic model. `data/processed/operations/refresh.jsonl` is a local, Git-ignored event log; it records status, source IDs, window, counts and exception class, never the exception message or key. `etl_run_log` in DuckDB records successful warehouse builds. Use both when diagnosing a run.

The incremental planner finds the most recent observation for every selected source and starts 45 calendar days before the oldest one (inclusive overlap). A new or missing source starts with a 365-day bootstrap window. This common window allows the existing transactional upsert to reconcile revised observations without duplicating primary keys. Raw responses remain content-addressed. The planner uses observation dates for refresh coverage only; it does not treat them as release dates or information-availability dates.

After each build, daily sources older than 7 calendar days and monthly sources older than 60 days are reported as `stale`. These are operational alert thresholds, not proof that the provider has failed: weekends, holidays and scheduled release lags can explain a gap. The job exits nonzero for stale or failed runs. The `bi_refresh` field remains `manual_required` even after a successful ETL run.

## First setup

1. Use a dedicated Windows GitHub Actions runner on the same computer as the Desktop project. Label it `fx-dashboard`; install Python 3.13 and allow the runner account to read/write the project directory. The workflow is in `.github/workflows/refresh.yml` and runs at 14:00 Asia/Bangkok, Monday–Friday. GitHub's cron uses UTC (`07:00 UTC`); the workflow will not run from this local commit until it is pushed to a configured GitHub repository and the runner is online.
2. In that repository's Actions settings, set variable `FX_PROJECT_ROOT` to the absolute path of the local project folder containing `config/sources/registry.yaml` and the PBIP. Set Actions secrets `FRED_API_KEY` and `BOT_API_KEY`. Do not paste keys into the repository, workflow file, command line or issue comments. Keep the local `.env` Git-ignored for manual runs.
3. Run the fixture tests before enabling the schedule: `python -m pytest tests/integration/test_orchestration.py -q`. The workflow has a manual `workflow_dispatch` trigger for a supervised first run. Confirm the persistent root has `data/processed/fx.duckdb`, `dashboard/powerbi/data/fx_model.xlsx`, and a `success` event. Confirm no source is reported stale. The first live run is a provider integration check; fixture tests provide the required deterministic proof.

## Manual refresh and recovery

From the project root with valid local credentials:

```powershell
python -m fx_intelligence.orchestration.refresh refresh --root .
```

For a bounded recovery, pass `--as-of YYYY-MM-DD` (the date must not precede observations already in this warehouse) and optionally `--sources` followed by source IDs from the registry. Use a separate scratch project root for historical replay before existing data. The 45-day overlap makes an identical rerun safe for warehouse primary keys. To inspect the last local events without printing credentials:

```powershell
Get-Content data/processed/operations/refresh.jsonl -Tail 10
```

If the job exits nonzero, inspect the latest event's `status`, `stale_sources` and `error_type`. For `failed`, verify the runner is online, both secrets are configured, provider access is available, and the project root is writable; then rerun the same date. The sanitized log intentionally omits raw exception text, so test the provider independently only in a secure local session. For `stale`, compare the source's last observation with its actual release calendar and the run date. If the gap is expected, document it; otherwise verify provider access and rerun. Do not silently forward-fill missing observations or edit the observation date to clear an alert. A failed source fetch may leave immutable raw files from earlier sources, but the warehouse build does not start until every selected fetch completes.

## Separate Power BI refresh

After a successful ETL event, open `dashboard/powerbi/FX Market Intelligence Dashboard.pbip` in Power BI Desktop on the project computer, select **Home → Refresh**, and wait for completion. Verify the six pages, especially the newest observation date, source labels, and warehouse build timestamp. The `Last Refresh` card in this report currently displays the warehouse build time, not a service refresh timestamp; do not describe it as a published Power BI refresh time. If Desktop refresh succeeds, record it with `python -m fx_intelligence.orchestration.refresh record-bi success --root .`. On a Desktop error, record `record-bi failed`, capture the error locally, verify the workbook and source paths, and retry Desktop refresh after fixing the cause. This status event never changes ETL status or warehouse data.

Power BI service refresh is a separate future deployment path. It requires a configured workspace, credentials and gateway/OneDrive path appropriate for the local workbook. This task neither publishes the PBIP nor schedules a service refresh.

## Safety notes

- The workflow deliberately uses a persistent self-hosted runner and `checkout` with `clean: false`; a disposable hosted runner would discard the local warehouse after every scheduled run.
- Do not run two manual refresh processes at once. GitHub Actions concurrency serializes scheduled runs, but it cannot serialize manual commands started outside Actions.
- DuckDB upserts are transactional and source keys are unique. CSV/workbook exports are regenerated after the warehouse commit; if export fails, rerun the same window before refreshing Power BI. Do not assume a partial export is usable.
- The workflow does not upload raw/provider data as Actions artifacts and does not commit generated files. The local event log omits request URLs and exception messages to avoid accidental key disclosure.
