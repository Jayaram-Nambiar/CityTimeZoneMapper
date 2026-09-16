from __future__ import annotations

import asyncio
from typing import Any

import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
USER_AGENT = (
    "CityTimezoneMapper/1.1 "
    "(https://github.com/Jayaram-Nambiar/CityTimeZoneMapper; "
    "contact: jayaramhnambiar@gmail.com)"
)
# Cloud hosts (Render free) often need longer budgets than local laptops.
_TIMEOUT = httpx.Timeout(25.0, connect=10.0)
_MAX_ATTEMPTS = 3


async def geocode_city_country(city: str, country: str) -> dict[str, Any] | None:
    """Resolve city+country to coordinates via OpenStreetMap Nominatim (free)."""
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Accept-Language": "en",
    }
    structured = {
        "city": city.strip(),
        "country": country.strip(),
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }
    freeform = {
        "q": f"{city.strip()}, {country.strip()}",
        "format": "json",
        "limit": 1,
        "addressdetails": 1,
    }

    async with httpx.AsyncClient(timeout=_TIMEOUT, headers=headers, follow_redirects=True) as client:
        results = await _search_with_retries(client, structured)
        if not results:
            results = await _search_with_retries(client, freeform)

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


async def _search_with_retries(
    client: httpx.AsyncClient,
    params: dict[str, Any],
) -> list[dict[str, Any]]:
    last_error: Exception | None = None
    for attempt in range(1, _MAX_ATTEMPTS + 1):
        try:
            response = await client.get(NOMINATIM_URL, params=params)
            # Nominatim may rate-limit cloud IPs; back off and retry.
            if response.status_code in {429, 502, 503, 504}:
                last_error = httpx.HTTPStatusError(
                    f"Nominatim returned {response.status_code}",
                    request=response.request,
                    response=response,
                )
                await asyncio.sleep(1.25 * attempt)
                continue
            response.raise_for_status()
            payload = response.json()
            return payload if isinstance(payload, list) else []
        except (httpx.TimeoutException, httpx.NetworkError, httpx.RemoteProtocolError) as exc:
            last_error = exc
            await asyncio.sleep(1.25 * attempt)
        except httpx.HTTPStatusError as exc:
            last_error = exc
            if exc.response is not None and exc.response.status_code in {403, 429, 502, 503, 504}:
                await asyncio.sleep(1.25 * attempt)
                continue
            raise

    if last_error is not None:
        raise last_error
    return []
