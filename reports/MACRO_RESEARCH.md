# Exploratory FX and macro research protocol

This protocol studies whether available interest-rate, inflation, broad-dollar and risk-sentiment observations co-move with directed USD/THB returns. It is descriptive research, not evidence of causality or a trading signal.

## Reproducible method

1. Select one directed FX rate type and compute observed-date returns with `analytics.performance`.
2. Align each macro series with `align_macro` using release date and vintage date. Exclude any value unavailable by the return date. A missing release date remains unavailable.
3. Convert rates to a common `percent per annum` unit before calculating percentage-point spreads. Do not subtract an index from a rate.
4. Run Pearson and Spearman correlation on paired, finite observations. Record sample size, date range, and whether observations repeat between macro releases.
5. Explore nonnegative observed-step lags: factor at `t` against FX outcome at `t+lag`. Document that unequal calendars make an observed-step lag different from a fixed number of calendar days.
6. Fit `y = intercept + slope*x` only when at least three pairs and a varying factor exist. Report coefficient, intercept, R-squared, residual sum of squares and sample size. Check residual time patterns and outliers before drawing any substantive conclusion.

## Interpretation limits

- A macro observation repeated across many daily FX returns reduces effective independence; significance tests need an autocorrelation-aware design and are omitted here.
- FRED values may be revised. A historical claim requires a genuine contemporaneous vintage and verified release calendar; an unavailable vintage is not fabricated.
- Samples, publication lags, holidays, rate-type choice, and quote inversion can materially change a result.
- OLS here has one factor, no robust standard errors, controls, or causal identification. No p-values or predictive claims are issued.

This protocol intentionally contains no market finding. The descriptive USD/THB comparison is in the [case study](../docs/CASE_STUDY.md).
