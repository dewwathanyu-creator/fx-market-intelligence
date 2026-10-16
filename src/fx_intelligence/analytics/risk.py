"""Descriptive risk statistics using observed FX intervals only."""

from datetime import date
from decimal import Decimal
from math import isfinite, sqrt
from statistics import correlation, stdev

from fx_intelligence.analytics.performance import PerformancePoint


def realized_volatility(log_returns: list[float], annualization: int = 252) -> float | None:
    """Sample standard deviation of observed log returns times sqrt(annualization)."""
    if annualization <= 0:
        raise ValueError("annualization must be positive")
    if any(not isfinite(value) for value in log_returns):
        raise ValueError("returns must be finite")
    if len(log_returns) < 2:
        return None
    return stdev(log_returns) * sqrt(annualization)


def rolling_volatility(
    points: list[PerformancePoint], window: int, annualization: int = 252
) -> list[float | None]:
    """Trailing volatility over N observed return intervals, with no gap filling."""
    if window < 2:
        raise ValueError("window must contain at least two returns")
    if any(
        points[i].observation_date >= points[i + 1].observation_date for i in range(len(points) - 1)
    ):
        raise ValueError("points must have strictly increasing dates")
    output: list[float | None] = []
    for i in range(len(points)):
        returns = [p.log_return for p in points[max(0, i - window + 1) : i + 1]]
        output.append(
            realized_volatility(returns, annualization)
            if len(returns) == window and all(value is not None for value in returns)
            else None
        )
    return output


def drawdown(points: list[PerformancePoint]) -> list[Decimal]:
    """Drawdown of an explicitly indexed FX series from its observed peak."""
    peak: Decimal | None = None
    result: list[Decimal] = []
    for point in points:
        if point.index <= 0:
            raise ValueError("positive indexed values required")
        peak = max(peak, point.index) if peak is not None else point.index
        result.append(point.index / peak - 1)
    return result


def historical_percentile(value: float, history: list[float]) -> float | None:
    """Empirical percentile: fraction of finite historical values <= value."""
    if not isfinite(value) or any(not isfinite(item) for item in history):
        raise ValueError("finite values required")
    return sum(item <= value for item in history) / len(history) if history else None


def rolling_correlation(
    left: list[tuple[date, float]], right: list[tuple[date, float]], window: int
) -> list[float | None]:
    """Pearson correlation on identical observed dates; constant windows yield None."""
    if window < 2:
        raise ValueError("window must contain at least two observations")
    if [d for d, _ in left] != [d for d, _ in right]:
        raise ValueError("identical dates required")
    if any(not isfinite(v) for _, v in left + right):
        raise ValueError("finite values required")
    output: list[float | None] = []
    for i in range(len(left)):
        if i + 1 < window:
            output.append(None)
            continue
        x = [v for _, v in left[i + 1 - window : i + 1]]
        y = [v for _, v in right[i + 1 - window : i + 1]]
        output.append(correlation(x, y) if len(set(x)) > 1 and len(set(y)) > 1 else None)
    return output
