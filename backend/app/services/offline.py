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


def find_offline_match(city: str, country: str) -> dict[str, Any] | None:
    """Exact then fuzzy-ish match against the bundled city catalog."""
    city_n = normalize(city)
    country_n = normalize(country)
    cities = load_offline_cities()

    exact = [
        c
        for c in cities
        if normalize(c["city"]) == city_n
        and (
            normalize(c["country"]) == country_n
            or normalize(c.get("country_code", "")) == country_n
            or country_n in normalize(c["country"])
        )
    ]
    if exact:
        return exact[0]

    city_partial = [
        c
        for c in cities
        if city_n in normalize(c["city"]) or normalize(c["city"]) in city_n
    ]
    country_filtered = [
        c
        for c in city_partial
        if country_n in normalize(c["country"])
        or normalize(c.get("country_code", "")) == country_n
        or normalize(c["country"]) in country_n
    ]
    pool = country_filtered or city_partial
    if not pool:
        return None

    # Prefer shortest city-name distance (simple heuristic).
    pool.sort(key=lambda c: abs(len(normalize(c["city"])) - len(city_n)))
    return pool[0]


def offline_city_count() -> int:
    return len(load_offline_cities())
