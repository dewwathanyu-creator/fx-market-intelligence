"""Directed FX returns; all calculations use observed dates only."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from math import log

from fx_intelligence.schemas.models import FXObservation


@dataclass(frozen=True)
class PerformancePoint:
    observation_date: date
    base_ccy: str
    quote_ccy: str
    index: Decimal
    simple_return: Decimal | None
    log_return: float | None


@dataclass(frozen=True)
class CurrencyRank:
    currency: str
    quote_ccy: str
    start_date: date
    end_date: date
    return_value: Decimal


def _ordered(rows: list[FXObservation]) -> list[FXObservation]:
    if not rows:
        raise ValueError("at least one FX observation required")
    ordered = sorted(rows, key=lambda row: row.observation_date)
    first = ordered[0]
    identity = (first.source_id, first.series_id, first.base_ccy, first.quote_ccy, first.rate_type)
    dates: set[date] = set()
    for row in ordered:
        if (row.source_id, row.series_id, row.base_ccy, row.quote_ccy, row.rate_type) != identity:
            raise ValueError("observations must share one source, series and quote convention")
        if row.observation_date in dates:
            raise ValueError("duplicate observation date")
        if row.rate is None or not row.rate.is_finite() or row.rate <= 0:
            raise ValueError("positive finite FX rates required")
        dates.add(row.observation_date)
    return ordered


def indexed_performance(rows: list[FXObservation]) -> list[PerformancePoint]:
    """Index first observed rate to 100; each return spans observed quotes."""
    ordered = _ordered(rows)
    base_rate = ordered[0].rate
    assert base_rate is not None
    result: list[PerformancePoint] = []
    previous: Decimal | None = None
    for row in ordered:
        assert row.rate is not None
        ratio = row.rate / previous if previous is not None else None
        result.append(
            PerformancePoint(
                observation_date=row.observation_date,
                base_ccy=row.base_ccy,
                quote_ccy=row.quote_ccy,
                index=Decimal(100) * row.rate / base_rate,
                simple_return=ratio - 1 if ratio is not None else None,
                log_return=log(float(ratio)) if ratio is not None else None,
            )
        )
        previous = row.rate
    return result


def rolling_return(points: list[PerformancePoint], observations: int) -> list[Decimal | None]:
    """Trailing return over N quote-to-quote intervals (needs N+1 observations)."""
    if observations < 1:
        raise ValueError("window must be positive")
    if points and any(
        (p.base_ccy, p.quote_ccy) != (points[0].base_ccy, points[0].quote_ccy) for p in points
    ):
        raise ValueError("quote convention must be consistent")
    return [
        points[i].index / points[i - observations].index - 1 if i >= observations else None
        for i in range(len(points))
    ]


def period_return(rows: list[FXObservation], period_start: date, as_of: date) -> Decimal | None:
    """Return from last observed close before period_start through as_of."""
    if as_of < period_start:
        raise ValueError("as_of precedes period_start")
    ordered = _ordered(rows)
    prior = [r for r in ordered if r.observation_date < period_start]
    current = [r for r in ordered if period_start <= r.observation_date <= as_of]
    if not prior or not current:
        return None
    assert prior[-1].rate is not None and current[-1].rate is not None
    return current[-1].rate / prior[-1].rate - 1


def mtd_return(rows: list[FXObservation], as_of: date) -> Decimal | None:
    return period_return(rows, as_of.replace(day=1), as_of)


def ytd_return(rows: list[FXObservation], as_of: date) -> Decimal | None:
    return period_return(rows, as_of.replace(month=1, day=1), as_of)


def rank_currency_strength(series: dict[str, list[FXObservation]]) -> list[CurrencyRank]:
    """Rank base currencies against the same quote currency on identical dates."""
    if not series:
        return []
    ordered = {name: _ordered(rows) for name, rows in series.items()}
    first = next(iter(ordered.values()))
    dates = [row.observation_date for row in first]
    quote = first[0].quote_ccy
    rate_type = first[0].rate_type
    ranks: list[CurrencyRank] = []
    if len(dates) < 2:
        raise ValueError("at least two common observation dates required")
    for currency, rows in ordered.items():
        if [row.observation_date for row in rows] != dates:
            raise ValueError("common observation dates required")
        if (
            rows[0].base_ccy != currency
            or rows[0].quote_ccy != quote
            or rows[0].rate_type != rate_type
        ):
            raise ValueError("common quote currency and rate type required")
        assert rows[0].rate is not None and rows[-1].rate is not None
        ranks.append(
            CurrencyRank(currency, quote, dates[0], dates[-1], rows[-1].rate / rows[0].rate - 1)
        )
    return sorted(ranks, key=lambda row: (-row.return_value, row.currency))
