"""Build a local, source-aware DuckDB database and Power BI CSV extracts."""

import argparse
import calendar
import json
import os
from datetime import date, timedelta
from pathlib import Path

import httpx
from dotenv import load_dotenv

from fx_intelligence.registry import load_registry
from fx_intelligence.warehouse.build import build_warehouse
from fx_intelligence.warehouse.export import export_powerbi
from fx_intelligence.warehouse.workbook import export_workbook

from .bot import BotClient
from .fred import FredClient
from .normalize import normalize_payload
from .storage import store_raw

DEFAULT_SOURCE_IDS = (
    "bot_usdthb_interbank",
    "bot_usdthb_bank_average",
    "bot_eurthb_bank_average",
    "fred_fedfunds",
    "fred_dgs2",
    "fred_dtwexbgs",
    "fred_cpiaucsl",
    "fred_vixcls",
)


def month_windows(start: date, end: date) -> list[tuple[date, date]]:
    """Split an inclusive period into BOT-sized calendar-month windows."""
    if end < start:
        raise ValueError("end must not precede start")
    windows = []
    current = start
    while current <= end:
        month_end = date(
            current.year, current.month, calendar.monthrange(current.year, current.month)[1]
        )
        stop = min(end, month_end)
        windows.append((current, stop))
        current = stop + timedelta(days=1)
    return windows


def build_local(
    start: date, end: date, root: Path, sources: tuple[str, ...] = DEFAULT_SOURCE_IDS
) -> dict[str, int]:
    """Fetch official sources, keep raw envelopes, validate and build BI exports."""
    registry = {item["id"]: item for item in load_registry(root / "config/sources/registry.yaml")}
    unknown = set(sources) - registry.keys()
    if unknown:
        raise ValueError(f"unknown source ids: {', '.join(sorted(unknown))}")
    load_dotenv(root / ".env")
    fx_rows = []
    macro_rows = []
    with httpx.Client(timeout=30) as http:
        for source_id in sources:
            source = registry[source_id]
            windows = month_windows(start, end) if source["provider"] == "BOT" else [(start, end)]
            for first, last in windows:
                if source["provider"] == "BOT":
                    params = {"start_period": first.isoformat(), "end_period": last.isoformat()}
                    if ":" in source["series_id"]:
                        params["currency"] = source["series_id"].split(":", 1)[1]
                    payload = BotClient(os.getenv("BOT_API_KEY", ""), http=http).fetch(
                        source["url"], params
                    )
                else:
                    observations = FredClient(os.getenv("FRED_API_KEY", ""), http=http).fetch(
                        source["series_id"], first.isoformat(), last.isoformat()
                    )
                    payload = {"observations": observations}
                window = f"{first.isoformat()}_{last.isoformat()}"
                saved = store_raw(root / "data/raw", source_id, window, payload)
                envelope = json.loads(saved.read_text(encoding="utf-8"))
                fx, macro = normalize_payload(envelope, source)
                fx_rows.extend(fx)
                macro_rows.extend(macro)
    db_path = root / "data/processed/fx.duckdb"
    counts = build_warehouse(db_path, fx_rows, macro_rows, sql_root=root / "sql")
    exported = export_powerbi(db_path, root / "dashboard/powerbi/data")
    export_workbook(root / "dashboard/powerbi/data", root / "dashboard/powerbi/data/fx_model.xlsx")
    return {**counts, **{f"export_{name}": count for name, count in exported.items()}}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build local official-source FX data for Power BI")
    parser.add_argument("--start", required=True, type=date.fromisoformat)
    parser.add_argument("--end", required=True, type=date.fromisoformat)
    parser.add_argument("--sources", nargs="*", default=DEFAULT_SOURCE_IDS)
    args = parser.parse_args()
    counts = build_local(args.start, args.end, Path.cwd(), tuple(args.sources))
    for name, count in counts.items():
        print(f"{name}: {count}")


if __name__ == "__main__":
    main()
