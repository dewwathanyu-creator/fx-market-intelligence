# Task 11 — Power BI report QA

## Report contract

The editable PBIP report is `dashboard/powerbi/FX Market Intelligence Dashboard.pbip`. `dashboard/powerbi/build_report.py` deterministically writes six PBIR page definitions from the existing semantic model. All cards, trends, tables and slicers bind to model fields; static sample numbers are not embedded in the PBIR visuals. The PNG/SVG files in `dashboard/mockups/` are illustrative design references only.

| Page | Business question | Expected check |
| --- | --- | --- |
| Market Overview | What happened to the BOT USD/THB interbank quote? | Latest THB per USD quote, observed return, 20-observation volatility, date and same-series history. Rising THB per USD denotes THB depreciation. |
| Currency Explorer | How do the comparable bank-average USD and EUR quotes move? | Separate quotes, indexed trends, shared rate type and aligned observation dates. The pair is available as a drillthrough target. |
| Macro Drivers | How do FX and selected macro observations move over time? | FRED selector, separate charts with separate units, observation dates, source and frequency. Treat association as descriptive. |
| Risk & Volatility | How have quote volatility and drawdown evolved? | 20- and 60-observation realized volatility, latest quote drawdown, method and coverage. Volatility uses the 252-observation annualization convention. |
| Thailand FX Monitor | What do BOT bilateral bank-average quotes show? | USD/THB and EUR/THB rate cards and indexed trends. NEER/REER panels explicitly say pending. |
| Data Quality & Research | What data were imported, and when? | Warehouse row counts, latest FX/macro observation dates, daily FX coverage and source ledger. Warehouse build time is distinct from Power BI refresh time. |

Every page contains page navigation, date and source context, a current observation date and a `Last Refresh` semantic-model card. The visual source ledger retains source ID, pair, rate type, observation date and, where available, retrieval timestamp. Dates on the same visual are model-filtered; missing observations are not silently forward-filled.

## Automated checks

- `python -m pytest -q tests/integration/test_powerbi_report.py`: 9 passed. Checks page inventory, navigation targets, data views, freshness labels, drillthrough binding, visual field references, Desktop rendering contracts, no extra page, explicit Gregorian timestamp parsing, sufficient Macro chart size and interbank-only Risk context.
- `python -m pytest -q --basetemp=.pytest_task11_sixpage`: 60 passed. The explicit temporary directory is necessary because this execution sandbox cannot create pytest's default temp directory.
- `python -m ruff check .`: passed.
- `python -m ruff format --check .`: passed.
- `git diff --check`: passed.

## Desktop visual QA

The user opened the PBIP in Power BI Desktop and supplied `dashboard/screenshots/task11-market-overview-before.png` on 17 October 2026. It confirms the report loaded and the Overview cards and chart queried real model data. It also revealed five defects:

1. The page and sidebar shapes rendered in theme blue because their fill colors lacked a `default` state selector. The report generator now sets explicit selected fill entries for shapes.
2. Navigation buttons showed no labels because Power BI expects separate unselected `show` and `default`-selected text entries. The generator now uses the documented two-entry pattern, including fill, shape and icon placement.
3. An obsolete `Page 1` directory remained in the report even though `pages.json` listed six pages. The empty tracked page was removed.
4. The Overview ledger showed EUR/THB bank-average rows alongside an interbank title. It was replaced with cards calculated from the fixed USD/THB interbank series and selected period.
5. `Last Refresh` displayed year 1483 although the warehouse workbook contains a 2026 timestamp. Locale-dependent parsing of the workbook's text timestamp is the likely cause; the Power Query type conversion now explicitly uses `en-US` for Gregorian parsing. The corrected value still needs a Desktop refresh check.

The user applied external changes and supplied `dashboard/screenshots/task11-market-overview-after-first-fix.png`. It confirms the page color, navigation text, six-page count, interbank-only context cards and 2026 warehouse date now render correctly. Two small clipping issues remained: the First quote card value and the last sidebar label. The generator now gives the quote more width and shortens the last sidebar label; redundant card labels in the footer are hidden. These latest adjustments still need a Desktop render check.

The user then supplied all six page screenshots (`dashboard/screenshots/task11-review-01-market-overview.png` through `task11-review-06-data-quality-research.png`). They confirm six pages load, the bank-average comparisons render, the Thailand pending-series note is explicit, and the quality cards show 543 FX rows and 603 macro rows. The screenshots revealed three remaining issues: Overview period move value is clipped; both Macro line charts have no plot at their short height; Risk's raw table starts with EUR/THB bank-average rows under an interbank heading. The current report generator uses full-width compact cards for the Overview period context, two full-height Macro charts with selected-series metadata cards, and an interbank-specific Risk method panel. The Currency Explorer table is relabeled as underlying observations rather than an aligned comparison table.

The final three screenshots (`dashboard/screenshots/task11-final-01-market-overview.png`, `task11-final-03-macro-drivers.png`, and `task11-final-04-risk-volatility.png`) confirm those corrections in Power BI Desktop. The Overview period move is visible as +6.9%; both Macro charts show observed lines with DTWEXBGS series, index unit and daily frequency; and the Risk panel shows BOT USD/THB interbank, the sample log-return volatility method and 181 observed FX dates. All six pages were visually inspected; the three pages with substantive fixes were rechecked afterward.

The current computer-control inventory does not expose native app windows. The user checked the Overview date slicer (the view changed), line tooltip (Overview Rate appeared), and left navigation (Ctrl+click reached Currency Explorer); all three passed. The drillthrough check exposed a source-field gap: the Overview trend did not project the pair field used by Currency Explorer's drillthrough target. The Overview chart now includes `tbl_dim_fx_pair[pair_id]` as its Series field, so each plotted USD/THB point carries the target field. The user then right-clicked the line and successfully reached Currency Explorer; `dashboard/screenshots/task11-drillthrough-before-filter-fix.png` shows the pair filter `USD/THB` applied. It also shows that the chart point's date filter was carried over, leaving one point and blank EUR cards. The target page binding now sets `acceptsFilterContext` to `None` so only the explicit pair drillthrough field is carried, and a Back button is present. `dashboard/screenshots/task11-drillthrough-final.png` confirms the target now shows a full USD/THB indexed trend, the `pair_id is USD/THB` filter and the Back button. EUR values are intentionally blank in this USD/THB drillthrough context. The user then Ctrl+clicked Back to source and returned to Market Overview. All four requested interaction checks passed.

The Desktop screenshots remain local, uncommitted QA evidence because Power BI's window chrome displays the user's account name. The committed report and this log record the checks without publishing that personal detail.

## Interpretation limits

- The report is for research, not live trading or execution.
- BOT interbank and bank-average series are distinct and must not be compared as equivalent quotes.
- The current data include only USD/THB interbank, USD/THB bank average and EUR/THB bank average FX series; NEER/REER are not loaded.
- FRED observation dates alone do not establish when a value was publicly released. No release-aware backtest or causal macro claim is made.
- A successful warehouse build does not establish real-time source freshness or Power BI refresh time.
