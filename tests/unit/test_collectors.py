import httpx
import pytest

from fx_intelligence.ingestion.bot import BotClient
from fx_intelligence.ingestion.fred import FredClient
from fx_intelligence.ingestion.http import FetchError


def test_fred_preserves_revision_dates_and_missing_values() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        assert request.url.params["series_id"] == "DGS2"
        assert request.url.params["file_type"] == "json"
        return httpx.Response(
            200,
            json={
                "observations": [
                    {
                        "date": "2026-01-02",
                        "value": "4.25",
                        "realtime_start": "2026-01-03",
                        "realtime_end": "9999-12-31",
                    },
                    {
                        "date": "2026-01-03",
                        "value": ".",
                        "realtime_start": "2026-01-04",
                        "realtime_end": "9999-12-31",
                    },
                ]
            },
        )

    with httpx.Client(transport=httpx.MockTransport(respond)) as http:
        rows = FredClient("test-key", http=http).fetch("DGS2", "2026-01-02", "2026-01-03")
    assert rows[0]["value"] == 4.25
    assert rows[0]["realtime_start"] == "2026-01-03"
    assert rows[1]["value"] is None


def test_bot_uses_authorization_header() -> None:
    def respond(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "test-key"
        assert "test-key" not in str(request.url)
        return httpx.Response(200, json={"result": {"data": []}})

    with httpx.Client(transport=httpx.MockTransport(respond)) as http:
        result = BotClient("test-key", http=http).fetch(
            "https://gateway.api.bot.or.th/Stat-ReferenceRate/v2/DAILY_REF_RATE/",
            {"start_period": "2026-01-01", "end_period": "2026-01-31"},
        )
    assert result == {"result": {"data": []}}


def test_retry_is_bounded_on_429() -> None:
    attempts = 0

    def respond(request: httpx.Request) -> httpx.Response:
        nonlocal attempts
        attempts += 1
        return httpx.Response(429)

    with httpx.Client(transport=httpx.MockTransport(respond)) as http:
        with pytest.raises(FetchError):
            FredClient("test-key", http=http, attempts=2, sleep=lambda _: None).fetch(
                "DGS2", "2026-01-01", "2026-01-31"
            )
    assert attempts == 2


def test_fred_failure_does_not_expose_key() -> None:
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(403))) as http:
        with pytest.raises(FetchError) as error:
            FredClient("private-key", http=http).fetch("DGS2", "2026-01-01", "2026-01-31")
    assert "private-key" not in str(error.value)
