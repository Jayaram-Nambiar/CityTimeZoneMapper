from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from importlib import util
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models import HealthResponse, ResolveRequest, ResolveResponse
from app.services.offline import offline_city_count
from app.services.resolver import ResolveError, resolve_timezone

# backend/app/main.py → repo root is parents[2]
REPO_ROOT = Path(__file__).resolve().parents[2]
STATIC_DIR = REPO_ROOT / "frontend" / "dist"
INDEX_FILE = STATIC_DIR / "index.html"


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "").strip()
    if raw == "*":
        return ["*"]
    if raw:
        return [origin.strip() for origin in raw.split(",") if origin.strip()]
    return [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ]


app = FastAPI(
    title="City Timezone Mapper",
    description=(
        "Resolve a city + country to an IANA timezone id, with mappings for "
        "Python zoneinfo (recommended) and pytz."
    ),
    version="1.0.0",
)

_origins = _cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=_origins != ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        python_version=sys.version.split()[0],
        zoneinfo_available=util.find_spec("zoneinfo") is not None,
        tzdata_available=util.find_spec("tzdata") is not None,
        offline_cities=offline_city_count(),
        server_time_utc=datetime.now(timezone.utc),
    )


@app.post("/api/resolve", response_model=ResolveResponse)
async def resolve(payload: ResolveRequest) -> ResolveResponse:
    try:
        return await resolve_timezone(
            city=payload.city,
            country=payload.country,
            prefer_source=payload.prefer_source,
        )
    except ResolveError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api")
def api_index() -> dict[str, str]:
    return {
        "service": "City Timezone Mapper",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "health": "/api/health",
        "resolve": "POST /api/resolve",
    }


if INDEX_FILE.is_file():
    # Mounted last so /api/*, /docs, /openapi.json stay on the API.
    app.mount(
        "/",
        StaticFiles(directory=str(STATIC_DIR), html=True),
        name="frontend",
    )
else:

    @app.get("/")
    def root() -> dict[str, str]:
        return {
            "service": "City Timezone Mapper",
            "docs": "/docs",
            "openapi": "/openapi.json",
            "health": "/api/health",
            "resolve": "POST /api/resolve",
            "note": (
                "Frontend build not found. Run `npm run build` in frontend/, "
                "or use the Vite dev server on port 5173."
            ),
        }
