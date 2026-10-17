"""Guard report readability and information hierarchy across all six pages."""

import json
from pathlib import Path

ROOT = Path("dashboard/powerbi/FX Market Intelligence Dashboard.Report")
PAGES = ROOT / "definition" / "pages"
THEME = ROOT / "StaticResources/SharedResources/BaseThemes/Fluent2-CY26SU09.json"


def _visuals():
    for path in PAGES.glob("*/visuals/*/visual.json"):
        yield json.loads(path.read_text(encoding="utf-8"))


def _text(visual):
    paragraphs = (
        visual["visual"]
        .get("objects", {})
        .get("general", [{}])[0]
        .get("properties", {})
        .get("paragraphs", [])
    )
    return " ".join(run["value"] for p in paragraphs for run in p["textRuns"])


def test_charts_have_one_authored_title_without_auto_title() -> None:
    charts = [v for v in _visuals() if v["visual"]["visualType"] == "lineChart"]
    assert len(charts) >= 6
    for chart in charts:
        title = chart["visual"]["visualContainerObjects"]["title"]
        assert title[0]["properties"]["show"]["expr"]["Literal"]["Value"] == "false"


def test_sidebar_labels_and_captions_remain_readable() -> None:
    visuals = list(_visuals())
    nav = [v for v in visuals if v["visual"]["visualType"] == "actionButton"]
    assert all(
        v["visual"]["objects"]["text"][1]["properties"]["fontSize"]["expr"]["Literal"]["Value"]
        == "15D"
        for v in nav
    )
    nav_text = " ".join(
        v["visual"]["objects"]["text"][1]["properties"]["text"]["expr"]["Literal"]["Value"]
        for v in nav
    )
    for label in ("Currencies", "Thailand FX", "Data Quality"):
        assert label in nav_text
    page_notes = [v for v in visuals if "RESEARCH" in _text(v)]
    assert page_notes
    assert all(
        int(
            v["visual"]["objects"]["general"][0]["properties"]["paragraphs"][0]["textRuns"][0][
                "textStyle"
            ]["fontSize"].removesuffix("px")
        )
        >= 12
        for v in page_notes
    )


def test_comparison_palette_and_tables_support_fast_reading() -> None:
    theme = json.loads(THEME.read_text(encoding="utf-8"))
    assert theme["dataColors"][:2] == ["#1670D5", "#B85B00"]
    assert theme["textClasses"]["label"]["fontSize"] >= 12
    tables = [v for v in _visuals() if v["visual"]["visualType"] == "tableEx"]
    assert len(tables) == 2
    assert all(
        len(v["visual"]["query"]["queryState"]["Values"]["projections"]) <= 3 for v in tables
    )
    assert any(
        projection["field"].get("Column", {}).get("Property") == "rate_type"
        for table in tables
        for projection in table["visual"]["query"]["queryState"]["Values"]["projections"]
    )
