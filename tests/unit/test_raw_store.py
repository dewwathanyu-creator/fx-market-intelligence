from pathlib import Path

from fx_intelligence.ingestion.storage import store_raw


def test_same_payload_is_idempotent(tmp_path: Path) -> None:
    payload = {"observations": [{"date": "2026-01-01", "value": "4.2"}]}
    first = store_raw(tmp_path, "fred_dgs2", "2026-01", payload)
    second = store_raw(tmp_path, "fred_dgs2", "2026-01", payload)
    assert first == second
    assert len(list(tmp_path.rglob("*.json"))) == 1


def test_date_range_window_is_allowed(tmp_path: Path) -> None:
    path = store_raw(tmp_path, "fred_dgs2", "2026-01-01_2026-01-31", {"observations": []})
    assert path.is_file()
