# Power BI Report QA

A record of the checks applied to the six-page Power BI report: what the report is expected to show, which automated tests protect it, which defects were found in Power BI Desktop and how they were resolved.

## Table of Contents

- [Report Contract](#report-contract)
- [Automated Checks](#automated-checks)
- [Desktop Visual QA](#desktop-visual-qa)
- [Interaction Checks](#interaction-checks)
- [Interface Polish](#interface-polish)
- [Interpretation Limits](#interpretation-limits)

---

## Report Contract

The editable report is `dashboard/powerbi/FX Market Intelligence Dashboard.pbip`. `dashboard/powerbi/build_report.py` deterministically writes six PBIR page definitions from the semantic model. All cards, trends, tables and slicers bind to model fields; no static sample numbers are embedded in the visuals.

| Page | Business question | Expected check |
| --- | --- | --- |
| Market Overview | What happened to the BOT USD/THB interbank quote? | Latest THB per USD quote, observed return, 20-observation volatility, date and same-series history. A rising THB per USD quote denotes THB depreciation. |
| Currency Explorer | How do the comparable bank-average USD and EUR quotes move? | Separate quotes, indexed trends, shared rate type and aligned observation dates. The pair is available as a drillthrough target. |
| Macro Drivers | How do FX and selected macro observations move over time? | FRED selector, separate charts with separate units, observation dates, source and frequency. Association is descriptive only. |
| Risk & Volatility | How have quote volatility and drawdown evolved? | 20- and 60-observation realized volatility, latest quote drawdown, method and coverage. Volatility uses the 252-observation annualization convention. |
| Thailand FX Monitor | What do BOT bilateral bank-average quotes show? | USD/THB and EUR/THB rate cards and indexed trends. NEER/REER panels state that the series are pending. |
| Data Quality & Research | What data were imported, and when? | Warehouse row counts, latest FX and macro observation dates, daily FX coverage and a source ledger. Warehouse build time is distinct from Power BI refresh time. |

Every page contains page navigation, date and source context, a current observation date and a `Last Refresh` card from the semantic model. The source ledger keeps source ID, pair, rate type, observation date and, where available, retrieval timestamp. Dates on a visual are model-filtered, and missing observations are never forward-filled.

## Automated Checks

- `tests/integration/test_powerbi_report.py` (9 tests) covers the page inventory, navigation targets, data views, freshness labels, drillthrough binding, visual field references, Desktop rendering contracts, absence of extra pages, explicit Gregorian timestamp parsing, sufficient Macro chart size and the interbank-only Risk context.
- The full suite of 74 tests passes with `python -m pytest -q`.
- `python -m ruff check .` and `python -m ruff format --check .` pass.

## Desktop Visual QA

The report was opened in Power BI Desktop and each page was inspected. The first review confirmed that the report loaded and that the Overview cards and chart queried real model data. It also revealed five defects, all since fixed in the report generator:

1. **Theme-blue shapes.** Page and sidebar shapes rendered in theme blue because their fill colors lacked a `default` state selector. The generator now sets explicit selected fill entries.
2. **Missing navigation labels.** Buttons showed no text because Power BI expects separate unselected `show` and `default`-selected text entries. The generator now uses the documented two-entry pattern, including fill, shape and icon placement.
3. **Obsolete page directory.** An empty `Page 1` directory remained although `pages.json` listed six pages. It was removed.
4. **Mixed rate types on Overview.** The Overview ledger showed EUR/THB bank-average rows under an interbank title. It was replaced with cards calculated from the fixed USD/THB interbank series and selected period.
5. **Year 1483 in `Last Refresh`.** Locale-dependent parsing of the workbook's text timestamp was the likely cause. The Power Query type conversion now uses `en-US` for Gregorian parsing, and the value was rechecked after a Desktop refresh.

A second review confirmed the page color, navigation text, six-page count, interbank-only context cards and the 2026 warehouse date. Two small clipping issues remained (the First quote card value and the last sidebar label). The generator now gives the quote more width, shortens the label and hides redundant footer labels.

A third review of all six pages confirmed that the bank-average comparisons render, the Thailand pending-series note is explicit, and the quality cards show 543 FX rows and 603 macro rows. It found three further issues:

- The Overview period move value was clipped.
- Both Macro line charts had no visible plot at their short height.
- The Risk raw table began with EUR/THB bank-average rows under an interbank heading.

The generator now uses full-width compact cards for the Overview period context, two full-height Macro charts with selected-series metadata cards, and an interbank-specific Risk method panel. The Currency Explorer table is labeled as underlying observations rather than an aligned comparison table.

A final check of the three corrected pages confirmed the fixes in Desktop. The Overview period move is visible as +6.9%; both Macro charts show observed lines with the series, unit and frequency; and the Risk panel shows BOT USD/THB interbank, the sample log-return volatility method and 181 observed FX dates.

## Interaction Checks

| Check | Result |
| --- | --- |
| Overview date slicer | Passed: the view changed with the selected range. |
| Line tooltip | Passed: the Overview Rate tooltip appeared. |
| Left navigation (`Ctrl`+click) | Passed: reached Currency Explorer. |
| Drillthrough from Overview | Passed after two fixes (below). |
| Back to source | Passed: returned to Market Overview. |

The drillthrough check exposed two defects. First, the Overview trend did not project the pair field used by the Currency Explorer target. The Overview chart now includes `tbl_dim_fx_pair[pair_id]` as its Series field, so each plotted USD/THB point carries the target field. Second, the chart point's date filter was carried over, leaving a single point and blank EUR cards. The target page binding now sets `acceptsFilterContext` to `None`, so only the explicit pair drillthrough field is carried, and a Back button is present. After the fix, the target shows a full USD/THB indexed trend with the `pair_id is USD/THB` filter. EUR values are intentionally blank in this USD/THB drillthrough context.

The six final page screenshots are in `dashboard/screenshots/final/`. The account name in the Power BI window chrome is masked.

## Interface Polish

A later polish kept all six pages and their model bindings. It enlarged primary text, strengthened secondary-text contrast, added selected-navigation and card accents, used a more distinct two-series palette, hid duplicate chart auto titles and reduced the two detail tables to three relevant columns. After the first polish the chart, four KPI values, context cards and footer rendered correctly, but three enlarged sidebar names were clipped, so the generator shortened them to `Currencies`, `Thailand FX` and `Data Quality`. Static PBIR checks and the full Python suite passed after the correction. The final sidebar labels and the other five pages have not been re-verified visually since this change, and the six final screenshots show the earlier accepted version.

## Interpretation Limits

- The report supports research, not live trading or execution.
- BOT interbank and bank-average series are distinct and must not be compared as equivalent quotes.
- The current data include only USD/THB interbank, USD/THB bank average and EUR/THB bank average FX series. NEER and REER are not loaded.
- FRED observation dates alone do not establish when a value was publicly released. No release-aware backtest or causal macro claim is made.
- A successful warehouse build does not establish real-time source freshness or Power BI refresh time.
