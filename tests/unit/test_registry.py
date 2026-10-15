from pathlib import Path

import pytest

from fx_intelligence.registry import RegistryError, load_registry


def test_registry_contains_mvp_sources() -> None:
    path = Path(__file__).parents[2] / "config" / "sources" / "registry.yaml"
    series = load_registry(path)
    assert {item["provider"] for item in series} >= {"BOT", "FRED"}
    assert any(item["id"] == "bot_usdthb_interbank" for item in series)
    required = {
        "access",
        "coverage_start_target",
        "coverage_verified",
        "missing_policy",
        "revision_policy",
        "docs",
    }
    assert all(required <= item.keys() for item in series)


def test_registry_rejects_duplicate_ids(tmp_path: Path) -> None:
    path = tmp_path / "registry.yaml"
    path.write_text(
        "series:\n"
        "  - id: x\n    provider: BOT\n    series_id: DAILY_REF_RATE\n"
        "    url: https://example.com\n    unit: THB per USD\n"
        "    frequency: daily\n    priority: P0\n    rate_type: interbank\n"
        "    base_ccy: USD\n    quote_ccy: THB\n"
        "  - id: x\n    provider: FRED\n    series_id: FEDFUNDS\n"
        "    url: https://example.com\n    unit: percent\n"
        "    frequency: monthly\n    priority: P0\n    rate_type: macro\n",
        encoding="utf-8",
    )
    with pytest.raises(RegistryError, match="duplicate"):
        load_registry(path)


def test_registry_requires_quote_direction(tmp_path: Path) -> None:
    path = tmp_path / "registry.yaml"
    path.write_text(
        "series:\n"
        "  - id: usdthb\n    provider: BOT\n    series_id: DAILY_REF_RATE\n"
        "    url: https://example.com\n    unit: THB per USD\n"
        "    frequency: daily\n    priority: P0\n    rate_type: interbank\n",
        encoding="utf-8",
    )
    with pytest.raises(RegistryError, match="base_ccy"):
        load_registry(path)


def test_registry_requires_rate_type(tmp_path: Path) -> None:
    path = tmp_path / "registry.yaml"
    path.write_text(
        "series:\n"
        "  - id: usdthb\n    provider: BOT\n    series_id: DAILY_REF_RATE\n"
        "    url: https://example.com\n    unit: THB per USD\n"
        "    frequency: daily\n    priority: P0\n    base_ccy: USD\n"
        "    quote_ccy: THB\n",
        encoding="utf-8",
    )
    with pytest.raises(RegistryError, match="rate_type"):
        load_registry(path)
