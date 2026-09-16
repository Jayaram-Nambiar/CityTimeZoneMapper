from __future__ import annotations

import httpx

from app.models import Coordinates, ResolveResponse
from app.services.geo_timezone import timezone_from_coordinates
from app.services.library_bridge import build_library_mapping
from app.services.nominatim import geocode_city_country
from app.services.offline import find_offline_match


class ResolveError(Exception):
    def __init__(self, message: str, status_code: int = 404) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def resolve_timezone(
    city: str,
    country: str,
    prefer_source: str = "auto",
) -> ResolveResponse:
    city = city.strip()
    country = country.strip()
    if not city or not country:
        raise ResolveError("Both city and country are required.", status_code=400)

    notes: list[str] = []

    if prefer_source in ("auto", "online"):
        try:
            online = await _resolve_online(city, country, notes)
            if online:
                return online
            notes.append("Online geocoding returned no match.")
        except httpx.HTTPError as exc:
            notes.append(f"Online geocoding failed ({exc.__class__.__name__}).")
            if prefer_source == "online":
                raise ResolveError(
                    "Online resolution failed and offline fallback was not requested. "
                    f"({exc.__class__.__name__})",
                    status_code=502,
                ) from exc

        if prefer_source == "online":
            raise ResolveError("No online match found for that city and country.")

    offline = _resolve_offline(city, country, notes)
    if offline:
        return offline

    detail = "Could not resolve timezone for that city and country via online or offline methods."
    if notes:
        detail = f"{detail} {' '.join(notes)}"
    raise ResolveError(detail)


async def _resolve_online(
    city: str,
    country: str,
    notes: list[str],
) -> ResolveResponse | None:
    geo = await geocode_city_country(city, country)
    if not geo:
        return None

    tz_id = timezone_from_coordinates(geo["latitude"], geo["longitude"])
    if not tz_id:
        notes.append("Coordinates found, but no timezone polygon matched.")
        return None

    notes.append("Resolved via OpenStreetMap Nominatim + timezonefinder.")
    return ResolveResponse(
        city=city,
        country=country,
        matched_name=geo["display_name"],
        timezone=tz_id,
        coordinates=Coordinates(
            latitude=geo["latitude"],
            longitude=geo["longitude"],
        ),
        source="online",
        confidence="high",
        libraries=build_library_mapping(tz_id),
        notes=notes,
    )


def _resolve_offline(
    city: str,
    country: str,
    notes: list[str],
) -> ResolveResponse | None:
    match = find_offline_match(city, country)
    if not match:
        return None

    tz_id = match.get("timezone")
    lat = match.get("latitude")
    lon = match.get("longitude")

    if not tz_id and lat is not None and lon is not None:
        tz_id = timezone_from_coordinates(float(lat), float(lon))

    if not tz_id:
        return None

    # Prefer recomputing from coordinates when present (keeps data honest).
    if lat is not None and lon is not None:
        computed = timezone_from_coordinates(float(lat), float(lon))
        if computed:
            tz_id = computed

    notes.append("Resolved via bundled offline city catalog + timezonefinder.")
    coords = None
    if lat is not None and lon is not None:
        coords = Coordinates(latitude=float(lat), longitude=float(lon))

    from app.services.offline import normalize

    exact = normalize(match["city"]) == normalize(city) and (
        normalize(match["country"]) == normalize(country)
        or normalize(match.get("country_code", "")) == normalize(country)
    )
    confidence = "high" if exact else "medium"

    return ResolveResponse(
        city=city,
        country=country,
        matched_name=f"{match['city']}, {match['country']}",
        timezone=tz_id,
        coordinates=coords,
        source="offline",
        confidence=confidence,
        libraries=build_library_mapping(tz_id),
        notes=notes,
    )
