# FX Market Intelligence Dashboard — Project specification

## Purpose

Create an auditable, reproducible FX market intelligence platform. It should turn official currency and macroeconomic time series into defensible analysis and a six-page Power BI report. Primary users are financial, investment, treasury, and data analysts. This is decision support and research, not a trading system or investment recommendation.

## Business questions

- How has THB moved against USD and regional currencies over selected periods?
- Is a THB move specific to Thailand, or associated with broad USD and regional moves?
- How do interest-rate differentials, inflation, dollar strength, risk sentiment, yields, and gold relate to FX changes?
- How unusual is current USD/THB volatility relative to its history?
- How do current conditions compare with prior stress or policy-shift periods?

## Scope and release order

| Level | Capabilities |
| --- | --- |
| MVP | Historical FX dashboard; currency performance and ranking; volatility and drawdown; macro indicator dashboard; automated data pipeline. |
| Advanced | Rolling correlation; rate differentials; official NEER/REER analysis; exploratory macro regimes; FX exposure scenarios. |
| Future | Forecasting/ML; generated commentary; intraday monitoring. |

MVP excludes automated trading, claims of guaranteed forecasts, tick data, arbitrage execution, and derivatives pricing. Prioritize Tasks 01–08 as a sound data and analytics base. Start Power BI after Task 08; Task 09 adds macro research before the full report is delivered.

## Data source policy

| Priority | Provider | Intended series | Frequency / caveat |
| --- | --- | --- | --- |
| P0 | Bank of Thailand (BOT) | USD/THB and THB cross rates | Daily; weighted-average interbank USD/THB and average exchange rates are distinct rate types. |
| P0 | FRED | Policy rates, US yields, broad USD indices, CPI and other macro factors | Daily to monthly; preserve revision/vintage metadata when available. |
| P1 | ECB | EUR reference rates | Daily; reference data, not execution prices. |
| P1 | BIS | Effective exchange-rate indices | Use published frequency and methodology. |
| P1 | BOT economic statistics | Thai CPI, interest rates, NEER/REER | Monthly or provider-specific. |

Official discovery pages: [BOT exchange rates](https://portal.api.bot.or.th/portal/catalogue-products/exchange-rates-1), [FRED API](https://fred.stlouisfed.org/docs/api/fred/), [ECB API](https://data.ecb.europa.eu/help/api/overview), and [BIS EER](https://data.bis.org/topics/EER). These are intended sources; Task 02 must verify live access, licensing, exact series IDs, historical coverage, and provider rules before ingestion. Target history begins in 2015 only where a series actually supports it. FX refreshes daily; macro refreshes on its true release cadence. Store credentials in environment variables, respect rate limits, and use retry/backoff and incremental fetch. Keep missing raw observations missing.

## Financial methodology

For a quoted rate `S_t` in quote-currency units per one base-currency unit, simple return is `S_t / S_(t-1) - 1`; log return is `ln(S_t / S_(t-1))`. For USD/THB, a positive rate return means USD appreciation and THB depreciation. Invert or re-express pairs before any cross-currency strength ranking.

Index performance to 100 at a stated start date. Calculate period returns (MTD/YTD), rolling returns (5/20/60 observations), and cross-rates only from compatible source, date, rate type, and quote conventions. The initial realized-volatility convention is sample standard deviation of daily log returns times `sqrt(252)`; document the trading-calendar assumption and do not treat 252 as universally valid. Planned windows are 20/60/120 observations. Drawdown applies to a clearly defined indexed series, not to an unlabeled exchange-rate quote.

Macro analysis may use Pearson/Spearman and rolling correlation, lag analysis, rate spreads, and exploratory OLS with diagnostics. Align by information availability (release date/vintage), not observation date alone; do not use future-revised values in historical analyses. State units and transformations. Correlation and regression do not establish causation. For THB competitiveness, use official BOT/BIS NEER and REER series rather than inventing an MVP trade-weighted index.

## Dashboard requirements

| Page | Main question | Planned views |
| --- | --- | --- |
| 01 Market Overview | What is happening now? | KPI cards, FX trend, performance heatmap. |
| 02 Currency Explorer | How do currencies compare? | Indexed performance, ranking. |
| 03 Macro Drivers | What moves alongside FX? | Rate/inflation/USD views, scatter and time series. |
| 04 Risk & Volatility | How unusual is market risk? | Rolling volatility, drawdown, correlations. |
| 05 Thailand FX Monitor | How does THB compare broadly? | USD/THB and official NEER/REER. |
| 06 Data Quality & Research | How trustworthy and interpretable are results? | Data health and sourced research notes. |

Provide currency, date range, frequency, and macro indicator slicers. Each page displays data source, observation date, and last refresh. Numbers in mockups are illustrative, never current market facts.

## End deliverables

1. Six-page interactive Power BI report.
2. Automated Python/DuckDB FX warehouse with SQL views, data dictionary, and shareable sample data.
3. Tested financial analytics package.
4. One evidence-based USD/THB research case study with regional comparison and limitations.
5. Reproducible GitHub repository with architecture, methodology, screenshots, and test evidence.
6. Project summary grounded in measured project facts, without invented impact claims.

## Quality and risk gates

Use unit tests, schema checks, duplicate-key checks, quote and cross-rate reconciliation, release-aware time-series tests, integration tests, Power BI parity checks, and clean-environment reproduction. Keep ETL refresh and Power BI refresh as separate operating steps; an updated data file alone does not refresh a published BI report. Document API coverage, missing/revised data, rate-type mismatches, refresh failures, and statistical limitations.
