"""Small retrying HTTP JSON transport."""

import time
from collections.abc import Callable, Mapping
from typing import Any

import httpx


class FetchError(RuntimeError):
    """A provider request failed without disclosing its URL or credentials."""


def get_json(
    http: httpx.Client,
    url: str,
    *,
    params: Mapping[str, str] | None = None,
    headers: Mapping[str, str] | None = None,
    attempts: int = 3,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """Fetch JSON with bounded retries for transient HTTP failures."""
    if attempts < 1:
        raise ValueError("attempts must be positive")
    for attempt in range(attempts):
        try:
            response = http.get(url, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                raise ValueError("provider response must be a JSON object")
            return data
        except (httpx.TimeoutException, httpx.TransportError, httpx.HTTPStatusError) as exc:
            status = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else None
            retryable = status is None or status in {
                429,
                500,
                502,
                503,
                504,
            }
            if not retryable or attempt + 1 == attempts:
                if status is None:
                    raise FetchError("provider request failed after retries") from None
                raise FetchError(f"provider returned HTTP {status}") from None
            sleep(min(2**attempt, 8))
    raise RuntimeError("unreachable")
