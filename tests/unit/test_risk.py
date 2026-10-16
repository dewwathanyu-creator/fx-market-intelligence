"""Reference checks for FX risk statistics."""

from datetime import date
from decimal import Decimal
from math import sqrt

import pytest

from fx_intelligence.analytics.performance import PerformancePoint
from fx_intelligence.analytics.risk import (
    drawdown,
    historical_percentile,
    realized_volatility,
    rolling_correlation,
    rolling_volatility,
)


def point(day: int, index: str, log_return: float | None = None) -> PerformancePoint:
    return PerformancePoint(date(2025, 1, day), "USD", "THB", Decimal(index), None, log_return)


def test_realized_volatility_uses_sample_standard_deviation():
    assert realized_volatility([0.01, 0.03], 252) == pytest.approx(sqrt(2) * 0.01 * sqrt(252))
    assert realized_volatility([0.01]) is None


def test_rolling_volatility_needs_full_nonmissing_window():
    points = [point(1, "100"), point(3, "101", 0.01), point(7, "103", 0.02)]
    values = rolling_volatility(points, 2)
    assert values[:2] == [None, None]
    assert values[2] == pytest.approx(sqrt(0.00005) * sqrt(252))


def test_drawdown_tracks_peak_on_index():
    values = drawdown([point(1, "100"), point(2, "120"), point(3, "90")])
    assert values == [Decimal(0), Decimal(0), Decimal("-0.25")]


def test_percentile_is_empirical_cdf():
    assert historical_percentile(3, [1, 2, 3, 4]) == 0.75
    assert historical_percentile(5, []) is None


def test_rolling_correlation_requires_common_dates_and_minimum_window():
    a = [(date(2025, 1, i), float(i)) for i in (1, 2, 3)]
    b = [(date(2025, 1, i), float(i * 2)) for i in (1, 2, 3)]
    assert rolling_correlation(a, b, 3) == [None, None, pytest.approx(1.0)]
    with pytest.raises(ValueError, match="identical dates"):
        rolling_correlation(a, b[:-1], 2)
