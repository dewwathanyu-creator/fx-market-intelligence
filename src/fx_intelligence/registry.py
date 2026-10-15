"""Load and validate source metadata."""

from pathlib import Path
from typing import Any

import yaml


class RegistryError(ValueError):
    """Source metadata is incomplete or contradictory."""


REQUIRED = {"id", "provider", "series_id", "url", "unit", "frequency", "priority", "rate_type"}


def load_registry(path: Path) -> list[dict[str, Any]]:
    """Load a registry and enforce essential metadata for each series."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("series"), list):
        raise RegistryError("registry requires a series list")
    seen: set[str] = set()
    for item in data["series"]:
        if not isinstance(item, dict):
            raise RegistryError("series item must be a mapping")
        missing = sorted(key for key in REQUIRED if not item.get(key))
        if missing:
            raise RegistryError(f"missing {', '.join(missing)}")
        if item["id"] in seen:
            raise RegistryError(f"duplicate series id: {item['id']}")
        seen.add(item["id"])
        if item["rate_type"] != "macro":
            for key in ("base_ccy", "quote_ccy"):
                if not item.get(key):
                    raise RegistryError(f"{item['id']} missing {key}")
            if item["base_ccy"] == item["quote_ccy"]:
                raise RegistryError(f"{item['id']} has identical base and quote")
    return data["series"]
