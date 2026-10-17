"""Check that the project entry points resolve to reviewable local evidence."""

import re
from decimal import Decimal
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
PAGES = (
    "market-overview",
    "currency-explorer",
    "macro-drivers",
    "risk-volatility",
    "thailand-fx-monitor",
    "data-quality-research",
)


def test_project_local_links_and_reproduction_steps() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for markdown in (
        ROOT / "README.md",
        ROOT / "docs" / "CASE_STUDY.md",
        ROOT / "reports" / "PROJECT_SUMMARY.md",
    ):
        for link in re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", markdown.read_text(encoding="utf-8")):
            if "://" not in link:
                assert (markdown.parent / unquote(link)).exists(), (markdown, link)
    assert "pip install -e" in readme
    assert "pytest" in readme
    assert "FX Market Intelligence Dashboard.pbip" in readme
    assert "FRED_API_KEY" in readme and "BOT_API_KEY" in readme


def test_six_final_screenshots_are_real_pngs() -> None:
    for page in PAGES:
        path = ROOT / "dashboard" / "screenshots" / "final" / f"{page}.png"
        assert path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), page


def test_case_study_has_reproducible_source_and_caveat() -> None:
    text = (ROOT / "docs" / "CASE_STUDY.md").read_text(encoding="utf-8")
    for required in (
        "2026-01-05",
        "2026-09-30",
        "DAILY_REF_RATE",
        "DAILY_AVG_EXG_RATE:USD",
        "DAILY_AVG_EXG_RATE:EUR",
        "https://portal.api.bot.or.th/",
        "THB per USD",
        "trading signal",
    ):
        assert required in text

    for first, last, stated in (
        ("31.3880", "33.5480", "+6.88%"),
        ("31.4254", "33.5541", "+6.77%"),
        ("36.7153", "38.0210", "+3.56%"),
    ):
        assert f"| {first} | {last} | {stated} |" in text
        calculated = 100 * (Decimal(last) / Decimal(first) - 1)
        assert f"{calculated:+.2f}%" == stated
