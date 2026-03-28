from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class Location:
    id: int
    name: str
    city: str
    state: str
    timezone: str


@dataclass(frozen=True)
class Appointment:
    location_id: int
    start: datetime
    end: datetime
    active: bool


@dataclass
class ScanResult:
    location_id: int
    city: str
    new_appointments: list[Appointment] = field(default_factory=list)
    error: str | None = None
