# FX performance methodology

Task 07 computes directed FX performance from validated observations. A quote is expressed as quote-currency units per one base-currency unit. For USD/THB, a positive return means USD strengthened against THB (THB weakened). To measure THB against USD, invert the quote before calculating returns.

- Simple return: `S_t / S_(t-1) - 1`.
- Log return: `ln(S_t / S_(t-1))`. Log output is a floating-point value; simple returns and indexed values use `Decimal`.
- Indexed performance: `100 * S_t / S_0`, where `S_0` is the first supplied observed quote.
- Rolling N-observation return: `S_t / S_(t-N) - 1`, requiring N+1 observed quotes. Windows of 5, 20 and 60 observations can be requested; they count observations, not calendar days.
- MTD/YTD: last observed quote through the as-of date divided by the last available quote strictly before the month/year start, minus one. Return `None` if either side is absent. This baseline may be older than the immediately preceding business day; the date must be displayed to users.
- Currency ranking: compare base currencies against one common quote currency and rate type, using an identical set of observation dates. Positive return means the base currency gained against the common quote currency.

No dates are synthesized or forward-filled. These functions reject nonpositive or nonfinite rates, duplicate dates, and mixed quote conventions. Source data remain at their published observation dates. Percent returns should be multiplied by 100 only for display. Ranking different market rate types or dates would be misleading and is rejected. Results are descriptive, not forecasts or trading signals.
