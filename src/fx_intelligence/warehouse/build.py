"""Build source-aware star-schema facts and BI-ready views."""

from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import duckdb

from fx_intelligence.schemas.models import FXObservation, MacroObservation
from fx_intelligence.validation.validate import validate_fx, validate_macro


def build_warehouse(
    db_path: Path,
    fx_rows: list[FXObservation],
    macro_rows: list[MacroObservation],
    *,
    sql_root: Path = Path("sql"),
) -> dict[str, int]:
    """Upsert validated observations transactionally and return input counts."""
    valid_fx, fx_issues = validate_fx(fx_rows)
    valid_macro, macro_issues = validate_macro(macro_rows)
    if fx_issues or macro_issues:
        raise ValueError(f"invalid input: {len(fx_issues)} FX, {len(macro_issues)} macro rows")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(str(db_path)) as db:
        db.execute("BEGIN TRANSACTION")
        try:
            db.execute((sql_root / "staging" / "schema.sql").read_text(encoding="utf-8"))
            for item in valid_fx:
                pair_id = f"{item.base_ccy}/{item.quote_ccy}"
                db.execute(
                    "INSERT OR IGNORE INTO dim_date VALUES (?, ?)", [item.observation_date] * 2
                )
                for currency in (item.base_ccy, item.quote_ccy):
                    db.execute("INSERT OR IGNORE INTO dim_currency VALUES (?, NULL)", [currency])
                db.execute(
                    "INSERT OR IGNORE INTO dim_fx_pair VALUES (?, ?, ?)",
                    [pair_id, item.base_ccy, item.quote_ccy],
                )
                db.execute(
                    "INSERT OR IGNORE INTO dim_source VALUES (?, ?)",
                    [item.source_id, item.source_id.split("_", 1)[0].upper()],
                )
                db.execute(
                    "INSERT OR REPLACE INTO fact_fx_rates VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        item.source_id,
                        item.series_id,
                        pair_id,
                        item.observation_date,
                        item.rate_type,
                        item.rate,
                        item.unit,
                        item.frequency,
                        item.retrieved_at,
                    ],
                )
            for item in valid_macro:
                db.execute(
                    "INSERT OR IGNORE INTO dim_date VALUES (?, ?)", [item.observation_date] * 2
                )
                db.execute(
                    "INSERT OR IGNORE INTO dim_indicator VALUES (?, ?, ?)",
                    [item.series_id, item.unit, item.frequency],
                )
                db.execute(
                    "INSERT OR IGNORE INTO dim_source VALUES (?, ?)",
                    [item.source_id, item.source_id.split("_", 1)[0].upper()],
                )
                db.execute(
                    "INSERT OR REPLACE INTO fact_macro VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        item.source_id,
                        item.series_id,
                        item.observation_date,
                        item.vintage_date.isoformat() if item.vintage_date else "unknown",
                        item.vintage_date,
                        item.release_date,
                        item.value,
                        item.unit,
                        item.frequency,
                        item.retrieved_at,
                    ],
                )
            db.execute((sql_root / "marts" / "views.sql").read_text(encoding="utf-8"))
            db.execute(
                "INSERT INTO etl_run_log VALUES (?, ?, ?, ?, ?, NULL)",
                [str(uuid4()), datetime.now(UTC), "success", len(valid_fx), len(valid_macro)],
            )
            db.execute("COMMIT")
        except Exception:
            db.execute("ROLLBACK")
            raise
    return {"fx": len(valid_fx), "macro": len(valid_macro)}
