"""Build the editable six-page PBIR report from the existing semantic model.

The report contains only visual definitions. All displayed observations and
metrics are queried from the imported semantic model at viewing time.
"""

# ruff: noqa: E501

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "FX Market Intelligence Dashboard.Report" / "definition"
PAGES = ROOT / "pages"
VISUAL_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/"
    "visualContainer/2.9.0/schema.json"
)
PAGE_SCHEMA = (
    "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/"
    "2.1.0/schema.json"
)
INK = "#192b3c"
MUTED = "#526979"
TEAL = "#0c6472"
NAVY = "#102e3d"
WHITE = "#ffffff"
BG = "#f3f7f8"
PAGE_SPECS = [
    ("Market Overview", "▦", "BOT USD/THB interbank · THB per USD"),
    ("Currency Explorer", "◉", "BOT bank averages · aligned USD and EUR quotes"),
    ("Macro Drivers", "▥", "BOT FX + FRED macro · exploratory association"),
    ("Risk & Volatility", "◇", "USD/THB interbank · observed return intervals"),
    ("Thailand FX Monitor", "⌖", "BOT bank averages · NEER/REER pending"),
    ("Data Quality & Research", "☑", "Current BOT + FRED source and coverage ledger"),
]


def _id(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:20]


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _literal(value: str | bool | int) -> dict:
    if isinstance(value, bool):
        encoded = "true" if value else "false"
    elif isinstance(value, int):
        encoded = f"{value}D"
    else:
        encoded = "'" + value.replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": encoded}}}


def _color(value: str) -> dict:
    return {"solid": {"color": _literal(value)}}


def _vco_background(color: str = WHITE) -> dict:
    return {
        "background": [{"properties": {"show": _literal(True), "color": _color(color)}}],
        "border": [{"properties": {"show": _literal(False)}}],
        "title": [{"properties": {"show": _literal(False)}}],
        "padding": [
            {"properties": {side: _literal(0) for side in ("top", "bottom", "left", "right")}}
        ],
    }


