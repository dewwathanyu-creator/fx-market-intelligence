# Power BI visual system

This is the working style for the six-page FX Market Intelligence Desktop report. It preserves the user's navy and blue direction and prioritizes fast interpretation over decorative detail. The editable source is `dashboard/powerbi/build_report.py`; regenerated PBIR files and the report theme travel with it.

## Visual hierarchy

1. The page title and subtitle state the business question, pair, rate type and unit.
2. Date/source/pair slicers occupy a consistent row below the title.
3. Four KPI cards show the key facts. A short teal rule marks each card without becoming another data series.
4. Charts occupy the main width; a narrow context panel explains baseline, method, missing series or coverage. The hand-authored chart title replaces Power BI's duplicate auto title.
5. Every page ends with source, observation date and warehouse build timestamp. That timestamp is not a Power BI service refresh time.

## Tokens and reading checks

| Role | Value | Use |
| --- | --- | --- |
| Sidebar | `#102E3D` | Navigation anchor |
| Canvas | `#F3F7F8` | Quiet background |
| Text | `#192B3C` | Titles and primary values |
| Secondary text | `#526979` | Context on white |
| Teal | `#0C6472` | Small accents and status text |
| Primary line | `#1670D5` | First chart series |
| Comparison line | `#B85B00` | Second chart series; distinct from primary blue |

Segoe UI is the default. Page titles use 31 px in the 1440 × 900 PBIR canvas, subtitle 16 px, navigation 15 px, authored chart titles 19 px, card labels 14 px and footer labels 12 px. Inspect the report at the user's normal Desktop zoom; these source-pixel sizes do not guarantee the rendered result. Keep chart axes and table labels readable, avoid clipped cells, and use text to identify series and quote direction. Microsoft's [Power BI accessibility guidance](https://learn.microsoft.com/en-us/power-bi/create-reports/desktop-accessibility-creating-reports) calls for consistent titles, legible labels and adequate contrast.

## FX interpretation guardrails

- USD/THB is THB per USD. A higher value means THB depreciation; a quote drawdown is not investor P&L.
- Interbank reference and commercial-bank customer-average rates are separate series. USD and EUR comparisons use compatible bank-average rate types and aligned dates.
- Volatility windows count observed returns and annualize with √252; missing raw dates are not filled.
- FRED observation dates alone do not prove release availability. The Macro page is exploratory; NEER/REER remain pending.

## Review checklist

After rebuilding, confirm all six pages render with the correct source and unit, four KPIs, chart/context panel and footer. At Desktop zoom, check values and labels for clipping, two-series color distinction, chart plots, date/pair filters, tooltip, Ctrl+click navigation, right-click drillthrough and Back. `docs/DASHBOARD_QA.md` records the prior accepted behavior; new screenshots must reflect the newly generated version before they replace the QA evidence.
