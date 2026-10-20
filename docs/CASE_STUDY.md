# USD/THB research case: January–September 2026 quote depreciation

A descriptive comparison of USD/THB and EUR/THB quotes between the first and last common observations in the 2026 local snapshot, with a reproducible query and stated limits.

## Table of Contents

- [Question and evidence](#question-and-evidence)
- [Reproduce the numbers](#reproduce-the-numbers)
- [What this does not establish](#what-this-does-not-establish)

---

## Question and evidence

How did the THB-per-USD reference quote change between the first and last common BOT observations in the local 2026 snapshot, and was the direction also visible in comparable customer bank-average USD and EUR quotes? This is a **descriptive period comparison**, not an explanation of the move or a trading signal.

The data come from the local Git-ignored `data/processed/fx.duckdb` warehouse, built **2026-10-16 12:09 Asia/Bangkok**, with BOT observations dated **2026-01-05** and **2026-09-30**. The [BOT Exchange Rates product](https://portal.api.bot.or.th/portal/catalogue-products/exchange-rates-1) explicitly offers a weighted-average interbank THB/USD reference route and a separate commercial-bank customer-average route. We keep them separate. Source IDs, endpoint codes and units are documented in the [data dictionary](DATA_DICTIONARY.md) and [registry](../config/sources/registry.yaml). These are local imported observations, not proof of a current live quote or independent confirmation of every provider historical value.

| BOT source / rate type | Pair and quote unit | 2026-01-05 | 2026-09-30 | Quote change |
| --- | --- | ---: | ---: | ---: |
| `bot_usdthb_interbank` / `DAILY_REF_RATE` / weighted-average interbank | USD/THB, THB per USD | 31.3880 | 33.5480 | +6.88% |
| `bot_usdthb_bank_average` / `DAILY_AVG_EXG_RATE:USD` / customer bank average | USD/THB, THB per USD | 31.4254 | 33.5541 | +6.77% |
| `bot_eurthb_bank_average` / `DAILY_AVG_EXG_RATE:EUR` / customer bank average | EUR/THB, THB per EUR | 36.7153 | 38.0210 | +3.56% |

Each change is `100 × (last / first − 1)`, rounded to two decimals. For example, interbank USD/THB is `100 × (33.5480 / 31.3880 − 1) = +6.8816…%`; the index with 5 January = 100 ends at **106.88**. A higher THB-per-USD quote means **THB depreciation against USD** over these endpoints. The two customer bank-average quotes also rose, with a larger percentage change for USD/THB than EUR/THB. This is a bilateral observation, not a broad trade-weighted THB-strength conclusion. The interbank and bank-average rows are **not** spliced into one series or compared as identical rate types.

## Reproduce the numbers

After a supervised BOT/FRED run has built the local warehouse, run this read-only query with DuckDB (or from Python's DuckDB connection):

```sql
SELECT source_id, series_id, pair_id, rate_type, observation_date, rate,
       unit, retrieved_at
FROM fact_fx_rates
WHERE observation_date IN (DATE '2026-01-05', DATE '2026-09-30')
  AND source_id IN (
      'bot_usdthb_interbank',
      'bot_usdthb_bank_average',
      'bot_eurthb_bank_average'
  )
ORDER BY source_id, observation_date;
```

Check both dates exist for each source, calculate each change **within** its source and rate type, and retain its retrieval timestamp. The displayed local warehouse contains **181 observations per FX source** between 5 January and 30 September 2026 (543 FX rows total). These counts and the warehouse build time come from `fact_fx_rates` and `etl_run_log`; they can differ after a fresh run. The [Market Overview](../dashboard/screenshots/final/market-overview.png) and [Currency Explorer](../dashboard/screenshots/final/currency-explorer.png) screenshots show the corresponding interbank and customer-average contexts. The Power BI snapshot's date slicer and current observation must be checked before comparing its cards with this endpoint table.

## What this does not establish

- The endpoints do not identify an external policy event or show why the exchange rate changed. FRED macro observations are available in the project, but their recorded observation dates alone are insufficient to establish contemporaneous release availability; [FRED's API documentation](https://fred.stlouisfed.org/docs/api/fred/series_observations.html) distinguishes observation dates and real-time periods. No causal macro conclusion is drawn.
- Both BOT routes are reference/statistical rates, not executable prices. Holidays and missing dates were not filled; the 181 values are observed dates, not 181 consecutive calendar days.
- Only two foreign currencies are in this local bank-average comparison. Official NEER/REER are pending, so the result cannot describe overall THB competitiveness.
- The local 30 September endpoint and 16 October build time are historical snapshot metadata. A later refresh may revise values or coverage; repeat the query and check the source ledger before reusing any figure.