class Page:
    def __init__(self, title: str, index: int) -> None:
        self.title = title
        self.index = index
        self.name = _id("page:" + title)
        self.visuals: list[dict] = []

    def add(self, key: str, kind: str, x: int, y: int, width: int, height: int, **extra) -> str:
        name = _id(self.name + ":" + key)
        visual = {"visualType": kind, **extra}
        self.visuals.append(
            {
                "$schema": VISUAL_SCHEMA,
                "name": name,
                "position": {
                    "x": x,
                    "y": y,
                    "z": 1000 + len(self.visuals),
                    "height": height,
                    "width": width,
                    "tabOrder": 1000 + len(self.visuals),
                },
                "visual": visual,
            }
        )
        return name

    def shape(self, key: str, x: int, y: int, width: int, height: int, color: str) -> None:
        self.add(
            key,
            "shape",
            x,
            y,
            width,
            height,
            objects={
                "shape": [{"properties": {"tileShape": _literal("rectangle")}}],
                "fill": [
                    {"properties": {"show": _literal(True)}},
                    {
                        "properties": {"fillColor": _color(color)},
                        "selector": {"id": "default"},
                    },
                ],
                "outline": [{"properties": {"show": _literal(False)}}],
            },
            visualContainerObjects={
                "background": [{"properties": {"show": _literal(False)}}],
                "border": [{"properties": {"show": _literal(False)}}],
            },
        )

    def text(
        self,
        key: str,
        value: str,
        x: int,
        y: int,
        width: int,
        height: int,
        *,
        size: int = 15,
        color: str = INK,
        bold: bool = False,
    ) -> None:
        style = {"fontFamily": "Segoe UI", "fontSize": f"{size}px", "color": color}
        if bold:
            style["fontWeight"] = "bold"
        self.add(
            key,
            "textbox",
            x,
            y,
            width,
            height,
            objects={
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [{"value": value, "textStyle": style}],
                                    "horizontalTextAlignment": "left",
                                }
                            ]
                        }
                    }
                ]
            },
            visualContainerObjects={
                "background": [{"properties": {"show": _literal(False)}}],
                "border": [{"properties": {"show": _literal(False)}}],
                "padding": [
                    {
                        "properties": {
                            side: _literal(0) for side in ("top", "bottom", "left", "right")
                        }
                    }
                ],
            },
        )

    def nav(
        self,
        destination: str,
        icon: str,
        label: str,
        y: int,
        active: bool,
        action: str = "PageNavigation",
    ) -> None:
        extra = (
            {}
            if active
            else {
                "visualLink": [
                    {
                        "properties": {
                            "show": _literal(True),
                            "type": _literal(action),
                            **(
                                {"navigationSection": _literal(destination)}
                                if action == "PageNavigation"
                                else {}
                            ),
                        }
                    }
                ]
            }
        )
        self.add(
            "nav:" + destination,
            "actionButton",
            16,
            y,
            202,
            39,
            objects={
                "shape": [
                    {"properties": {"tileShape": _literal("rectangleRounded")}},
                    {
                        "properties": {"tileShape": _literal("rectangleRounded")},
                        "selector": {"id": "default"},
                    },
                ],
                "fill": [
                    {"properties": {"show": _literal(True)}},
                    {
                        "properties": {
                            "fillColor": _color("#215768" if active else NAVY),
                        },
                        "selector": {"id": "default"},
                    },
                ],
                "outline": [{"properties": {"show": _literal(False)}}],
                "text": [
                    {"properties": {"show": _literal(True)}},
                    {
                        "properties": {
                            "text": _literal(f"{icon}  {label}"),
                            "fontColor": _color(WHITE if active else "#b4d0d9"),
                            "fontSize": _literal(15),
                            "horizontalAlignment": _literal("left"),
                        },
                        "selector": {"id": "default"},
                    },
                ],
                "icon": [
                    {"properties": {"show": _literal(False)}},
                    {
                        "properties": {"placement": _literal("left")},
                        "selector": {"id": "default"},
                    },
                ],
            },
            visualContainerObjects={
                **extra,
                "background": [{"properties": {"show": _literal(False)}}],
                "border": [{"properties": {"show": _literal(False)}}],
            },
        )

    def slicer(
        self,
        key: str,
        table: str,
        column: str,
        label: str,
        x: int,
        width: int,
        *,
        mode: str = "Dropdown",
    ) -> None:
        self.add(
            key,
            "slicer",
            x,
            94,
            width,
            80,
            query={"queryState": {"Values": {"projections": [_projection(table, column)]}}},
            objects={
                "data": [{"properties": {"mode": _literal(mode)}}],
                "header": [{"properties": {"show": _literal(True), "text": _literal(label)}}],
            },
            visualContainerObjects={
                "background": [{"properties": {"show": _literal(True), "color": _color(WHITE)}}],
                "border": [{"properties": {"show": _literal(False)}}],
                "padding": [
                    {
                        "properties": {
                            side: _literal(8) for side in ("top", "bottom", "left", "right")
                        }
                    }
                ],
            },
        )

    def card(
        self,
        key: str,
        label: str,
        measure: str,
        x: int,
        width: int,
        *,
        y: int = 187,
        compact: bool = False,
    ) -> None:
        self.shape(key + ":bg", x, y, width, 84 if compact else 127, WHITE)
        self.shape(key + ":accent", x + 18, y, 54, 4, TEAL)
        self.text(
            key + ":label",
            label.upper(),
            x + 18,
            y + (10 if compact else 15),
            width - 36,
            25,
            size=14,
            color=MUTED,
        )
        self.add(
            key,
            "cardVisual",
            x + 16,
            y + (32 if compact else 44),
            width - 32,
            42 if compact else 67,
            query={
                "queryState": {
                    "Data": {"projections": [_projection("tbl_fact_fx_rates", measure, True)]}
                }
            },
            objects={
                "outline": [
                    {"properties": {"show": _literal(False)}, "selector": {"id": "default"}}
                ],
                "label": [{"properties": {"show": _literal(False)}, "selector": {"id": "default"}}],
            },
            visualContainerObjects={
                "background": [{"properties": {"show": _literal(False)}}],
                "border": [{"properties": {"show": _literal(False)}}],
                "padding": [
                    {
                        "properties": {
                            side: _literal(0) for side in ("top", "bottom", "left", "right")
                        }
                    }
                ],
            },
        )

    def chart(
        self,
        key: str,
        title: str,
        measure_names: list[str],
        x: int = 266,
        y: int = 334,
        width: int = 755,
        height: int = 364,
        series: tuple[str, str] | None = None,
    ) -> None:
        self.shape(key + ":bg", x, y, width, height, WHITE)
        self.text(key + ":title", title, x + 20, y + 14, width - 40, 32, size=19, bold=True)
        query_state = {
            "Category": {"projections": [_projection("tbl_dim_date", "date_key")]},
            "Y": {
                "projections": [
                    _projection("tbl_fact_fx_rates", measure, True) for measure in measure_names
                ]
            },
        }
        if series is not None:
            query_state["Series"] = {"projections": [_projection(*series)]}
        self.add(
            key,
            "lineChart",
            x + 17,
            y + 51,
            width - 34,
            height - 67,
            query={"queryState": query_state},
            visualContainerObjects=_vco_background(),
        )

    def table(
        self,
        key: str,
        title: str,
        fields: list[tuple[str, str]],
        x: int = 1038,
        y: int = 334,
        width: int = 366,
        height: int = 364,
    ) -> None:
        self.shape(key + ":bg", x, y, width, height, WHITE)
        self.text(key + ":title", title, x + 18, y + 14, width - 36, 31, size=19, bold=True)
        self.add(
            key,
            "tableEx",
            x + 15,
            y + 50,
            width - 30,
            height - 66,
            query={
                "queryState": {
                    "Values": {"projections": [_projection(table, col) for table, col in fields]}
                }
            },
            visualContainerObjects=_vco_background(),
        )

    def save(self) -> None:
        page = {
            "$schema": PAGE_SCHEMA,
            "name": self.name,
            "displayName": self.title,
            "displayOption": "FitToPage",
            "height": 900,
            "width": 1440,
        }
        if self.title == "Currency Explorer":
            drill_filter = "Filter" + _id("drill:" + self.name) + "abcd"
            field = _field("tbl_dim_fx_pair", "pair_id")
            page["filterConfig"] = {
                "filters": [
                    {
                        "name": drill_filter,
                        "field": field,
                        "type": "Categorical",
                        "howCreated": "Drillthrough",
                    }
                ]
            }
            page["pageBinding"] = {
                "name": "Pod",
                "type": "Drillthrough",
                "acceptsFilterContext": "None",
                "parameters": [
                    {
                        "name": "Param_" + drill_filter,
                        "boundFilter": drill_filter,
                        "fieldExpr": field,
                    }
                ],
            }
        _write(PAGES / self.name / "page.json", page)
        for visual in self.visuals:
            _write(PAGES / self.name / "visuals" / visual["name"] / "visual.json", visual)


