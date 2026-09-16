from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class ResolveRequest(BaseModel):
    city: str = Field(..., min_length=1, max_length=120, examples=["Tokyo"])
    country: str = Field(..., min_length=1, max_length=120, examples=["Japan"])
    prefer_source: Literal["auto", "online", "offline"] = "auto"


class Coordinates(BaseModel):
    latitude: float
    longitude: float


class TimeLibraryMapping(BaseModel):
    """How to consume the IANA id with common Python timezone libraries."""

    iana_id: str
    zoneinfo: dict[str, Any]
    pytz: dict[str, Any]
    current_local_time_iso: str
    utc_offset: str
    is_dst: bool


class ResolveResponse(BaseModel):
    city: str
    country: str
    matched_name: str | None = None
    timezone: str
    coordinates: Coordinates | None = None
    source: Literal["online", "offline"]
    confidence: Literal["high", "medium", "low"]
    libraries: TimeLibraryMapping
    notes: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    python_version: str
    zoneinfo_available: bool
    tzdata_available: bool
    offline_cities: int
    server_time_utc: datetime
