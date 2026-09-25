# Architecture — City Timezone Mapper

This document explains **why** the project is structured the way it is: the problem constraints, the major design choices, alternatives we rejected, and the tradeoffs you should know before changing things.

It complements:

- [`README.md`](../README.md) — overview + local setup  
- [`API.md`](API.md) — OpenAPI contracts and programmatic clients  
- [`DEPLOY.md`](DEPLOY.md) — public hosting  
- [`THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md) — dependency attribution  

---

## 1. Problem statement

**Input:** a human place description (`city` + `country`)  
**Output:** an **IANA timezone id** that can be passed to Python timezone APIs, plus enough metadata to trust and use the answer (source, coordinates, current offset, code snippets).

Constraints that shaped the design:

1. Prefer **free / open-source** services and libraries (no paid timezone SaaS required).  
2. Provide an **offline fallback** when the network or upstream geocoder fails.  
3. Target **Python 3.9+** best practice: `zoneinfo` + `tzdata`, while still acknowledging `pytz`.  
4. Ship a **professional UI** that works on desktop and mobile browsers.  
5. Keep the codebase small enough that a friend can clone, run, and understand it quickly.

---

## 2. High-level system shape

```text
┌──────────────────────────┐        ┌──────────────────────────────────────┐
│  React + Vite frontend   │  /api  │  FastAPI backend                     │
│  (presentation + forms)  │───────►│  resolve orchestration               │
└──────────────────────────┘        │    ├─ Nominatim client (online)      │
                                    │    ├─ offline city catalog           │
                                    │    ├─ timezonefinder (lat/lon→TZ)    │
                                    │    └─ zoneinfo / pytz bridge         │
                                    └──────────────────────────────────────┘
```

### Why a separate frontend and backend?

| Option | Verdict |
| --- | --- |
| Single Python template app (Jinja only) | Simpler deploy, weaker interactive UX and mobile polish |
| Frontend-only (call Nominatim from the browser) | Exposes abusive traffic patterns, CORS/policy pain, mixes secrets/UA poorly |
| **FastAPI API + React UI** (chosen) | Clear contract, reusable API for scripts, UI free to iterate |

The API is a first-class product: the UI is one client; `examples/python_client_demo.py` is another.

---

## 3. Core contract: IANA timezone ids

We standardize on strings like `America/Sao_Paulo`, not:

- raw UTC offsets alone (`+05:30`)  
- Windows timezone display names  
- country-level guesses (“India is IST”) without a place  

**Rationale**

- IANA ids are the interchange format across languages and databases.  
- Offsets change with daylight saving; ids encode the rule history.  
- Both `zoneinfo.ZoneInfo("...")` and `pytz.timezone("...")` accept the same ids.

The backend’s `libraries` object exists so callers see **exactly** how to consume the id in modern vs legacy Python.

---

## 4. Resolution pipeline

Implemented primarily in `backend/app/services/resolver.py`.

### 4.1 Online path

1. **Geocode** with a cloud-tolerant provider chain (`geocoding.py`):
   1. **Open-Meteo** (GeoNames-backed, free, returns timezone often)
   2. **Photon** (Komoot; OSM-based)
   3. **Nominatim** (public OSM instance — last resort)
2. **Map coordinates → timezone** with `timezonefinder` (`geo_timezone.py`)
3. **Enrich** with `zoneinfo`/`pytz` metadata (`library_bridge.py`)

**Root cause of “works locally, fails on Render”**

Public Nominatim aggressively rate-limits and sometimes blocks **datacenter IPs**. A home/laptop IP often succeeds while the same code on Render fails or times out, then offline fallback only helps if the city is in the catalog. That is an online-path reliability bug, not a missing offline alias.

**Why not Nominatim-only?**

- Free for light personal use, but unsuitable as the sole production geocoder from cloud hosts
- Structured `city` + `country` queries are fine when the instance cooperates

**Why Open-Meteo / Photon first?**

- Explicitly usable as HTTP APIs from servers
- Still free for this project’s scope
- Avoid stacking a second paid vendor

### 4.2 Offline path

1. Normalize and match against `backend/app/data/cities_offline.json`  
2. Prefer recomputing timezone from stored lat/lon via timezonefinder when possible  
3. Return confidence `high`/`medium` based on match strictness  

**Why a curated catalog instead of shipping all of GeoNames?**

| Approach | Tradeoff |
| --- | --- |
| Full GeoNames dump | Huge download, licensing/ops complexity for a small app |
| Empty offline mode | App becomes useless offline |
| **Curated major cities (~100)** (chosen) | Tiny, readable, good demo coverage, easy to extend |

This is an explicit YAGNI choice: expand the JSON when real usage demands it.

### 4.3 `prefer_source` modes

- `auto` — online then offline (product default)  
- `online` — fail closed if geocoding fails (useful for testing)  
- `offline` — skip network (useful on planes / demos)  

Exposing the mode in the UI makes the architecture teachable, not magical.

---

## 5. Python timezone libraries: zoneinfo first, pytz second

### Decision

For **new** code on Python 3.9+, recommend:

```python
from zoneinfo import ZoneInfo
```

and depend on `tzdata` so Windows hosts have an up-to-date IANA database.

Still return `pytz` usage in the payload for migration and comparison.

### Rationale

- `zoneinfo` is in the standard library; it is the direction of the ecosystem.  
- `pytz` historically had subtle localization pitfalls (`localize` vs replace `tzinfo`) that confuse beginners.  
- Showing both in the UI reduces “Stack Overflow says pytz” friction while steering people correctly.

### Alternatives considered

| Library | Why not primary |
| --- | --- |
| `pytz` only | Discouraged for new code |
| `dateutil.tz` | Useful, but IANA story is less direct for this teaching goal |
| Hard-code offsets | Wrong under DST |

---

## 6. Backend framework choice (FastAPI)

**Chosen:** FastAPI + Pydantic v2 + Uvicorn  

**Why**

- Automatic OpenAPI docs at `/docs` help non-authors explore the API  
- Typed request/response models document the contract in code  
- Async-friendly HTTP client (`httpx`) for Nominatim  

**Rejected for this size**

- Django: heavier than needed  
- Flask alone: fine, but we wanted first-class schema/docs with less glue  
- Serverless-only: cold starts + local offline story more awkward for beginners  

Default bind port **8001** avoids colliding with the common `8000` occupation on developer machines.

---

## 7. Frontend choice (React + Vite)

**Chosen:** Vite React app with a single main view (`App.jsx`)  

**Why**

- Fast local DX and simple production build  
- Enough structure for a polished responsive UI without a large design system  
- Dev proxy (`vite.config.js`) forwards `/api` → backend, so the browser stays same-origin during development  

**Responsive design principles applied**

- Fluid type (`clamp`) and padding  
- Single-column layout under ~960px  
- Minimum ~44px touch targets  
- `font-size: 16px` on inputs to prevent iOS focus zoom  
- `viewport-fit=cover` + safe-area insets for notched phones  
- `prefers-reduced-motion` disables decorative animations  

**Why not Next.js / a component library?**

Overkill for one primary workflow (lookup → result). Extra framework surface area would slow down a friend trying to learn the timezone pipeline.

---

## 8. Data flow & trust boundaries

```text
Browser
  └─► POST /api/resolve {city, country, prefer_source}
        └─► (optional) Nominatim HTTPS
        └─► local timezonefinder dataset
        └─► local cities_offline.json
        └─► stdlib zoneinfo (+ tzdata) / pytz
```

Trust notes:

- The browser never talks to Nominatim directly (keeps User-Agent and error handling centralized).  
- Offline data is static and reviewable in git.  
- No secrets are required for the default paths.

---

## 9. Error handling philosophy

- Domain failures become `ResolveError` with intentional HTTP status codes (`400`, `404`, `502`).  
- Online HTTP failures in `auto` mode **degrade** to offline instead of hard-failing whenever possible.  
- We avoid blanket `try/except` that swallows bugs; geocoding network errors are caught narrowly.

---

## 10. What we consciously did *not* build (yet)

These are reasonable future features — omitted to keep the first version teachable:

- Authentication / multi-user history  
- Redis/cache layer for Nominatim responses  
- Full world city database  
- Production Docker/Compose (easy to add later)  
- Hosted free-tier deploy config (Render/Fly) — discussed separately; not required for local sharing  

If you add hosting later, the cleanest shape is still **one backend that also serves `frontend/dist`**, so friends get a single URL.

---

## 11. Extending the system safely

| Goal | Suggested change |
| --- | --- |
| More offline cities | Append entries to `cities_offline.json` with lat/lon/timezone |
| Different geocoder | Swap `nominatim.py`; keep returning lat/lon into timezonefinder |
| Drop pytz | Remove from `library_bridge.py` + UI card once callers migrate |
| Stricter Nominatim usage | Add caching + inter-request delay |

Keep the **IANA id** as the external contract so clients do not churn.

---

## 12. Summary of major decisions

1. **Separate API and UI** for reuse and clarity.  
2. **IANA ids** as the only timezone answer format.  
3. **Free Nominatim + local timezonefinder** instead of paid APIs.  
4. **Small offline catalog** for resilience, not global completeness.  
5. **`zoneinfo`/`tzdata` first**, `pytz` as compatibility.  
6. **Responsive React UI** optimized for real mobile browsers.  
7. **Documentation-first** so a friend can clone, run, and understand without a walkthrough call.

When in doubt, prefer the smallest change that preserves the IANA contract and the online→offline degradation story.