def _field(table: str, column: str, measure: bool = False) -> dict:
    kind = "Measure" if measure else "Column"
    return {kind: {"Expression": {"SourceRef": {"Entity": table}}, "Property": column}}


def _projection(table: str, column: str, measure: bool = False) -> dict:
    return {
        "field": _field(table, column, measure),
        "queryRef": f"{table}.{column}",
        "nativeQueryRef": column,
    }


def _base(title: str, index: int) -> Page:
    page = Page(title, index)
    page.shape("canvas", 0, 0, 1440, 900, BG)
    page.shape("sidebar", 0, 0, 232, 900, NAVY)
    page.text("brand", "◆  FX INTELLIGENCE", 22, 25, 195, 42, size=19, color=WHITE, bold=True)
    page.text("menu-label", "DASHBOARD", 25, 91, 170, 24, size=13, color="#c0dbe2")
    short_nav = {
        "Currency Explorer": "Currencies",
        "Thailand FX Monitor": "Thailand FX",
        "Data Quality & Research": "Data Quality",
    }
    for nav_index, (nav_title, icon, _) in enumerate(PAGE_SPECS):
        nav_label = short_nav.get(nav_title, nav_title)
        page.nav(
            _id("page:" + nav_title), icon, nav_label, 123 + nav_index * 44, index == nav_index
        )
        if index == nav_index:
            page.shape("active-nav-marker", 16, 123 + nav_index * 44, 4, 39, "#39bdc4")
    page.text("rail-note", "RESEARCH · NOT TRADING", 24, 412, 196, 30, size=12, color="#c0dbe2")
    page.text("title", title, 266, 23, 760, 50, size=31, bold=True)
    page.text("subtitle", PAGE_SPECS[index][2], 267, 65, 850, 29, size=16, color=MUTED)
    page.text(
        "scope-badge", "OFFICIAL DATA · LOCAL REFRESH", 1135, 30, 280, 30, size=12, color=TEAL
    )
    page.shape("header-rule", 266, 87, 1138, 2, "#dce8eb")
    page.shape("footer-bg", 266, 718, 1138, 141, WHITE)
    page.shape("footer-rule", 266, 718, 1138, 2, "#dce8eb")
    page.text(
        "footer-title", "SOURCE  ·  OBSERVATION  ·  REFRESH", 288, 738, 530, 28, size=15, bold=True
    )
    page.text(
        "footer-note",
        "Observation date and warehouse refresh are different. This report is research, not a trade quote.",
        288,
        823,
        1080,
        27,
        size=13,
        color=MUTED,
    )
    page.text(
        "bottom-line",
        "FX Market Intelligence Dashboard · BOT + FRED · quote direction is explicit",
        266,
        875,
        1000,
        20,
        size=12,
        color=MUTED,
    )
    return page


