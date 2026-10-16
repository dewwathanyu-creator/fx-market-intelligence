from datetime import UTC, date, datetime
from decimal import Decimal

from fx_intelligence.schemas.models import MacroObservation
from fx_intelligence.transformation.alignment import align_macro


def macro(
    observation: date, release: date | None, vintage: date | None, value: str
) -> MacroObservation:
    return MacroObservation(
        source_id="fred",
        series_id="CPIAUCSL",
        observation_date=observation,
        retrieved_at=datetime(2026, 3, 1, tzinfo=UTC),
        value=Decimal(value),
        unit="index",
        frequency="monthly",
        vintage_date=vintage,
        release_date=release,
    )


def test_macro_is_unavailable_before_release() -> None:
    row = macro(date(2026, 1, 1), date(2026, 2, 10), date(2026, 2, 10), "320")
    aligned = align_macro([row], [date(2026, 2, 9), date(2026, 2, 10)])
    assert aligned[0] is None
    assert aligned[1] == row


def test_revision_is_unavailable_before_vintage() -> None:
    original = macro(date(2026, 1, 1), date(2026, 2, 10), date(2026, 2, 10), "320")
    revision = macro(date(2026, 1, 1), date(2026, 2, 10), date(2026, 2, 20), "321")
    aligned = align_macro([original, revision], [date(2026, 2, 15), date(2026, 2, 21)])
    assert [row.value for row in aligned if row] == [Decimal("320"), Decimal("321")]


def test_missing_release_date_stays_unavailable() -> None:
    row = macro(date(2026, 1, 1), None, None, "320")
    assert align_macro([row], [date(2026, 2, 21)]) == [None]
