"""Contract checks for the editable six-page Power BI report."""

import json
import re
from pathlib import Path

REPORT = Path("dashboard/powerbi/FX Market Intelligence Dashboard.Report/definition")
MODEL = Path("dashboard/powerbi/FX Market Intelligence Dashboard.SemanticModel/definition/tables")
EXPECTED_PAGES = [
    "Market Overview",
    "Currency Explorer",
    "Macro Drivers",
    "Risk & Volatility",
    "Thailand FX Monitor",
    "Data Quality & Research",
]


def _pages():
    metadata = json.loads((REPORT / "pages/pages.json").read_text(encoding="utf-8"))
    return [
        (
            page_id,
            json.loads((REPORT / "pages" / page_id / "page.json").read_text(encoding="utf-8")),
        )
        for page_id in metadata["pageOrder"]
    ]


def _visuals(page_id):
    return [
        json.loads(path.read_text(encoding="utf-8"))
        for path in (REPORT / "pages" / page_id / "visuals").glob("*/visual.json")
    ]


def test_six_page_report_has_real_data_views_and_navigation():
    pages = _pages()
    assert [page["displayName"] for _, page in pages] == EXPECTED_PAGES
    page_ids = {page_id for page_id, _ in pages}
    for page_id, page in pages:
        visuals = _visuals(page_id)
        assert visuals, page["displayName"]
        kinds = {visual["visual"]["visualType"] for visual in visuals}
        assert "slicer" in kinds, page["displayName"]
        assert "cardVisual" in kinds, page["displayName"]
        assert "lineChart" in kinds or "tableEx" in kinds, page["displayName"]
        destinations = {
            action["properties"]["navigationSection"]["expr"]["Literal"]["Value"].strip("'")
            for visual in visuals
            for action in visual["visual"].get("visualContainerObjects", {}).get("visualLink", [])
            if "navigationSection" in action["properties"]
        }
        assert destinations == page_ids - {page_id}, page["displayName"]


def test_each_page_exposes_source_observation_and_refresh():
    for page_id, page in _pages():
        payload = "\n".join(json.dumps(v, ensure_ascii=False) for v in _visuals(page_id))
        for field in ("source_id", "Observation Date", "Last Refresh"):
            assert field in payload, (page["displayName"], field)


def test_report_has_drillthrough_target_for_pair_context():
    pages = _pages()
    overview_id, _ = pages[0]
    target = next(page for _, page in pages if page["displayName"] == "Currency Explorer")
    assert target.get("pageBinding", {}).get("type") == "Drillthrough"
    assert target["pageBinding"].get("acceptsFilterContext") == "None"
    target_field = target["pageBinding"]["parameters"][0]["fieldExpr"]
    charts = [
        visual for visual in _visuals(overview_id) if visual["visual"]["visualType"] == "lineChart"
    ]
    assert any(
        projection["field"] == target_field
        for chart in charts
        for role in chart["visual"].get("query", {}).get("queryState", {}).values()
        for projection in role.get("projections", [])
    )
    target_id = next(
        page_id for page_id, page in pages if page["displayName"] == "Currency Explorer"
    )
    assert any(
        action["properties"]["type"]["expr"]["Literal"]["Value"] == "'Back'"
        for visual in _visuals(target_id)
        for action in visual["visual"].get("visualContainerObjects", {}).get("visualLink", [])
    )


def test_visual_fields_exist_in_semantic_model():
    members = {}
    for table_file in MODEL.glob("*.tmdl"):
        definition = table_file.read_text(encoding="utf-8")
        members[table_file.stem] = {
            match.group(1) or match.group(2)
            for match in re.finditer(
                r"^[\t ]*(?:column|measure)\s+(?:'([^']+)'|([\w]+))",
                definition,
                flags=re.MULTILINE,
            )
        }
    for page_id, page in _pages():
        for visual in _visuals(page_id):
            for role in visual["visual"].get("query", {}).get("queryState", {}).values():
                for projection in role.get("projections", []):
                    field = projection["field"]
                    reference = field.get("Measure") or field.get("Column")
                    table = reference["Expression"]["SourceRef"]["Entity"]
                    column = reference["Property"]
                    assert column in members[table], (page["displayName"], table, column)


def test_desktop_render_contract_for_shapes_and_navigation():
    for page_id, page in _pages():
        for visual in _visuals(page_id):
            kind = visual["visual"]["visualType"]
            objects = visual["visual"].get("objects", {})
            if kind == "shape":
                assert any(
                    entry.get("selector", {}).get("id") == "default"
                    and "fillColor" in entry["properties"]
                    for entry in objects["fill"]
                ), page["displayName"]
            if kind == "actionButton":
                assert any(
                    entry.get("selector", {}).get("id") == "default"
                    and "text" in entry["properties"]
                    for entry in objects["text"]
                ), page["displayName"]


def test_no_unlisted_pages_or_unfiltered_overview_ledger():
    pages = _pages()
    assert {folder.name for folder in (REPORT / "pages").iterdir() if folder.is_dir()} == {
        page_id for page_id, _ in pages
    }
    overview_id = pages[0][0]
    for visual in _visuals(overview_id):
        if visual["visual"]["visualType"] != "tableEx":
            continue
        query = visual["visual"].get("query", {}).get("queryState", {})
        fields = [
            projection["field"] for role in query.values() for projection in role["projections"]
        ]
        assert not any(field.get("Column", {}).get("Property") == "source_id" for field in fields)


def test_refresh_timestamp_uses_gregorian_parse_culture():
    definition = (MODEL / "tbl_refresh_metadata.tmdl").read_text(encoding="utf-8")
    assert '"en-US"' in definition


def test_macro_charts_have_enough_render_area():
    page_id = next(page_id for page_id, page in _pages() if page["displayName"] == "Macro Drivers")
    charts = [v for v in _visuals(page_id) if v["visual"]["visualType"] == "lineChart"]
    assert len(charts) == 2
    assert all(chart["position"]["height"] >= 250 for chart in charts)
    assert charts[0]["position"]["x"] != charts[1]["position"]["x"]


def test_risk_page_does_not_list_other_fx_sources():
    page_id = next(
        page_id for page_id, page in _pages() if page["displayName"] == "Risk & Volatility"
    )
    assert not any(v["visual"]["visualType"] == "tableEx" for v in _visuals(page_id))
