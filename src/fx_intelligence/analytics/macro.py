"""Exploratory one-factor statistics on release-aware observations."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from math import isfinite
from statistics import correlation, mean

from fx_intelligence.schemas.models import MacroObservation
from fx_intelligence.transformation.alignment import align_macro


@dataclass(frozen=True)
class OLSResult:
    n: int
    intercept: float
    slope: float
    r_squared: float
    residual_sum_squares: float


def rate_spread(left: MacroObservation, right: MacroObservation) -> Decimal:
    """Spread in percentage points between rates with the same annual unit."""
    if left.unit != "percent per annum" or right.unit != "percent per annum":
        raise ValueError("same annual percentage unit required")
    if left.value is None or right.value is None:
        raise ValueError("both rates must be observed")
    return left.value - right.value


def available_pairs(
    dated_returns: list[tuple[date, float]], macro_rows: list[MacroObservation]
) -> list[tuple[float, float]]:
    """Pair each return only with macro information available by that date."""
    if any(not isfinite(value) for _, value in dated_returns):
        raise ValueError("returns must be finite")
    aligned = align_macro(macro_rows, [day for day, _ in dated_returns])
    return [
        (value, float(row.value))
        for (_, value), row in zip(dated_returns, aligned, strict=True)
        if row is not None and row.value is not None and row.value.is_finite()
    ]


def _check_pair(x: list[float], y: list[float]) -> None:
    if len(x) != len(y):
        raise ValueError("series lengths must match")
    if any(not isfinite(v) for v in x + y):
        raise ValueError("finite values required")


def pearson(x: list[float], y: list[float]) -> float | None:
    _check_pair(x, y)
    if len(x) < 2 or len(set(x)) < 2 or len(set(y)) < 2:
        return None
    return correlation(x, y)


def _ranks(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(values):
        j = i + 1
        while j < len(values) and ordered[j][1] == ordered[i][1]:
            j += 1
        average_rank = (i + 1 + j) / 2
        for index, _ in ordered[i:j]:
            ranks[index] = average_rank
        i = j
    return ranks


def spearman(x: list[float], y: list[float]) -> float | None:
    _check_pair(x, y)
    return pearson(_ranks(x), _ranks(y))


def lagged_pearson(factor: list[float], outcome: list[float], lag: int) -> float | None:
    """Correlate factor at t with outcome at t+lag, in observed steps."""
    if lag < 0:
        raise ValueError("lag must be nonnegative")
    _check_pair(factor, outcome)
    if lag >= len(factor):
        return None
    return pearson(factor[: len(factor) - lag], outcome[lag:]) if lag else pearson(factor, outcome)


def ols_one_factor(x: list[float], y: list[float]) -> OLSResult | None:
    """Fit y=intercept+slope*x; no causal interpretation is implied."""
    _check_pair(x, y)
    if len(x) < 3 or len(set(x)) < 2:
        return None
    x_bar, y_bar = mean(x), mean(y)
    xx = sum((value - x_bar) ** 2 for value in x)
    slope = sum((a - x_bar) * (b - y_bar) for a, b in zip(x, y, strict=True)) / xx
    intercept = y_bar - slope * x_bar
    residual_sum_squares = sum((b - intercept - slope * a) ** 2 for a, b in zip(x, y, strict=True))
    total_sum_squares = sum((b - y_bar) ** 2 for b in y)
    r_squared = 1 - residual_sum_squares / total_sum_squares if total_sum_squares else 0.0
    return OLSResult(len(x), intercept, slope, r_squared, residual_sum_squares)
