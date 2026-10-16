"""Small hand-checkable macro research fixtures."""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from fx_intelligence.analytics.macro import (
    available_pairs,
    lagged_pearson,
    ols_one_factor,
    pearson,
    rate_spread,
    spearman,
)
from fx_intelligence.schemas.models import MacroObservation


def macro(value: str, release_day: int, *, unit: str = "percent per annum") -> MacroObservation:
    return MacroObservation(
        source_id="fred",
        series_id="RATE",
        observation_date=date(2025, 1, 1),
        retrieved_at=datetime(2025, 2, 1, tzinfo=UTC),
        value=Decimal(value),
        unit=unit,
        frequency="monthly",
        vintage_date=date(2025, 1, release_day),
        release_date=date(2025, 1, release_day),
    )


def test_spread_requires_matching_percentage_units():
    assert rate_spread(macro("5", 2), macro("3", 2)) == Decimal("2")
    with pytest.raises(ValueError, match="same annual percentage unit"):
        rate_spread(macro("5", 2), macro("3", 2, unit="index"))


def test_research_pairs_exclude_future_releases_and_vintages():
    x = [(date(2025, 1, day), float(day)) for day in (2, 3, 4)]
    rows = [macro("5", 3)]
    assert available_pairs(x, rows) == [(3.0, 5.0), (4.0, 5.0)]


def test_pearson_spearman_and_constant_series():
    assert pearson([1, 2, 3], [2, 4, 6]) == pytest.approx(1)
    assert spearman([1, 2, 3], [3, 2, 1]) == pytest.approx(-1)
    assert pearson([1, 1, 1], [2, 3, 4]) is None


def test_lag_uses_past_factor_not_future_factor():
    assert lagged_pearson([1, 2, 3, 4], [0, 2, 4, 6], lag=1) == pytest.approx(1)
    assert lagged_pearson([1, 2], [1, 2], lag=3) is None
    with pytest.raises(ValueError, match="nonnegative"):
        lagged_pearson([1, 2], [1, 2], lag=-1)


def test_ols_coefficient_and_sparse_input():
    fit = ols_one_factor([1, 2, 3], [3, 5, 7])
    assert fit is not None
    assert fit.intercept == pytest.approx(1)
    assert fit.slope == pytest.approx(2)
    assert fit.r_squared == pytest.approx(1)
    assert ols_one_factor([1, 1, 1], [2, 3, 4]) is None
