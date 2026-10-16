"""Hand-calculated directed FX performance checks."""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from fx_intelligence.analytics.performance import (
    indexed_performance,
    mtd_return,
    period_return,
    rank_currency_strength,
    rolling_return,
    ytd_return,
)
from fx_intelligence.schemas.models import FXObservation


def quote(day: int, rate: str, base: str = "USD", quote_ccy: str = "THB") -> FXObservation:
    return FXObservation(
        source_id="bot_fx_interbank_usd_thb",
        series_id=f"{base}{quote_ccy}",
        base_ccy=base,
        quote_ccy=quote_ccy,
        rate_type="interbank_reference",
        observation_date=date(2025, 1, day),
        retrieved_at=datetime(2025, 2, 1, tzinfo=UTC),
        rate=Decimal(rate),
        unit=f"{quote_ccy} per {base}",
        frequency="daily",
    )


def test_index_and_returns_show_usd_strength_thb_weakness():
    points = indexed_performance([quote(1, "40"), quote(2, "44")])
    assert [p.index for p in points] == [Decimal(100), Decimal(110)]
    assert points[0].simple_return is None
    assert points[1].simple_return == Decimal("0.1")
    assert points[1].log_return == pytest.approx(0.09531017980432493)
    assert points[1].base_ccy == "USD" and points[1].quote_ccy == "THB"


def test_inverted_quote_has_correct_direction():
    from fx_intelligence.transformation.fx import invert_fx

    points = indexed_performance([invert_fx(quote(1, "40")), invert_fx(quote(2, "44"))])
    assert float(points[1].simple_return) == pytest.approx(40 / 44 - 1)
    assert points[1].simple_return < 0


def test_rolling_uses_observations_and_needs_full_window():
    points = indexed_performance([quote(1, "40"), quote(3, "44"), quote(7, "48")])
    assert rolling_return(points, 2) == [None, None, Decimal("0.2")]
    assert rolling_return(points, 5) == [None, None, None]


def test_period_uses_previous_period_close_and_requires_it():
    rows = [quote(1, "40"), quote(2, "44")]
    assert period_return(rows, date(2025, 1, 2), date(2025, 1, 2)) == Decimal("0.1")
    assert period_return(rows, date(2025, 1, 1), date(2025, 1, 2)) is None
    assert mtd_return(rows, date(2025, 1, 2)) is None
    assert ytd_return(rows, date(2025, 1, 2)) is None


def test_ranking_requires_common_dates_and_quote_currency():
    usd = [quote(1, "40"), quote(2, "44")]
    eur = [quote(1, "42", "EUR"), quote(2, "43", "EUR")]
    ranked = rank_currency_strength({"USD": usd, "EUR": eur})
    assert [row.currency for row in ranked] == ["USD", "EUR"]
    assert ranked[0].return_value == Decimal("0.1")
    with pytest.raises(ValueError, match="common observation dates"):
        rank_currency_strength({"USD": usd, "EUR": [quote(1, "42", "EUR"), quote(3, "43", "EUR")]})