def _footer(page: Page, source_label: str, observation_measure: str) -> None:
    page.text("footer-source", source_label, 288, 775, 530, 32, size=14, color=INK)
    page.text(
        "footer-observation-label", "OBSERVED THROUGH", 850, 742, 235, 22, size=12, color=MUTED
    )
    page.text("footer-refresh-label", "WAREHOUSE BUILT", 1110, 742, 270, 22, size=12, color=MUTED)
    page.add(
        "footer-observation",
        "cardVisual",
        850,
        768,
        235,
        49,
        query={
            "queryState": {
                "Data": {
                    "projections": [_projection("tbl_fact_fx_rates", observation_measure, True)]
                }
            }
        },
        objects={
            "label": [{"properties": {"show": _literal(False)}, "selector": {"id": "default"}}]
        },
        visualContainerObjects={
            "background": [{"properties": {"show": _literal(False)}}],
            "border": [{"properties": {"show": _literal(False)}}],
        },
    )
    page.add(
        "footer-refresh",
        "cardVisual",
        1110,
        768,
        270,
        49,
        query={
            "queryState": {
                "Data": {"projections": [_projection("tbl_fact_fx_rates", "Last Refresh", True)]}
            }
        },
        objects={
            "label": [{"properties": {"show": _literal(False)}, "selector": {"id": "default"}}]
        },
        visualContainerObjects={
            "background": [{"properties": {"show": _literal(False)}}],
            "border": [{"properties": {"show": _literal(False)}}],
        },
    )


