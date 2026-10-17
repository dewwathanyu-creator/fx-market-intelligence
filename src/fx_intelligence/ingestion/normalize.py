"""Convert saved official payloads into source-aware canonical observations."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from fx_intelligence.schemas.models import FXObservation, MacroObservation


def normalize_payload(
    envelope: dict[str, Any], source: dict[str, Any]
) -> tuple[list[FXObservation], list[MacroObservation]]:
    """Parse a saved raw envelope using its matching registry entry."""
    retrieved_at = datetime.fromisoformat(envelope["retrieved_at"])
    if retrieved_at.tzinfo is None:
        raise ValueError("retrieval timestamp must carry a timezone")
    payload = envelope["payload"]
    if source["provider"] == "BOT":
        if source.get("scaling_check_required"):
            raise ValueError("provider currency scaling requires verification")
        detail = payload["result"]["data"]["data_detail"]
        if not isinstance(detail, list):
            raise ValueError("BOT data_detail must be a list")
        is_average = source["series_id"].startswith("DAILY_AVG_EXG_RATE")
        currency = source["base_ccy"]
        result: list[FXObservation] = []
        for row in detail:
            if is_average and row.get("currency_id") != currency:
                continue
            rate_text = row.get("mid_rate" if is_average else "rate")
            result.append(
                FXObservation(
                    source_id=source["id"],
                    series_id=source["series_id"],
                    base_ccy=currency,
                    quote_ccy=source["quote_ccy"],
                    rate_type=source["rate_type"],
                    observation_date=date.fromisoformat(row["period"]),
                    retrieved_at=retrieved_at,
                    rate=Decimal(str(rate_text)) if rate_text not in (None, "") else None,
                    unit=source["unit"],
                    frequency=source["frequency"],
                )
            )
        return result, []
    if source["provider"] == "FRED":
        rows = payload["observations"]
        if not isinstance(rows, list):
            raise ValueError("FRED observations must be a list")
        macro = [
            MacroObservation(
                source_id=source["id"],
                series_id=source["series_id"],
                observation_date=date.fromisoformat(row["date"]),
                retrieved_at=retrieved_at,
                value=Decimal(str(row["value"])) if row["value"] is not None else None,
                unit=source["unit"],
                frequency=source["frequency"],
                vintage_date=date.fromisoformat(row["realtime_start"]),
                release_date=None,
            )
            for row in rows
        ]
        return [], macro
    raise ValueError("unsupported provider")
