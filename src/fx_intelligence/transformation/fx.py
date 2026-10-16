"""Directed FX pair and frequency transformations."""

from dataclasses import replace
from decimal import Decimal

from fx_intelligence.schemas.models import FXObservation


def _positive_rate(item: FXObservation) -> Decimal:
    if item.rate is None or not item.rate.is_finite() or item.rate <= 0:
        raise ValueError("valid positive rate required")
    return item.rate


def invert_fx(item: FXObservation) -> FXObservation:
    """Invert a quote while keeping its source and observation metadata."""
    return replace(
        item,
        series_id=f"{item.series_id}:inverse",
        base_ccy=item.quote_ccy,
        quote_ccy=item.base_ccy,
        rate=Decimal(1) / _positive_rate(item),
        unit=f"{item.base_ccy} per {item.quote_ccy}",
    )


def cross_rate(left: FXObservation, right: FXObservation) -> FXObservation:
    """Derive B per A from C per A and C per B with compatible observations."""
    if left.rate_type != right.rate_type:
        raise ValueError("cross-rate requires the same rate type")
    if left.source_id != right.source_id:
        raise ValueError("cross-rate requires the same source")
    if left.observation_date != right.observation_date:
        raise ValueError("cross-rate requires the same observation date")
    if left.quote_ccy != right.quote_ccy:
        raise ValueError("cross-rate requires a common quote currency")
    if left.base_ccy == right.base_ccy:
        raise ValueError("cross-rate needs distinct base currencies")
    return replace(
        left,
        series_id=f"{left.series_id}/{right.series_id}",
        quote_ccy=right.base_ccy,
        rate=_positive_rate(left) / _positive_rate(right),
        unit=f"{right.base_ccy} per {left.base_ccy}",
        retrieved_at=max(left.retrieved_at, right.retrieved_at),
    )


def month_end(rows: list[FXObservation]) -> list[FXObservation]:
    """Select the last available daily quote in each calendar month and series."""
    selected: dict[tuple[str, str, str, int, int], FXObservation] = {}
    for item in rows:
        key = (
            item.source_id,
            item.series_id,
            item.rate_type,
            item.observation_date.year,
            item.observation_date.month,
        )
        current = selected.get(key)
        if current is None or item.observation_date > current.observation_date:
            selected[key] = item
    ordered = sorted(selected.values(), key=lambda item: (item.series_id, item.observation_date))
    return [replace(item, frequency="monthly") for item in ordered]
