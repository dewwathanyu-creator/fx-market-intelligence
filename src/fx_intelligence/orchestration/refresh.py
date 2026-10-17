"""Incremental warehouse refresh with source freshness and sanitized event logs."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import duckdb

from fx_intelligence.ingestion.build_local import DEFAULT_SOURCE_IDS, build_local
from fx_intelligence.registry import load_registry

BOOTSTRAP_DAYS = 365
OVERLAP_DAYS = 45
MAX_AGE_DAYS = {"daily": 7, "monthly": 60}


class RefreshFailure(RuntimeError):
    """A refresh failed; details are deliberately sanitized in the event log."""


def _latest_dates(db_path: Path, sources: tuple[str, ...]) -> dict[str, date | None]:
    latest: dict[str, date | None] = dict.fromkeys(sources)
    if not db_path.is_file():
        return latest
    with duckdb.connect(str(db_path), read_only=True) as db:
        tables = {
            row[0]
            for row in db.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
            ).fetchall()
        }
        for table in ("fact_fx_rates", "fact_macro"):
            if table not in tables:
                continue
            for source_id, observed in db.execute(
                f"SELECT source_id, MAX(observation_date) FROM {table} "
                "WHERE source_id IN (SELECT UNNEST(?)) GROUP BY source_id",
                [list(sources)],
            ).fetchall():
                if latest[source_id] is None or observed > latest[source_id]:
                    latest[source_id] = observed
    return latest


def incremental_start(
    db_path: Path,
    sources: tuple[str, ...],
    as_of: date,
    *,
    bootstrap_days: int = BOOTSTRAP_DAYS,
    overlap_days: int = OVERLAP_DAYS,
) -> date:
    """Use the oldest selected source's latest date with a revision overlap."""
    if not sources or bootstrap_days < 1 or overlap_days < 1:
        raise ValueError("sources and lookback lengths must be positive")
    bootstrap_start = as_of - timedelta(days=bootstrap_days - 1)
    latest = _latest_dates(db_path, sources)
    if any(value is None for value in latest.values()):
        return bootstrap_start
    oldest = min(value for value in latest.values() if value is not None)
    if oldest > as_of:
        raise ValueError("warehouse observation date is after the requested date")
    return min(as_of, oldest - timedelta(days=overlap_days - 1))


def _append_event(root: Path, event: dict) -> None:
    path = root / "data/processed/operations/refresh.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    entry = {"logged_at": datetime.now(UTC).isoformat(), **event}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def run_refresh(
    root: Path,
    as_of: date,
    *,
    sources: tuple[str, ...] = DEFAULT_SOURCE_IDS,
    build_fn: Callable = build_local,
) -> dict[str, int]:
    """Fetch one common incremental window, then verify each source's age."""
    registry = {item["id"]: item for item in load_registry(root / "config/sources/registry.yaml")}
    if not sources or len(sources) != len(set(sources)) or set(sources) - registry.keys():
        raise ValueError("source selection is empty, duplicated, or unknown")
    db_path = root / "data/processed/fx.duckdb"
    try:
        start = incremental_start(db_path, sources, as_of)
    except Exception as error:
        _append_event(
            root,
            {
                "event": "etl_refresh",
                "as_of": as_of.isoformat(),
                "sources": list(sources),
                "status": "failed",
                "error_type": type(error).__name__,
                "stage": "planning",
            },
        )
        raise RefreshFailure(
            "ETL refresh planning failed; inspect sanitized operations log"
        ) from None
    base_event = {
        "event": "etl_refresh",
        "as_of": as_of.isoformat(),
        "start": start.isoformat(),
        "sources": list(sources),
        "bi_refresh": "manual_required",
    }
    try:
        counts = build_fn(start, as_of, root, sources)
        latest = _latest_dates(db_path, sources)
    except Exception as error:
        _append_event(root, {**base_event, "status": "failed", "error_type": type(error).__name__})
        raise RefreshFailure("ETL refresh failed; inspect sanitized operations log") from None

    stale = [
        source_id
        for source_id in sources
        if latest[source_id] is None
        or not 0
        <= (as_of - latest[source_id]).days
        <= MAX_AGE_DAYS.get(registry[source_id]["frequency"], 60)
    ]
    status = "stale" if stale else "success"
    _append_event(
        root,
        {**base_event, "status": status, "counts": counts, "stale_sources": stale},
    )
    if stale:
        raise RefreshFailure("ETL refresh completed with stale source data")
    return counts


def record_bi_refresh(root: Path, status: str) -> None:
    """Record the independent manual Power BI refresh result without touching ETL."""
    if status not in {"success", "failed"}:
        raise ValueError("BI status must be success or failed")
    _append_event(root, {"event": "bi_refresh", "status": status})


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh and monitor the FX warehouse")
    sub = parser.add_subparsers(dest="command", required=True)
    refresh = sub.add_parser("refresh")
    refresh.add_argument("--root", type=Path, default=Path.cwd())
    refresh.add_argument("--as-of", type=date.fromisoformat, default=datetime.now(UTC).date())
    refresh.add_argument("--sources", nargs="+", default=DEFAULT_SOURCE_IDS)
    bi = sub.add_parser("record-bi")
    bi.add_argument("status", choices=("success", "failed"))
    bi.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    if args.command == "record-bi":
        record_bi_refresh(args.root, args.status)
        return
    try:
        counts = run_refresh(args.root, args.as_of, sources=tuple(args.sources))
    except RefreshFailure as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps({"status": "success", "counts": counts}, sort_keys=True))


if __name__ == "__main__":
    main()
