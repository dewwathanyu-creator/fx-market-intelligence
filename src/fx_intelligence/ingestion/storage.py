"""Content-addressed raw response storage."""

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def store_raw(root: Path, source_id: str, window: str, payload: dict[str, Any]) -> Path:
    """Store an immutable payload once and return its file path."""
    if (
        not source_id.replace("_", "").isalnum()
        or not window.replace("-", "").replace("_", "").isalnum()
    ):
        raise ValueError("source_id/window contains unsafe path characters")
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()[:16]
    directory = root / source_id / window
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{digest}.json"
    if not path.exists():
        envelope = {
            "source_id": source_id,
            "window": window,
            "retrieved_at": datetime.now(UTC).isoformat(),
            "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "payload": payload,
        }
        path.write_text(json.dumps(envelope, indent=2, ensure_ascii=False), encoding="utf-8")
    return path
