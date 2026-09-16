from __future__ import annotations

"""Online place → coordinates (and optional IANA timezone) geocoding.

Root cause addressed: the public Nominatim instance frequently rate-limits or
times out from cloud datacenter IPs (e.g. Render). Local laptops often work
fine against the same endpoint, which makes the failure look mysterious.

Strategy: try geocoders that are designed for API/cloud use first, then fall
back to Nominatim, then let the resolver fall back to the offline catalog.
"""

import asyncio
from typing import Any

import httpx

USER_AGENT = (
    "CityTimezoneMapper/1.2 "
    "(https://github.com/Jayaram-Nambiar/CityTimeZoneMapper; "
    "contact: jayaramhnambiar@gmail.com)"
)
_TIMEOUT = httpx.Timeout(20.0, connect=8.0)

# Prefer populated places over airports/POIs when a provider returns a list.
_OPEN_METEO_PLACE_CODES = {
    "PPL",
    "PPLA",
    "PPLA2",
    "PPLA3",
    "PPLA4",
    "PPLC",
    "PPLG",
    "PPLS",
}


async def geocode_city_country(city: str, country: str) -> dict[str, Any] | None:
    """Return {latitude, longitude, display_name, timezone?, provider} or None."""
    city = city.strip()
    country = country.strip()
    errors: list[str] = []

    providers = (
        ("open-meteo", _geocode_open_meteo),
        ("photon", _geocode_photon),
        ("nominatim", _geocode_nominatim),
    )

    async with httpx.AsyncClient(
        timeout=_TIMEOUT,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        follow_redirects=True,
    ) as client:
        for name, fn in providers:
            try:
                hit = await fn(client, city, country)
                if hit:
                    hit["provider"] = name
                    return hit
                errors.append(f"{name}: no match")
            except httpx.HTTPError as exc:
                errors.append(f"{name}: {exc.__class__.__name__}")
                await asyncio.sleep(0.35)

    return {"_errors": errors} if errors else None


def provider_errors(payload: dict[str, Any] | None) -> list[str]:
    if not payload:
        return []
    return list(payload.get("_errors") or [])


def is_geocode_hit(payload: dict[str, Any] | None) -> bool:
    return bool(payload) and "latitude" in payload and "longitude" in payload


async def _geocode_open_meteo(
    client: httpx.AsyncClient,
    city: str,
    country: str,
) -> dict[str, Any] | None:
    """Free GeoNames-backed API; cloud-friendly and often returns timezone."""
    response = await client.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": f"{city}, {country}",
            "count": 5,
            "language": "en",
            "format": "json",
        },
    )
    response.raise_for_status()
    results = response.json().get("results") or []
    if not results:
        response = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 10, "language": "en", "format": "json"},
        )
        response.raise_for_status()
        results = [
            row
            for row in (response.json().get("results") or [])
            if _country_matches(row.get("country"), row.get("country_code"), country)
        ]

    if not results:
        return None

    pick = _pick_open_meteo(results, city)
    if not pick:
        return None
    # If we only matched a non-settlement feature (airport/POI), defer to the next
    # provider so city queries like "Cochin" can resolve to the actual city.
    if pick.get("feature_code") not in _OPEN_METEO_PLACE_CODES:
        return None

    display = ", ".join(
        part
        for part in (
            pick.get("name"),
            pick.get("admin1"),
            pick.get("country"),
        )
        if part
    )
    return {
        "latitude": float(pick["latitude"]),
        "longitude": float(pick["longitude"]),
        "display_name": display or f"{city}, {country}",
        "timezone": pick.get("timezone"),
    }


def _pick_open_meteo(results: list[dict[str, Any]], city: str) -> dict[str, Any] | None:
    city_n = city.strip().lower()
    places = [r for r in results if r.get("feature_code") in _OPEN_METEO_PLACE_CODES]
    pool = places or results

    exact = [r for r in pool if str(r.get("name", "")).lower() == city_n]
    if exact:
        exact.sort(key=lambda r: int(r.get("population") or 0), reverse=True)
        return exact[0]

    soft = [
        r
        for r in pool
        if city_n in str(r.get("name", "")).lower()
        or str(r.get("name", "")).lower() in city_n
    ]
    if soft:
        soft.sort(key=lambda r: int(r.get("population") or 0), reverse=True)
        return soft[0]
    return pool[0]


async def _geocode_photon(
    client: httpx.AsyncClient,
    city: str,
    country: str,
) -> dict[str, Any] | None:
    """Komoot Photon — OSM-based, generally more usable from cloud than public Nominatim."""
    response = await client.get(
        "https://photon.komoot.io/api/",
        params={"q": f"{city}, {country}", "limit": 5},
    )
    response.raise_for_status()
    features = response.json().get("features") or []
    if not features:
        return None

    preferred_types = {"city", "town", "village", "hamlet", "municipality", "locality"}
    ranked = sorted(
        features,
        key=lambda f: (
            0 if (f.get("properties") or {}).get("type") in preferred_types else 1,
            0
            if (f.get("properties") or {}).get("country", "").lower() == country.lower()
            else 1,
        ),
    )
    feature = ranked[0]
    props = feature.get("properties") or {}
    coords = (feature.get("geometry") or {}).get("coordinates") or []
    if len(coords) < 2:
        return None

    lon, lat = float(coords[0]), float(coords[1])
    display = ", ".join(
        part
        for part in (
            props.get("name"),
            props.get("state"),
            props.get("country"),
        )
        if part
    )
    return {
        "latitude": lat,
        "longitude": lon,
        "display_name": display or f"{city}, {country}",
    }


async def _geocode_nominatim(
    client: httpx.AsyncClient,
    city: str,
    country: str,
) -> dict[str, Any] | None:
    """Public OSM Nominatim — last online resort (often blocked/slow from cloud IPs)."""
    headers = {"Accept-Language": "en"}
    for params in (
        {
            "city": city,
            "country": country,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        },
        {
            "q": f"{city}, {country}",
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        },
    ):
        response = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        results = response.json()
        if not results:
            continue
        hit = results[0]
        return {
            "latitude": float(hit["lat"]),
            "longitude": float(hit["lon"]),
            "display_name": hit.get("display_name") or f"{city}, {country}",
        }
    return None


def _country_matches(name: str | None, code: str | None, wanted: str) -> bool:
    wanted_n = wanted.strip().lower()
    if not wanted_n:
        return True
    if code and code.strip().lower() == wanted_n:
        return True
    if name and (
        name.strip().lower() == wanted_n
        or wanted_n in name.strip().lower()
        or name.strip().lower() in wanted_n
    ):
        return True
    return False
