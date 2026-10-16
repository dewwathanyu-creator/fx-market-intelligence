from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import duckdb

from fx_intelligence.schemas.models import FXObservation, MacroObservation
from fx_intelligence.warehouse.build import build_warehouse


def sample_rows() -> tuple[list[FXObservation], list[MacroObservation]]:
    now = datetime(2026, 1, 5, tzinfo=UTC)
    fx = FXObservation(
        source_id="bot",
        series_id="DAILY_REF_RATE",
        base_ccy="USD",
        quote_ccy="THB",
        rate_type="interbank_weighted_average",
        observation_date=date(2026, 1, 2),
        retrieved_at=now,
        rate=Decimal("33.25"),
        unit="THB per USD",
        frequency="daily",
    )
    macro = MacroObservation(
        source_id="fred",
        series_id="DGS2",
        observation_date=date(2026, 1, 2),
        retrieved_at=now,
        value=Decimal("4.20"),
        unit="percent per annum",
        frequency="daily",
        vintage_date=date(2026, 1, 5),
        release_date=date(2026, 1, 2),
    )
    return [fx], [macro]


def test_star_schema_preserves_grain_and_lineage(tmp_path: Path) -> None:
    db_path = tmp_path / "fx.duckdb"
    fx, macro = sample_rows()
    counts = build_warehouse(db_path, fx, macro)
    assert counts == {"fx": 1, "macro": 1}
    with duckdb.connect(str(db_path), read_only=True) as db:
        assert db.sql("select count(*) from dim_date").fetchone()[0] == 1
        assert db.sql("select count(*) from dim_currency").fetchone()[0] == 2
        assert db.sql("select count(*) from dim_fx_pair").fetchone()[0] == 1
        assert db.sql("select count(*) from dim_source").fetchone()[0] == 2
        assert db.sql("select provider from dim_source where source_id = 'bot'").fetchone() == (
            "BOT",
        )
        assert db.sql("select source_id, rate from fact_fx_rates").fetchone() == (
            "bot",
            Decimal("33.2500000000"),
        )
        assert db.sql("select source_id, value from fact_macro").fetchone() == (
            "fred",
            Decimal("4.2000000000"),
        )


def test_rerun_is_idempotent_and_mart_matches(tmp_path: Path) -> None:
    db_path = tmp_path / "fx.duckdb"
    fx, macro = sample_rows()
    build_warehouse(db_path, fx, macro)
    build_warehouse(db_path, fx, macro)
    with duckdb.connect(str(db_path), read_only=True) as db:
        assert db.sql("select count(*) from fact_fx_rates").fetchone()[0] == 1
        assert db.sql("select count(*) from fact_macro").fetchone()[0] == 1
        assert db.sql("select rate from v_fx_latest").fetchone()[0] == Decimal("33.2500000000")
        assert db.sql("select count(*) from etl_run_log").fetchone()[0] == 2
