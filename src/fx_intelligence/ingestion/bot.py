"""Bank of Thailand API client."""

import time
from collections.abc import Callable, Mapping
from typing import Any

import httpx

from .http import get_json


class BotClient:
    """Fetch BOT payloads without erasing provider fields or rate type."""

    def __init__(
        self,
        api_key: str,
        *,
        http: httpx.Client,
        attempts: int = 3,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if not api_key:
            raise ValueError("BOT_API_KEY is required")
        self.api_key = api_key
        self.http = http
        self.attempts = attempts
        self.sleep = sleep

    def fetch(self, url: str, params: Mapping[str, str]) -> dict[str, Any]:
        """Return the raw BOT response for a registry endpoint."""
        if not url.startswith("https://gateway.api.bot.or.th/"):
            raise ValueError("BOT endpoint must use the official HTTPS gateway")
        return get_json(
            self.http,
            url,
            params=params,
            headers={"Authorization": self.api_key},
            attempts=self.attempts,
            sleep=self.sleep,
        )
