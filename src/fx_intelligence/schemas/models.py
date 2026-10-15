"""Typed contracts for source-aware FX and macro observations."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal


@dataclass(frozen=True)
class FXObservation:
    source_id: str
    series_id: str
    base_ccy: str
    quote_ccy: str
    rate_type: str
    observation_date: date
    retrieved_at: datetime
    rate: Decimal | None
    unit: str
    frequency: str


@dataclass(frozen=True)
class MacroObservation:
    source_id: str
    series_id: str
    observation_date: date
    retrieved_at: datetime
    value: Decimal | None
    unit: str
    frequency: str
    vintage_date: date | None
    release_date: date | None
