"""FRED observations client."""

import time
from collections.abc import Callable
from typing import Any

import httpx

from .http import get_json


class FredClient:
    """Fetch a FRED series while preserving revision metadata."""

    def __init__(
        self,
        api_key: str,
        *,
        http: httpx.Client,
        attempts: int = 3,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not api_key:
            raise ValueError("FRED_API_KEY is required")
        self.api_key = api_key
        self.http = http
        self.attempts = attempts
        self.sleep = sleep

    def fetch(self, series_id: str, start: str, end: str) -> list[dict[str, Any]]:
        """Return parsed observations for an inclusive date window."""
        data = get_json(
            self.http,
            "https://api.stlouisfed.org/fred/series/observations",
            params={
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "observation_start": start,
                "observation_end": end,
            },
            attempts=self.attempts,
            sleep=self.sleep,
        )
        observations = data.get("observations")
        if not isinstance(observations, list):
            raise ValueError("FRED response missing observations")
        result: list[dict[str, Any]] = []
        for row in observations:
            if not isinstance(row, dict) or not all(
                key in row for key in ("date", "value", "realtime_start", "realtime_end")
            ):
                raise ValueError("FRED observation missing required fields")
            result.append(
                {
                    "date": row["date"],
                    "value": None if row["value"] == "." else float(row["value"]),
                    "realtime_start": row["realtime_start"],
                    "realtime_end": row["realtime_end"],
                }
            )
        return result
