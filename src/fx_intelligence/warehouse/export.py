"""Deterministic, source-aware CSV exports for Power BI Desktop."""

import csv
from collections import defaultdict
from datetime import timedelta
from decimal import Decimal
from pathlib import Path

import duckdb

from fx_intelligence.analytics.performance import indexed_performance, rolling_return
from fx_intelligence.analytics.risk import drawdown, rolling_volatility
from fx_intelligence.schemas.models import FXObservation


def _write_csv(path: Path, headers: list[str], rows: list[tuple[object, ...]]) -> int:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        for row in rows:
            writer.writerow("" if value is None else value for value in row)
    return len(rows)


def export_powerbi(db_path: Path, out_dir: Path) -> dict[str, int]:
    """Export stable star-schema tables and Python parity metrics from DuckDB."""
    if not db_path.is_file():
        raise FileNotFoundError(db_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    with duckdb.connect(str(db_path), read_only=True) as db:
        tables = {
            "dim_currency": "SELECT currency_code, region FROM dim_currency ORDER BY currency_code",
            "dim_fx_pair": "SELECT pair_id, base_ccy, quote_ccy FROM dim_fx_pair ORDER BY pair_id",
            "dim_indicator": (
                "SELECT indicator_id, unit, frequency FROM dim_indicator ORDER BY indicator_id"
            ),
            "dim_source": "SELECT source_id, provider FROM dim_source ORDER BY source_id",
            "fact_fx_rates": """SELECT source_id, series_id, pair_id, observation_date,
                rate_type, rate, unit, frequency, retrieved_at FROM fact_fx_rates
                ORDER BY source_id, pair_id, rate_type, observation_date""",
            "fact_macro": """SELECT source_id, series_id, observation_date, vintage_date,
                release_date, value, unit, frequency, retrieved_at FROM fact_macro
                ORDER BY source_id, series_id, observation_date, vintage_date""",
        }
        for name, query in tables.items():
            cursor = db.execute(query)
            headers = [column[0] for column in cursor.description]
            counts[name] = _write_csv(out_dir / f"{name}.csv", headers, cursor.fetchall())

        bounds = db.execute(
            """SELECT MIN(observation_date), MAX(observation_date) FROM (
                SELECT observation_date FROM fact_fx_rates
                UNION ALL SELECT observation_date FROM fact_macro
            )"""
        ).fetchone()
        date_rows: list[tuple[object, ...]] = []
        if bounds and bounds[0] is not None:
            day = bounds[0]
            while day <= bounds[1]:
                date_rows.append((day, day.year, day.month, day.strftime("%b"), day.day))
                day += timedelta(days=1)
        counts["dim_date"] = _write_csv(
            out_dir / "dim_date.csv", ["date_key", "year", "month", "month_name", "day"], date_rows
        )

        grouped: dict[tuple[str, str, str], list[FXObservation]] = defaultdict(list)
        for row in db.execute(tables["fact_fx_rates"]).fetchall():
            (
                source_id,
                series_id,
                pair_id,
                observation_date,
                rate_type,
                rate,
                unit,
                frequency,
                retrieved_at,
            ) = row
            base_ccy, quote_ccy = pair_id.split("/", 1)
            grouped[(source_id, pair_id, rate_type)].append(
                FXObservation(
                    source_id,
                    series_id,
                    base_ccy,
                    quote_ccy,
                    rate_type,
                    observation_date,
                    retrieved_at,
                    Decimal(rate),
                    unit,
                    frequency,
                )
            )
        metric_rows: list[tuple[object, ...]] = []
        for (source_id, pair_id, rate_type), series in grouped.items():
            points = indexed_performance(series)
            drawdowns = drawdown(points)
            rolling = {n: rolling_return(points, n) for n in (5, 20, 60)}
            volatility = {n: rolling_volatility(points, n) for n in (20, 60, 120)}
            for i, point in enumerate(points):
                metric_rows.append(
                    (
                        source_id,
                        pair_id,
                        rate_type,
                        point.observation_date,
                        point.index,
                        point.simple_return,
                        point.log_return,
                        drawdowns[i],
                        rolling[5][i],
                        rolling[20][i],
                        rolling[60][i],
                        volatility[20][i],
                        volatility[60][i],
                        volatility[120][i],
                    )
                )
        counts["fact_fx_metrics"] = _write_csv(
            out_dir / "fact_fx_metrics.csv",
            [
                "source_id",
                "pair_id",
                "rate_type",
                "observation_date",
                "indexed_rate",
                "simple_return",
                "log_return",
                "drawdown",
                "rolling_return_5",
                "rolling_return_20",
                "rolling_return_60",
                "volatility_20",
                "volatility_60",
                "volatility_120",
            ],
            metric_rows,
        )
        last = db.execute(
            "SELECT run_at FROM etl_run_log WHERE status = 'success' ORDER BY run_at DESC LIMIT 1"
        ).fetchone()
        counts["refresh_metadata"] = _write_csv(
            out_dir / "refresh_metadata.csv",
            ["last_success_at", "fx_row_count", "macro_row_count"],
            [(last[0] if last else None, counts["fact_fx_rates"], counts["fact_macro"])],
        )
    return counts
