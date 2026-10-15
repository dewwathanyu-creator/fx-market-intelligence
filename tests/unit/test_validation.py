from datetime import UTC, date, datetime
from decimal import Decimal

from fx_intelligence.schemas.models import FXObservation, MacroObservation
from fx_intelligence.validation.validate import validate_fx, validate_macro

NOW = datetime(2026, 1, 5, tzinfo=UTC)


def fx(**changes: object) -> FXObservation:
    values = {
        "source_id": "bot",
        "series_id": "DAILY_REF_RATE",
        "base_ccy": "USD",
        "quote_ccy": "THB",
        "rate_type": "interbank_weighted_average",
        "observation_date": date(2026, 1, 2),
        "retrieved_at": NOW,
        "rate": Decimal("33.25"),
        "unit": "THB per USD",
        "frequency": "daily",
    }
    values.update(changes)
    return FXObservation(**values)


def test_valid_fx_keeps_lineage() -> None:
    accepted, issues = validate_fx([fx()])
    assert len(accepted) == 1
    assert accepted[0].source_id == "bot"
    assert issues == []


def test_rejects_nonpositive_and_nonfinite_fx() -> None:
    accepted, issues = validate_fx([fx(rate=Decimal("0")), fx(rate=Decimal("NaN"))])
    assert accepted == []
    assert {issue.reason for issue in issues} == {"invalid_rate"}


def test_rejects_duplicate_compound_key() -> None:
    accepted, issues = validate_fx([fx(), fx(rate=Decimal("33.30"))])
    assert len(accepted) == 1
    assert [issue.reason for issue in issues] == ["duplicate_key"]


def test_rejects_same_base_and_quote() -> None:
    accepted, issues = validate_fx([fx(quote_ccy="USD")])
    assert accepted == []
    assert issues[0].reason == "invalid_pair"


def test_missing_macro_value_is_preserved() -> None:
    item = MacroObservation(
        source_id="fred",
        series_id="CPIAUCSL",
        observation_date=date(2026, 1, 1),
        retrieved_at=NOW,
        value=None,
        unit="index",
        frequency="monthly",
        vintage_date=None,
        release_date=None,
    )
    accepted, issues = validate_macro([item])
    assert accepted[0].value is None
    assert issues == []


def test_rejects_macro_release_after_retrieval() -> None:
    item = MacroObservation(
        source_id="fred",
        series_id="CPIAUCSL",
        observation_date=date(2026, 1, 1),
        retrieved_at=NOW,
        value=Decimal("320"),
        unit="index",
        frequency="monthly",
        vintage_date=None,
        release_date=date(2026, 1, 6),
    )
    accepted, issues = validate_macro([item])
    assert accepted == []
    assert issues[0].reason == "future_release"
