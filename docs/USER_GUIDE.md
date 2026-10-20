# User Guide: Reading the FX Market Intelligence Report

A guide for analysts who open the six-page Power BI report. It explains what each page shows, how to read a quote, how the data is refreshed and which limits to keep in mind before citing a number.

## Table of Contents

- [Purpose](#purpose)
- [How to Read Every Page](#how-to-read-every-page)
- [Page Reference](#page-reference)
- [Filters, Navigation and Drillthrough](#filters-navigation-and-drillthrough)
- [Data Sources](#data-sources)
- [Is the Data Live, and How Is It Updated](#is-the-data-live-and-how-is-it-updated)
- [Limitations](#limitations)

---

## Purpose

The report explores the Thai baht against the US dollar and the euro, together with selected US macroeconomic series. It answers three questions: how the exchange rate changed, how volatile it was, and where each number came from. It suits analysis and market monitoring. It is **not** a live price, investment advice, a forecasting system or an order-execution system.

Open `dashboard/powerbi/FX Market Intelligence Dashboard.pbip` in Power BI Desktop on a machine that holds the project's generated data workbook. The left menu and the bottom tabs switch pages. Three left-menu labels are shortened (`Currencies`, `Thailand FX`, `Data Quality`), but the real page names remain in full. In Desktop edit mode, hold `Ctrl` and click a navigation button.

## How to Read Every Page

1. **Title and subtitle** state the currency pair, source, rate type or unit of the page.
2. **Top filters** select a date range and the items the page supports, such as FX source, currency pair, rate type or FRED indicator. `All` means the filter is not restricting the data. Some cards stay pinned to a source and pair named on the card so that different rate types are never mixed.
3. **Four KPI cards** show a value or date for the selected context. A `--` means no usable value exists in that context, for example the EUR/THB card when only USD/THB is selected.
4. **The main chart** has observation dates on its horizontal axis, not the time the data was retrieved. Hover over a point or line to see the tooltip, then check the series name and unit.
5. **The context panel** on the right gives the starting point, calculation method, unit, frequency, coverage or pending items, depending on the page.
6. **The footer** shows the source, `OBSERVED THROUGH` (the latest observation date under the current filters) and `WAREHOUSE BUILT` (when the warehouse was built). `WAREHOUSE BUILT` is **not** the time Power BI last read the file and not the time the provider published the data.

If a result looks unusual, check the date range, source, currency pair and rate type first. BOT interbank and BOT commercial-bank average rates are different series and must not be read as one price.

### Quote direction

`USD/THB` means **THB per one US dollar**. A value of 33.50 means 1 USD equals 33.50 THB in that series. When the USD/THB line rises, the dollar strengthens and the baht **depreciates**. When it falls, the baht strengthens. `EUR/THB` reads the same way (THB per euro). The percentage change of either pair is a **change in the quote**, not the investment return of a baht holder.

## Page Reference

| Page | What it shows | How to use it |
| --- | --- | --- |
| **Market Overview** | Latest BOT interbank USD/THB, change from the prior observation, 20-observation volatility and latest date; the USD/THB chart; the first quote and date of the selected range with `Period move` | Select the date range first, then compare the latest level with the first point and the direction of the chart. `Move vs prior obs.` is the change over the latest observation interval. `Period move` compares the first and last values of the selected range. A positive value on the USD/THB quote means a weaker baht, not an investor gain. |
| **Currency Explorer** | BOT bank-average USD/THB and EUR/THB, the period move of each pair, an indexed two-line chart (base `100`) and a table of date, pair and rate | Compare pairs by **percentage change** from a common index base rather than comparing 33 THB per USD with 38 THB per EUR directly. Read the chart and table under comparable dates and rate types. After a drillthrough from Overview with USD/THB selected, the EUR card may show `--` because it is filtered out. |
| **Macro Drivers** | USD/THB interbank and the selected FRED indicator in **separate** charts; the latest value and observation date of both; series ID, unit and frequency | After choosing an indicator, always read the unit in the right panel (index, percent per annum or VIX). Two series moving together is an observed pattern. It does not prove cause, nor that the macro value was public on that day, especially for monthly series. |
| **Risk & Volatility** | Realized volatility over 20 and 60 observations, quote drawdown and latest date; a two-line volatility chart; the calculation method and the number of FX observations available | Check whether short-term movement is larger or smaller than longer-term movement. Volatility is the sample standard deviation of log returns multiplied by the square root of 252, over **observed** intervals rather than calendar days. Drawdown is the decline of the **quote index** from its running peak, so it is not an investor loss and must be read with the USD/THB direction. |
| **Thailand FX Monitor** | BOT bank-average USD/THB and EUR/THB, period moves and an indexed comparison; an NEER/REER panel | Follow the baht against two currencies on the same rate type. The NEER/REER panel reads `pending official series` because **no effective exchange rate index is loaded**. Two pairs are not enough to describe the baht against all trading partners. |
| **Data Quality & Research** | Row counts for FX and macro data, the latest FX and macro observation dates, the number of FX observations per day, and a table of source, rate type and date | Check that the data has the expected count and date range. The daily count chart helps reveal gaps or incomplete series. A high row count does not guarantee accuracy or freshness, so compare the observation date with the warehouse build time and the Power BI refresh before concluding. |

**Worked example.** If USD/THB rises from 33.00 to 33.66 THB per USD in the selected range, `Period move` is about +2%. The quote rose 2%, which means the baht weakened against the dollar. Next, check Risk & Volatility for whether the move coincided with higher volatility, and Macro Drivers for how the dollar index or Treasury yield moved over nearby dates. Before writing a conclusion, confirm the observation dates, units and frequencies, and avoid saying that any macro series "caused" the move on the strength of this chart alone.

## Filters, Navigation and Drillthrough

- Change `Date range` to view another window. The latest-value cards show the **latest value inside the selected range**, which need not be today. Some days have no observation because of holidays or series frequency.
- Use `FX source`, `Currency pair` and `Rate type` to restrict a page. Do not mix interbank and commercial-bank average rates when comparing results.
- On Macro Drivers, `FRED indicator` switches the economic series. Re-read `Unit` and `Frequency` every time.
- Hover over a chart for a single day's value. In Desktop edit mode, `Ctrl`+click the left menu to change page.
- From a point on the Market Overview chart, right-click and choose `Drillthrough`, then `Currency Explorer` to open the detail for that pair. The target page filters to the pair. `Ctrl`+click `← Back to source` in the left bar to return. In normal reading view the button works without `Ctrl`.
- If a chart or card is blank after a drillthrough, check the Filters pane and the page date filter, then use Back or change the filter.

## Data Sources

| Source | Series loaded into the current report | Meaning and caution |
| --- | --- | --- |
| **Bank of Thailand (BOT)** | `DAILY_REF_RATE` for USD/THB interbank weighted average; `DAILY_AVG_EXG_RATE` for USD/THB and EUR/THB commercial-bank average | Official daily data in different rate types. These are observations, not live trading prices. JPY is in the registry but not in this warehouse. |
| **FRED, Federal Reserve Bank of St. Louis** | `FEDFUNDS` (monthly federal funds rate), `DGS2` (daily 2-year Treasury yield), `DTWEXBGS` (daily broad dollar index), `CPIAUCSL` (monthly consumer price index), `VIXCLS` (daily VIX) | Each series has its own unit and frequency. An observation date is not the date the value was published, and a release date the provider does not supply is not guessed. |

The data path is **BOT and FRED APIs → Python collection and validation → DuckDB calculation and tables → `dashboard/powerbi/data/fx_model.xlsx` → Power BI import model → six report pages**. ECB, BIS, NEER and REER are not yet loaded. Retrieval dates and missing observations are kept as they are, and missing dates are never filled automatically.

## Is the Data Live, and How Is It Updated

**The data is not live.** Power BI Desktop uses data imported from a local workbook. Leaving the report open does not follow the market, and `Home → Refresh` alone reads the existing workbook. It does not call the BOT or FRED APIs again.

A full update has two separate steps:

1. From the project root, open PowerShell in a Python environment with the project installed and with `FRED_API_KEY` and `BOT_API_KEY` set in a Git-ignored `.env` file. Run `python -m fx_intelligence.orchestration.refresh refresh --root .`. This fetches new data, validates it, updates DuckDB and rebuilds the Power BI workbook. Status is written to `data/processed/operations/refresh.jsonl`. If the job fails or reports a stale source, fix the cause before using the result.
2. Open `dashboard/powerbi/FX Market Intelligence Dashboard.pbip` in Power BI Desktop and select **Home → Refresh**. Wait for the load, then check `OBSERVED THROUGH`, the chart and card values and `WAREHOUSE BUILT` on at least one page. Only then does the Desktop report reflect the new workbook.

A GitHub Actions definition runs the ETL on weekdays at 14:00 Thailand time. It is **not active** until the repository is pushed with a Windows runner, project path and secrets configured. Even when the ETL runs on schedule, Power BI Desktop must still be refreshed separately. The Power BI service is not configured for publishing or refresh. If the project moves to another machine, change the workbook path in Power BI first.

The recorded snapshot holds three BOT series with 543 rows and five FRED series with 603 rows. It covers FX observations from 5 January to 30 September 2026, and the warehouse was built on 16 October 2026. These figures are a **snapshot at that run** and are not always the latest prices or status. For any real decision, confirm that the latest ETL run succeeded, Power BI was refreshed, no source is stale and the observation dates of the series in use are current enough.

## Limitations

- Series with different frequencies and holidays need not line up. Two lines that appear to move together do not prove a causal relationship.
- Some FRED series are revised after publication. Observation and vintage dates do not guarantee that an analyst at the time saw today's value.
- In the volatility page, 20 and 60 refer to observed return intervals, and the square root of 252 is an annualization assumption, not the number of data days in every year.
- Sample values and screenshots in the README are images from the build date. The `.pbip` is the editable report, and the real data files stay local and are not committed to Git.

For calculation methods see [METHODOLOGY.md](METHODOLOGY.md). For Power BI tables and formulas see [POWERBI_MODEL.md](POWERBI_MODEL.md). For data definitions see [DATA_DICTIONARY.md](DATA_DICTIONARY.md). For update problems see [RUNBOOK.md](RUNBOOK.md).
