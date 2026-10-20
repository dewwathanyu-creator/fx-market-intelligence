# Source Registry and Data Dictionary

The series, providers, units and quote conventions held in the registry, with the coverage of the local snapshot.

## Table of Contents

- [Local snapshot](#local-snapshot)

---

The machine-readable series contract is in config/sources/registry.yaml. Provider routes and FRED IDs were checked against official documentation in October 2026. A local credentialed collection populated the October 2026 local snapshot described below; this does not establish every series' full historical coverage. A target start in 2015 is not a claim that every series has observations that far back.

| Series ID | Provider | Provider route or code | Unit and convention |
| --- | --- | --- | --- |
| bot_usdthb_interbank | BOT | DAILY_REF_RATE | THB per USD; weighted-average interbank reference rate. |
| bot_usdthb_bank_average | BOT | DAILY_AVG_EXG_RATE:USD | THB per USD; bank customer average. |
| bot_eurthb_bank_average | BOT | DAILY_AVG_EXG_RATE:EUR | THB per EUR; bank customer average. |
| bot_jpythb_bank_average | BOT | DAILY_AVG_EXG_RATE:JPY | Check provider scaling before calculations. |
| fred_fedfunds | FRED | FEDFUNDS | Monthly effective federal funds rate, percent per annum. |
| fred_dgs2 | FRED | DGS2 | Daily US 2-year Treasury yield, percent per annum. |
| fred_dtwexbgs | FRED | DTWEXBGS | Daily broad nominal US dollar index. |
| fred_cpiaucsl | FRED | CPIAUCSL | Monthly US consumer price index. |
| fred_vixcls | FRED | VIXCLS | Daily VIX index. |

BOT [Exchange Rates API](https://portal.api.bot.or.th/portal/catalogue-products/exchange-rates-1) separates interbank reference and commercial-bank average endpoints. These are not interchangeable when deriving cross-rates. FRED [observations API](https://fred.stlouisfed.org/docs/api/fred/series_observations.html) requires an API key and provides real-time revision fields. Source access, provider terms, coverage, currency scaling and release schedules must be checked during ingestion. Missing raw observations remain missing. Macro observation periods must be kept distinct from the date a value became public.

P1 ECB, BIS and Thai macro series need their own verified metadata before ingestion. They are not silently represented by these MVP entries.

## Local snapshot

The local Desktop demonstration warehouse built on 16 October 2026 contains three BOT FX series from 5 January through 30 September 2026, with 181 observations each, and five FRED series with 603 observations combined. This is observed local coverage, not guaranteed provider coverage or current market data. `bot_jpythb_bank_average` is in the registry but absent from this warehouse. Recheck source IDs, currency scaling and licensing before expanding the project or redistributing raw provider data. [The case study](CASE_STUDY.md) records two dated BOT endpoints and its query.
