"""Live provider payload shapes map to explicit canonical contracts."""

from datetime import date
from decimal import Decimal

import pytest

from fx_intelligence.ingestion.normalize import normalize_payload


def test_bot_reference_and_average_are_distinct_rate_types():
    ref = {
        "id": "bot_usdthb_interbank",
        "provider": "BOT",
        "series_id": "DAILY_REF_RATE",
        "base_ccy": "USD",
        "quote_ccy": "THB",
        "rate_type": "interbank_weighted_average",
        "unit": "THB per USD",
        "frequency": "daily",
    }
    envelope = {
        "retrieved_at": "2025-02-01T00:00:00+00:00",
        "payload": {
            "result": {"data": {"data_detail": [{"period": "2025-01-06", "rate": "34.50"}]}}
        },
    }
    fx, macro = normalize_payload(envelope, ref)
    assert macro == [] and len(fx) == 1
    assert fx[0].rate == Decimal("34.50") and fx[0].observation_date == date(2025, 1, 6)
    avg = {
        **ref,
        "id": "bot_eurthb_bank_average",
        "series_id": "DAILY_AVG_EXG_RATE:EUR",
        "base_ccy": "EUR",
        "rate_type": "commercial_bank_average",
        "unit": "THB per EUR",
    }
    envelope["payload"]["result"]["data"]["data_detail"] = [
        {"period": "2025-01-06", "currency_id": "EUR", "mid_rate": "35.70"}
    ]
    fx, _ = normalize_payload(envelope, avg)
    assert fx[0].rate == Decimal("35.70") and fx[0].rate_type == "commercial_bank_average"


def test_fred_vintage_is_preserved_without_invented_release_date():
    source = {
        "id": "fred_fedfunds",
        "provider": "FRED",
        "series_id": "FEDFUNDS",
        "unit": "percent per annum",
        "frequency": "monthly",
    }
    envelope = {
        "retrieved_at": "2025-02-01T00:00:00+00:00",
        "payload": {
            "observations": [
                {
                    "date": "2025-01-01",
                    "value": 4.33,
                    "realtime_start": "2025-02-01",
                    "realtime_end": "9999-12-31",
                }
            ]
        },
    }
    fx, macro = normalize_payload(envelope, source)
    assert fx == [] and len(macro) == 1
    assert macro[0].value == Decimal("4.33")
    assert macro[0].vintage_date == date(2025, 2, 1)
    assert macro[0].release_date is None


def test_unverified_jpy_scale_is_not_silently_accepted():
    source = {
        "id": "bot_jpythb_bank_average",
        "provider": "BOT",
        "series_id": "DAILY_AVG_EXG_RATE:JPY",
        "base_ccy": "JPY",
        "quote_ccy": "THB",
        "rate_type": "commercial_bank_average",
        "unit": "provider-scaled THB per JPY",
        "frequency": "daily",
        "scaling_check_required": True,
    }
    envelope = {
        "retrieved_at": "2025-02-01T00:00:00+00:00",
        "payload": {"result": {"data": {"data_detail": []}}},
    }
    with pytest.raises(ValueError, match="scaling"):
        normalize_payload(envelope, source)
