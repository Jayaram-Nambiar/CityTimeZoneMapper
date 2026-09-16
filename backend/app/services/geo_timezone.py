from __future__ import annotations

from functools import lru_cache

from timezonefinder import TimezoneFinder


@lru_cache(maxsize=1)
def _finder() -> TimezoneFinder:
    return TimezoneFinder(in_memory=True)


def timezone_from_coordinates(latitude: float, longitude: float) -> str | None:
    """Offline lat/lon → IANA timezone using the timezonefinder polygon dataset."""
    return _finder().timezone_at(lat=latitude, lng=longitude)
