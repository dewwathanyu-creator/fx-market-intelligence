"""Offline checks for scheduled refresh planning and failure visibility."""

import json
from datetime import date
from pathlib import Path

import duckdb
import pytest

from fx_intelligence.orchestration.refresh import (
    RefreshFailure,
    incremental_start,
    record_bi_refresh,
    run_refresh,
)


def _root(tmp_path: Path) -> Path:
    registry = tmp_path / "config/sources/registry.yaml"
    registry.parent.mkdir(parents=True)
    registry.write_text(
        "series:\n"
        "  - id: bot_usdthb_interbank\n"
        "    provider: BOT\n"
        "    series_id: DAILY_REF_RATE\n"
        "    url: https://example.invalid/bot\n"
        "    unit: THB per USD\n"
        "    frequency: daily\n"
        "    priority: P0\n"
        "    rate_type: interbank_weighted_average\n"
        "    base_ccy: USD\n"
        "    quote_ccy: THB\n"
        "  - id: fred_fedfunds\n"
        "    provider: FRED\n"
        "    series_id: FEDFUNDS\n"
        "    url: https://example.invalid/fred\n"
        "    unit: percent per annum\n"
        "    frequency: monthly\n"
        "    priority: P0\n"
        "    rate_type: macro\n",
        encoding="utf-8",
    )
    return tmp_path


def _seed(root: Path, *, fx: date | None, macro: date | None) -> None:
    path = root / "data/processed/fx.duckdb"
    path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(path)) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS fact_fx_rates("
            "source_id VARCHAR, observation_date DATE, "
            "PRIMARY KEY(source_id, observation_date))"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS fact_macro("
            "source_id VARCHAR, observation_date DATE, "
            "PRIMARY KEY(source_id, observation_date))"
        )
        if fx is not None:
            db.execute(
                "INSERT OR IGNORE INTO fact_fx_rates VALUES (?, ?)", ["bot_usdthb_interbank", fx]
            )
        if macro is not None:
            db.execute("INSERT OR IGNORE INTO fact_macro VALUES (?, ?)", ["fred_fedfunds", macro])


def _events(root: Path) -> list[dict]:
    path = root / "data/processed/operations/refresh.jsonl"
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_incremental_rerun_uses_overlap_and_keeps_source_rows_unique(tmp_path: Path) -> None:
    root = _root(tmp_path)
    calls = []

    def build(start, end, project_root, sources):
        calls.append((start, end, sources))
        _seed(project_root, fx=end, macro=end)
        return {"fx": 1, "macro": 1}

    sources = ("bot_usdthb_interbank", "fred_fedfunds")
    run_refresh(root, date(2026, 10, 15), sources=sources, build_fn=build)
    run_refresh(root, date(2026, 10, 16), sources=sources, build_fn=build)
    run_refresh(root, date(2026, 10, 16), sources=sources, build_fn=build)
    assert calls == [
        (date(2025, 10, 16), date(2026, 10, 15), sources),
        (date(2026, 9, 1), date(2026, 10, 16), sources),
        (date(2026, 9, 2), date(2026, 10, 16), sources),
    ]
    with duckdb.connect(str(root / "data/processed/fx.duckdb"), read_only=True) as db:
        assert db.execute("SELECT COUNT(*) FROM fact_fx_rates").fetchone()[0] == 2
        assert db.execute("SELECT COUNT(*) FROM fact_macro").fetchone()[0] == 2
    assert len(_events(root)) == 3
    assert all(event["status"] == "success" for event in _events(root))


def test_stale_source_is_reported_separately_from_successful_build(tmp_path: Path) -> None:
    root = _root(tmp_path)

    def build(start, end, project_root, sources):
        _seed(project_root, fx=date(2026, 10, 14), macro=date(2026, 8, 1))
        return {"fx": 1, "macro": 1}

    with pytest.raises(RefreshFailure, match="stale source"):
        run_refresh(
            root,
            date(2026, 10, 16),
            sources=("bot_usdthb_interbank", "fred_fedfunds"),
            build_fn=build,
        )
    event = _events(root)[0]
    assert event["status"] == "stale"
    assert event["stale_sources"] == ["fred_fedfunds"]


def test_failure_log_and_exception_never_include_provider_secret(tmp_path: Path) -> None:
    root = _root(tmp_path)
    secret = "SUPER_SECRET_API_KEY_123"

    def build(start, end, project_root, sources):
        raise RuntimeError(f"provider URL contains {secret}")

    with pytest.raises(RefreshFailure) as error:
        run_refresh(root, date(2026, 10, 16), sources=("bot_usdthb_interbank",), build_fn=build)
    assert secret not in str(error.value)
    assert secret not in (root / "data/processed/operations/refresh.jsonl").read_text()
    assert _events(root)[0]["status"] == "failed"
    assert _events(root)[0]["error_type"] == "RuntimeError"


def test_bi_refresh_failure_does_not_change_etl_status(tmp_path: Path) -> None:
    root = _root(tmp_path)
    record_bi_refresh(root, "failed")
    assert _events(root)[0]["event"] == "bi_refresh"
    assert _events(root)[0]["status"] == "failed"
    assert not (root / "data/processed/fx.duckdb").exists()


def test_incremental_start_uses_oldest_selected_source(tmp_path: Path) -> None:
    root = _root(tmp_path)
    _seed(root, fx=date(2026, 10, 14), macro=date(2026, 9, 30))
    assert incremental_start(
        root / "data/processed/fx.duckdb",
        ("bot_usdthb_interbank", "fred_fedfunds"),
        date(2026, 10, 16),
    ) == date(2026, 8, 17)
