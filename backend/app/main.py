from __future__ import annotations

import sys
from datetime import datetime, timezone
from importlib import util

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.models import HealthResponse, ResolveRequest, ResolveResponse
from app.services.offline import offline_city_count
from app.services.resolver import ResolveError, resolve_timezone

app = FastAPI(
    title="City Timezone Mapper",
    description=(
        "Resolve a city + country to an IANA timezone id, with mappings for "
        "Python zoneinfo (recommended) and pytz."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
        "http://localhost:8001",
        "http://127.0.0.1:8001",
    ],
    allow_credentials=True,
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


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "City Timezone Mapper",
        "docs": "/docs",
        "health": "/api/health",
        "resolve": "POST /api/resolve",
    }
