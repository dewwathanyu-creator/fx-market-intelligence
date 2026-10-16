from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from fx_intelligence.schemas.models import FXObservation
from fx_intelligence.transformation.fx import cross_rate, invert_fx, month_end


def fx(
    base: str, quote: str, rate: str, rate_type: str = "commercial_bank_average"
) -> FXObservation:
    return FXObservation(
        source_id="bot",
        series_id=f"{base}{quote}",
        base_ccy=base,
        quote_ccy=quote,
        rate_type=rate_type,
        observation_date=date(2026, 1, 2),
        retrieved_at=datetime(2026, 1, 3, tzinfo=UTC),
        rate=Decimal(rate),
        unit=f"{quote} per {base}",
        frequency="daily",
    )


def test_inversion_is_reciprocal() -> None:
    original = fx("USD", "THB", "40")
    inverse = invert_fx(original)
    assert (inverse.base_ccy, inverse.quote_ccy) == ("THB", "USD")
    assert inverse.rate == Decimal("0.025")
    assert invert_fx(inverse).rate == original.rate


def test_cross_rate_identity() -> None:
    eur_thb = fx("EUR", "THB", "44")
    usd_thb = fx("USD", "THB", "40")
    eur_usd = cross_rate(eur_thb, usd_thb)
    assert (eur_usd.base_ccy, eur_usd.quote_ccy) == ("EUR", "USD")
    assert eur_usd.rate == Decimal("1.1")


def test_cross_rate_rejects_mixed_rate_types() -> None:
    with pytest.raises(ValueError, match="rate type"):
        cross_rate(fx("EUR", "THB", "44"), fx("USD", "THB", "40", "interbank"))


def test_month_end_uses_last_available_observation() -> None:
    first = fx("USD", "THB", "40")
    last = FXObservation(
        **{**first.__dict__, "observation_date": date(2026, 1, 30), "rate": Decimal("41")}
    )
    sampled = month_end([first, last])
    assert sampled[0].observation_date == last.observation_date
    assert sampled[0].rate == last.rate
    assert sampled[0].frequency == "monthly"