def build() -> None:
    pages: list[Page] = []

    page = _base("Market Overview", 0)
    page.slicer("date", "tbl_dim_date", "date_key", "Date range", 266, 280, mode="Between")
    page.slicer("source", "tbl_fact_fx_rates", "source_id", "FX source", 564, 230)
    page.slicer("pair", "tbl_dim_fx_pair", "pair_id", "Currency pair", 812, 225)
    page.slicer("rate-type", "tbl_fact_fx_rates", "rate_type", "Rate type", 1055, 225)
    for i, (label, measure) in enumerate(
        [
            ("USD/THB latest", "Overview Rate"),
            ("Move vs prior obs.", "Overview Return"),
            ("20-obs. volatility", "Overview Volatility"),
            ("Latest observation", "Overview Observation Date"),
        ]
    ):
        page.card(f"kpi:{i}", label, measure, 266 + i * 282, 265)
    page.chart(
        "trend",
        "USD/THB interbank trend · THB per USD",
        ["Overview Rate"],
        series=("tbl_dim_fx_pair", "pair_id"),
    )
    page.shape("context-panel", 1038, 334, 366, 364, WHITE)
    page.text("context-title", "Selected interbank period", 1056, 349, 330, 30, size=18, bold=True)
    page.card(
        "context-start-date",
        "First observation",
        "Overview Start Date",
        1055,
        333,
        y=386,
        compact=True,
    )
    page.card(
        "context-start-rate", "First quote", "Overview Start Rate", 1055, 333, y=486, compact=True
    )
    page.card("context-move", "Period move", "Overview Period Move", 1055, 333, y=586, compact=True)
    _footer(page, "BOT · USD/THB interbank · THB per USD", "Overview Observation Date")
    pages.append(page)

    page = _base("Currency Explorer", 1)
    page.nav("drillthrough-back", "←", "Back to source", 603, False, action="Back")
    page.slicer("date", "tbl_dim_date", "date_key", "Date range", 266, 280, mode="Between")
    page.slicer("source", "tbl_fact_fx_rates", "source_id", "Bank-average source", 564, 246)
    page.slicer("pair", "tbl_dim_fx_pair", "pair_id", "Pair / drillthrough", 828, 230)
    page.slicer("rate-type", "tbl_fact_fx_rates", "rate_type", "Rate type", 1076, 215)
    for i, (label, measure) in enumerate(
        [
            ("USD/THB bank avg.", "Bank USD Latest"),
            ("EUR/THB bank avg.", "Bank EUR Latest"),
            ("USD period move", "Bank USD Period Move"),
            ("EUR period move", "Bank EUR Period Move"),
        ]
    ):
        page.card(f"kpi:{i}", label, measure, 266 + i * 282, 265)
    page.chart(
        "trend",
        "Indexed bank-average performance · shared 2026 baseline",
        ["Bank USD Indexed", "Bank EUR Indexed"],
    )
    page.table(
        "comparison",
        "Selected BOT quote observations",
        [
            ("tbl_fact_fx_rates", "pair_id"),
            ("tbl_fact_fx_rates", "observation_date"),
            ("tbl_fact_fx_rates", "rate"),
        ],
    )
    _footer(page, "BOT · USD/EUR bank averages · THB per unit", "Latest FX Observation Date")
    pages.append(page)

    page = _base("Macro Drivers", 2)
    page.slicer("date", "tbl_dim_date", "date_key", "Date range", 266, 280, mode="Between")
    page.slicer("indicator", "tbl_dim_indicator", "indicator_id", "FRED indicator", 564, 280)
    page.slicer("source", "tbl_fact_fx_rates", "source_id", "FX reference", 862, 255)
    for i, (label, measure) in enumerate(
        [
            ("USD/THB interbank", "Overview Rate"),
            ("Selected macro value", "Selected Macro Latest"),
            ("Macro observation", "Selected Macro Observation Date"),
            ("FX observation", "Overview Observation Date"),
        ]
    ):
        page.card(f"kpi:{i}", label, measure, 266 + i * 282, 265)
    page.chart("fx-trend", "USD/THB · THB per USD", ["Overview Rate"], width=365)
    page.chart(
        "macro-trend",
        "FRED indicator · own unit",
        ["Selected Macro Value"],
        x=656,
        width=365,
    )
    page.shape("macro-context", 1038, 334, 366, 364, WHITE)
    page.text("macro-context-title", "Selected FRED series", 1056, 349, 330, 30, size=18, bold=True)
    page.card("macro-series", "Series ID", "Selected Macro Series", 1055, 333, y=386, compact=True)
    page.card("macro-unit", "Unit", "Selected Macro Unit", 1055, 333, y=486, compact=True)
    page.card(
        "macro-frequency", "Frequency", "Selected Macro Frequency", 1055, 333, y=586, compact=True
    )
    _footer(page, "BOT FX + FRED macro · release date absent", "Selected Macro Observation Date")
    pages.append(page)

    page = _base("Risk & Volatility", 3)
    page.slicer("date", "tbl_dim_date", "date_key", "Date range", 266, 280, mode="Between")
    page.slicer("source", "tbl_fact_fx_rates", "source_id", "FX source", 564, 235)
    page.slicer("pair", "tbl_dim_fx_pair", "pair_id", "Currency pair", 817, 230)
    for i, (label, measure) in enumerate(
        [
            ("20-obs. volatility", "Overview Volatility"),
            ("60-obs. volatility", "Overview 60 Volatility"),
            ("Quote drawdown", "Overview Drawdown"),
            ("Latest observation", "Overview Observation Date"),
        ]
    ):
        page.card(f"kpi:{i}", label, measure, 266 + i * 282, 265)
    page.chart(
        "volatility",
        "Annualized realized volatility · 20 / 60 observed returns",
        ["Overview Volatility Trend", "Overview 60 Volatility Trend"],
    )
    page.shape("risk-method", 1038, 334, 366, 364, WHITE)
    page.text("risk-method-title", "Method and coverage", 1056, 349, 330, 30, size=18, bold=True)
    page.text("risk-source", "BOT USD/THB interbank · THB per USD", 1056, 402, 330, 35, size=14)
    page.text("risk-method-note", "Sample SD of log returns × √252", 1056, 463, 330, 35, size=14)
    page.card(
        "risk-coverage",
        "Observed FX dates",
        "Overview Metric Row Count",
        1055,
        333,
        y=533,
        compact=True,
    )
    page.text(
        "risk-limitation",
        "Quote drawdown is not investor P&L; exposure direction matters.",
        1056,
        635,
        330,
        48,
        size=12,
        color=MUTED,
    )
    _footer(page, "BOT · USD/THB interbank · √252 convention", "Overview Observation Date")
    pages.append(page)

    page = _base("Thailand FX Monitor", 4)
    page.slicer("date", "tbl_dim_date", "date_key", "Date range", 266, 280, mode="Between")
    page.slicer("source", "tbl_fact_fx_rates", "source_id", "Bank-average source", 564, 246)
    page.slicer("pair", "tbl_dim_fx_pair", "pair_id", "Pair", 828, 225)
    for i, (label, measure) in enumerate(
        [
            ("USD/THB bank avg.", "Bank USD Latest"),
            ("EUR/THB bank avg.", "Bank EUR Latest"),
            ("USD period move", "Bank USD Period Move"),
            ("EUR period move", "Bank EUR Period Move"),
        ]
    ):
        page.card(f"kpi:{i}", label, measure, 266 + i * 282, 265)
    page.chart(
        "thb-trend",
        "Indexed THB bilateral quotes · same rate type",
        ["Bank USD Indexed", "Bank EUR Indexed"],
    )
    page.shape("pending-panel", 1038, 334, 366, 364, WHITE)
    page.text("pending-title", "Effective FX indices", 1058, 350, 315, 32, size=18, bold=True)
    page.text("neer", "NEER · pending official series", 1058, 426, 320, 32, size=16, color=MUTED)
    page.text("reer", "REER · pending official series", 1058, 506, 320, 32, size=16, color=MUTED)
    page.text(
        "pending-note",
        "Do not infer broad THB strength from two bilateral quotes.",
        1058,
        601,
        320,
        56,
        size=13,
        color=MUTED,
    )
    _footer(page, "BOT · bank average · NEER/REER pending", "Latest FX Observation Date")
    pages.append(page)

    page = _base("Data Quality & Research", 5)
    page.slicer("date", "tbl_dim_date", "date_key", "Date range", 266, 280, mode="Between")
    page.slicer("source", "tbl_fact_fx_rates", "source_id", "FX source", 564, 246)
    page.slicer("indicator", "tbl_dim_indicator", "indicator_id", "Macro series", 828, 246)
    for i, (label, measure) in enumerate(
        [
            ("Warehouse FX rows", "FX Row Count"),
            ("Warehouse macro rows", "Macro Row Count"),
            ("Latest FX obs.", "Latest FX Observation Date"),
            ("Latest macro obs.", "Latest Macro Observation Date"),
        ]
    ):
        page.card(f"kpi:{i}", label, measure, 266 + i * 282, 265)
    page.chart("coverage", "FX observations by observation date", ["Daily FX Observation Count"])
    page.table(
        "quality-table",
        "Source coverage · observed dates",
        [
            ("tbl_fact_fx_rates", "source_id"),
            ("tbl_fact_fx_rates", "rate_type"),
            ("tbl_fact_fx_rates", "observation_date"),
        ],
    )
    _footer(page, "BOT · 3 FX series / FRED · 5 macro series", "Latest FX Observation Date")
    pages.append(page)

    for page in pages:
        page.save()
    pages_json = json.loads((PAGES / "pages.json").read_text(encoding="utf-8"))
    pages_json["pageOrder"] = [page.name for page in pages]
    pages_json["activePageName"] = pages[0].name
    _write(PAGES / "pages.json", pages_json)


if __name__ == "__main__":
    build()
