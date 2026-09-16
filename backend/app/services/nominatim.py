from __future__ import annotations

from typing import Any

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "CityTimeZoneMapper/1.0 (github.com/Jayaram-Nambiar/CityTimeZoneMapper; contact: jayaramhnambiar@gmail.com)"


async def geocode_city_country(city: str, country: str) -> dict[str, Any] | None:
    """Resolve city+country to coordinates via OpenStreetMap Nominatim (free)."""
    params = {
        "city": city.strip(),
        "country": country.strip(),
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    async with httpx.AsyncClient(timeout=12.0) as client:
        response = await client.get(NOMINATIM_URL, params=params, headers=headers)
        response.raise_for_status()
        results = response.json()

    if not results:
        # Fallback free-form query if structured search misses.
        async with httpx.AsyncClient(timeout=12.0) as client:
            response = await client.get(
                NOMINATIM_URL,
                params={
                    "q": f"{city.strip()}, {country.strip()}",
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1,
                },
                headers=headers,
            )
            response.raise_for_status()
            results = response.json()

    if not results:
        return None

    hit = results[0]
    address = hit.get("address") or {}
    display = hit.get("display_name") or f"{city}, {country}"
    return {
        "latitude": float(hit["lat"]),
        "longitude": float(hit["lon"]),
        "display_name": display,
        "address": address,
    }
