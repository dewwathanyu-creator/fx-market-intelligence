"""Stable Power BI exports must reconcile to canonical Python and SQL results."""

import csv
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import duckdb
import pytest

from fx_intelligence.analytics.performance import indexed_performance
from fx_intelligence.analytics.risk import rolling_volatility
from fx_intelligence.schemas.models import FXObservation
from fx_intelligence.warehouse.build import build_warehouse
from fx_intelligence.warehouse.export import export_powerbi


def _fx(day: int, rate: str) -> FXObservation:
    return FXObservation(
        source_id="bot_usdthb_interbank",
        series_id="DAILY_REF_RATE",
        base_ccy="USD",
        quote_ccy="THB",
        rate_type="interbank_weighted_average",
        observation_date=date(2025, 1, day),
        retrieved_at=datetime(2025, 2, 1, tzinfo=UTC),
        rate=Decimal(rate),
        unit="THB per USD",
        frequency="daily",
    )


def _csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def test_bi_export_grain_performance_volatility_and_refresh(tmp_path: Path) -> None:
    rows = [_fx(2, "40"), _fx(3, "44"), _fx(6, "48")]
    db_path = tmp_path / "fx.duckdb"
    build_warehouse(db_path, rows, [], sql_root=Path("sql"))
    out = tmp_path / "powerbi"
    result = export_powerbi(db_path, out)
    facts = _csv(out / "fact_fx_rates.csv")
    metrics = _csv(out / "fact_fx_metrics.csv")
    dates = _csv(out / "dim_date.csv")
    refresh = _csv(out / "refresh_metadata.csv")
    assert result["fact_fx_rates"] == len(facts) == 3
    assert (
        len({(r["source_id"], r["pair_id"], r["observation_date"], r["rate_type"]) for r in facts})
        == 3
    )
    assert dates[0]["date_key"] == "2025-01-02" and dates[-1]["date_key"] == "2025-01-06"
    expected = indexed_performance(rows)
    last = next(r for r in metrics if r["observation_date"] == "2025-01-06")
    assert Decimal(last["indexed_rate"]) == expected[-1].index
    assert Decimal(last["simple_return"]) == expected[-1].simple_return
    assert last["volatility_20"] == ""
    assert refresh[0]["last_success_at"]
    assert refresh[0]["fx_row_count"] == "3"
    with duckdb.connect(str(db_path), read_only=True) as db:
        assert db.sql("select count(*) from fact_fx_rates").fetchone()[0] == len(facts)


def test_exported_volatility_matches_python_reference(tmp_path: Path) -> None:
    rows = [_fx(day, str(40 + day / 10 + (day % 3) / 20)) for day in range(1, 23)]
    db_path = tmp_path / "fx.duckdb"
    build_warehouse(db_path, rows, [], sql_root=Path("sql"))
    out = tmp_path / "powerbi"
    export_powerbi(db_path, out)
    metrics = _csv(out / "fact_fx_metrics.csv")
    expected = rolling_volatility(indexed_performance(rows), 20)[-1]
    assert expected is not None
    assert float(metrics[-1]["volatility_20"]) == pytest.approx(expected, rel=1e-10)
