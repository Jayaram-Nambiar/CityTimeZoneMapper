from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from app.main import app
from app.services.geo_timezone import timezone_from_coordinates
from app.services.library_bridge import build_library_mapping
from app.services.offline import find_offline_match, load_offline_cities, offline_city_count
from app.services.resolver import ResolveError, resolve_timezone


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["zoneinfo_available"] is True
    assert payload["offline_cities"] == offline_city_count()
    assert payload["offline_cities"] > 0


def test_api_index() -> None:
    client = TestClient(app)
    response = client.get("/api")
    assert response.status_code == 200
    payload = response.json()
    assert payload["health"] == "/api/health"
    assert "resolve" in payload


def test_offline_catalog_loads() -> None:
    cities = load_offline_cities()
    assert isinstance(cities, list)
    assert len(cities) >= 50
    sample = cities[0]
    for key in ("city", "country", "latitude", "longitude", "timezone"):
        assert key in sample


def test_offline_tokyo_match() -> None:
    match = find_offline_match("Tokyo", "Japan")
    assert match is not None
    assert match["timezone"] == "Asia/Tokyo"


def test_offline_cochin_alias() -> None:
    match = find_offline_match("cochin", "India")
    assert match is not None
    assert match["timezone"] == "Asia/Kolkata"


def test_timezonefinder_known_point() -> None:
    assert timezone_from_coordinates(40.7128, -74.0060) == "America/New_York"


def test_library_bridge_zoneinfo() -> None:
    mapping = build_library_mapping("Asia/Kolkata")
    assert mapping.iana_id == "Asia/Kolkata"
    assert mapping.zoneinfo["recommended"] is True
    assert mapping.utc_offset[0] in {"+", "-"}
    assert "T" in mapping.current_local_time_iso


def test_resolve_offline_endpoint() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/resolve",
        json={"city": "Tokyo", "country": "Japan", "prefer_source": "offline"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["timezone"] == "Asia/Tokyo"
    assert payload["source"] == "offline"
    assert payload["libraries"]["iana_id"] == "Asia/Tokyo"


def test_resolve_validation_rejects_empty() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/resolve",
        json={"city": "", "country": "Japan", "prefer_source": "offline"},
    )
    assert response.status_code == 422


def test_resolve_unknown_offline_city() -> None:
    try:
        asyncio.run(
            resolve_timezone(
                "ZzNotARealCity",
                "ZzNotACountry",
                prefer_source="offline",
            )
        )
        raised = False
    except ResolveError:
        raised = True
    assert raised is True


def test_resolve_online_tokyo() -> None:
    """Live network check — exercises the cloud-tolerant geocoder chain."""
    result = asyncio.run(resolve_timezone("Tokyo", "Japan", prefer_source="online"))
    assert result.timezone == "Asia/Tokyo"
    assert result.source == "online"
    assert result.coordinates is not None
