from datetime import date

from fx_intelligence.ingestion.build_local import DEFAULT_SOURCE_IDS, month_windows


def test_month_windows_clip_to_requested_range():
    assert month_windows(date(2026, 1, 30), date(2026, 3, 2)) == [
        (date(2026, 1, 30), date(2026, 1, 31)),
        (date(2026, 2, 1), date(2026, 2, 28)),
        (date(2026, 3, 1), date(2026, 3, 2)),
    ]


def test_default_live_sources_avoid_unverified_jpy_scaling():
    assert "bot_jpythb_bank_average" not in DEFAULT_SOURCE_IDS
    assert "bot_usdthb_interbank" in DEFAULT_SOURCE_IDS
