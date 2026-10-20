# FX Performance Methodology

Definitions of returns, indexed performance, volatility and drawdown used by the analytics package and the report.

## Table of Contents

- [FX risk statistics](#fx-risk-statistics)

---

This page defines how directed FX performance is computed from validated observations. A quote is expressed as quote-currency units per one base-currency unit. For USD/THB, a positive return means USD strengthened against THB (THB weakened). To measure THB against USD, invert the quote before calculating returns.

- Simple return: `S_t / S_(t-1) - 1`.
- Log return: `ln(S_t / S_(t-1))`. Log output is a floating-point value; simple returns and indexed values use `Decimal`.
- Indexed performance: `100 * S_t / S_0`, where `S_0` is the first supplied observed quote.
- Rolling N-observation return: `S_t / S_(t-N) - 1`, requiring N+1 observed quotes. Windows of 5, 20 and 60 observations can be requested; they count observations, not calendar days.
- MTD/YTD: last observed quote through the as-of date divided by the last available quote strictly before the month/year start, minus one. Return `None` if either side is absent. This baseline may be older than the immediately preceding business day; the date must be displayed to users.
- Currency ranking: compare base currencies against one common quote currency and rate type, using an identical set of observation dates. Positive return means the base currency gained against the common quote currency.

No dates are synthesized or forward-filled. These functions reject nonpositive or nonfinite rates, duplicate dates, and mixed quote conventions. Source data remain at their published observation dates. Percent returns should be multiplied by 100 only for display. Ranking different market rate types or dates would be misleading and is rejected. Results are descriptive, not forecasts or trading signals.

## FX risk statistics

Realized volatility uses sample standard deviation (`n-1`) of observed daily log returns multiplied by `sqrt(252)`. The 252 factor is a conventional trading-day approximation; actual BOT/FRED business calendars and missing observations may differ. Rolling windows of 20, 60, and 120 refer to observed return intervals, require a full window, and produce no value until enough nonmissing returns exist. A multi-day gap is one observed interval, not several zero-return days; this may understate or distort an annualized value and must be disclosed.

Drawdown is `indexed_value / maximum_index_to_date - 1`, beginning at zero. It measures the selected directed quote, so inversion changes interpretation. Historical percentile is the empirical fraction of finite historical observations less than or equal to the current value. Rolling Pearson correlation requires identical observation dates and returns no value for constant windows. Correlation is descriptive and does not imply causation.
