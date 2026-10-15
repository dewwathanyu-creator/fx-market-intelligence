"""Validate canonical observations and retain rejection reasons."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from fx_intelligence.schemas.models import FXObservation, MacroObservation


@dataclass(frozen=True)
class ValidationIssue:
    index: int
    reason: str
    source_id: str
    series_id: str
    observation_date: date


def _issue(index: int, reason: str, item: FXObservation | MacroObservation) -> ValidationIssue:
    return ValidationIssue(index, reason, item.source_id, item.series_id, item.observation_date)


def _invalid_number(value: Decimal | None) -> bool:
    return value is not None and not value.is_finite()


def validate_fx(
    rows: list[FXObservation],
) -> tuple[list[FXObservation], list[ValidationIssue]]:
    """Separate usable FX observations from invalid or duplicate records."""
    accepted: list[FXObservation] = []
    issues: list[ValidationIssue] = []
    keys: set[tuple[str, str, str, str, str, date]] = set()
    for index, item in enumerate(rows):
        key = (
            item.source_id,
            item.series_id,
            item.base_ccy,
            item.quote_ccy,
            item.rate_type,
            item.observation_date,
        )
        reason = None
        if (
            len(item.base_ccy) != 3
            or len(item.quote_ccy) != 3
            or not item.base_ccy.isupper()
            or not item.quote_ccy.isupper()
            or item.base_ccy == item.quote_ccy
        ):
            reason = "invalid_pair"
        elif item.rate is None or _invalid_number(item.rate) or item.rate <= 0:
            reason = "invalid_rate"
        elif not all((item.source_id, item.series_id, item.rate_type, item.unit, item.frequency)):
            reason = "missing_metadata"
        elif item.retrieved_at.tzinfo is None or item.observation_date > item.retrieved_at.date():
            reason = "invalid_chronology"
        elif key in keys:
            reason = "duplicate_key"
        if reason:
            issues.append(_issue(index, reason, item))
        else:
            accepted.append(item)
            keys.add(key)
    return accepted, issues


def validate_macro(
    rows: list[MacroObservation],
) -> tuple[list[MacroObservation], list[ValidationIssue]]:
    """Validate macro metadata without filling missing source values."""
    accepted: list[MacroObservation] = []
    issues: list[ValidationIssue] = []
    keys: set[tuple[str, str, date, date | None]] = set()
    for index, item in enumerate(rows):
        key = (item.source_id, item.series_id, item.observation_date, item.vintage_date)
        reason = None
        if _invalid_number(item.value):
            reason = "invalid_value"
        elif not all((item.source_id, item.series_id, item.unit, item.frequency)):
            reason = "missing_metadata"
        elif item.retrieved_at.tzinfo is None:
            reason = "invalid_chronology"
        elif item.release_date and item.release_date > item.retrieved_at.date():
            reason = "future_release"
        elif key in keys:
            reason = "duplicate_key"
        if reason:
            issues.append(_issue(index, reason, item))
        else:
            accepted.append(item)
            keys.add(key)
    return accepted, issues
