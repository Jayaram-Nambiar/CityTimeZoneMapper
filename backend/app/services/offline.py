from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cities_offline.json"


@lru_cache(maxsize=1)
def load_offline_cities() -> list[dict[str, Any]]:
    with DATA_PATH.open(encoding="utf-8-sig") as handle:
        payload = json.load(handle)
    return payload["cities"]


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().split())


def _city_names(entry: dict[str, Any]) -> list[str]:
    names = [entry["city"], *entry.get("aliases", [])]
    return [normalize(name) for name in names if name]


def find_offline_match(city: str, country: str) -> dict[str, Any] | None:
    """Exact then fuzzy-ish match against the bundled city catalog."""
    city_n = normalize(city)
    country_n = normalize(country)
    cities = load_offline_cities()

    def country_ok(entry: dict[str, Any]) -> bool:
        return (
            normalize(entry["country"]) == country_n
            or normalize(entry.get("country_code", "")) == country_n
            or country_n in normalize(entry["country"])
            or normalize(entry["country"]) in country_n
        )

    exact = [
        c
        for c in cities
        if city_n in _city_names(c) and country_ok(c)
    ]
    if exact:
        return exact[0]

    city_partial = [
        c
        for c in cities
        if any(
            city_n in name or name in city_n
            for name in _city_names(c)
        )
    ]
    country_filtered = [c for c in city_partial if country_ok(c)]
    pool = country_filtered or city_partial
    if not pool:
        return None

    pool.sort(key=lambda c: min(abs(len(name) - len(city_n)) for name in _city_names(c)))
    return pool[0]


def offline_city_count() -> int:
    return len(load_offline_cities())
