"""Align macro observations to dates on which values were actually available."""

from datetime import date

from fx_intelligence.schemas.models import MacroObservation


def align_macro(
    rows: list[MacroObservation], target_dates: list[date]
) -> list[MacroObservation | None]:
    """Choose the latest known observation and vintage at each target date."""
    result: list[MacroObservation | None] = []
    for target in target_dates:
        available = [
            item
            for item in rows
            if item.release_date is not None
            and item.release_date <= target
            and (item.vintage_date is None or item.vintage_date <= target)
        ]
        result.append(
            max(
                available,
                key=lambda item: (item.observation_date, item.vintage_date or date.min),
                default=None,
            )
        )
    return result
