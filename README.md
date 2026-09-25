# City Timezone Mapper

[![License: MIT](https://img.shields.io/badge/License-MIT-0F3D3E.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-1a5c5e.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/API-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

**Resolve a city and country to an [IANA timezone id](https://www.iana.org/time-zones)** (for example `Asia/Tokyo` or `America/New_York`), then consume that id with Python’s modern timezone stack — `zoneinfo` and `tzdata` on Python 3.9+ — with optional `pytz` compatibility snippets.

| | |
| --- | --- |
| **Repository** | https://github.com/Jayaram-Nambiar/CityTimeZoneMapper |
| **License** | [MIT](LICENSE) (attribution required — keep the copyright notice) |
| **Third-party notices** | [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) |

---

## Features

- **Online geocoding chain** designed for cloud hosts: Open-Meteo → Photon → Nominatim (last resort), then **timezonefinder** for lat/lon → IANA id
- **Offline fallback** via a bundled major-city catalog when upstream geocoders are unavailable
- **OpenAPI contracts** for programmatic clients (`/docs`, `/redoc`, `/openapi.json`)
- **Responsive React UI** (desktop and mobile browsers)
- **Single-container deploy** (Dockerfile + optional Render Blueprint)

No commercial timezone API keys are required for the default path.

---

## Architecture (summary)

```text
City + Country
      │
      ▼
 prefer_source = auto | online | offline
      │
      ├─ online ──► Open-Meteo / Photon / Nominatim ──► timezonefinder ──► IANA id
      │
      └─ offline ─► cities_offline.json (+ timezonefinder) ─────────────► IANA id
                                                                              │
                                                                              ▼
                                                         zoneinfo (+ tzdata) / pytz mapping
```

**Why not Nominatim alone?** The public Nominatim instance often rate-limits or blocks datacenter IPs. Lookups that succeed on a laptop can fail on hosts such as Render. The multi-provider chain addresses that failure mode; the offline catalog is a final fallback, not the primary design.

Deeper rationale: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## Quick start

### Prerequisites

| Tool | Version |
| --- | --- |
| Python | 3.9+ (tested on 3.11) |
| Node.js | 18+ (tested on 24) |
| Git | recent |

### 1. Clone

```bash
git clone https://github.com/Jayaram-Nambiar/CityTimeZoneMapper.git
cd CityTimeZoneMapper
```

### 2. Backend

```bash
cd backend
python -m venv .venv

# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

- API docs: http://127.0.0.1:8001/docs  
- OpenAPI JSON: http://127.0.0.1:8001/openapi.json  
- Health: http://127.0.0.1:8001/api/health  

### 3. Frontend (development)

```bash
cd frontend
npm install
npm run dev
```

UI: http://127.0.0.1:5173 (Vite proxies `/api` to port **8001**).

### 4. Optional production-style local run

```bash
cd frontend && npm ci && npm run build
cd ../backend && uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001 — FastAPI serves the built UI and the API from one origin.

---

## Using the application

1. Enter a **city** and **country**.
2. Choose a source: **Auto** (recommended), **Online only**, or **Offline catalog only**.
3. Resolve and copy the IANA id or the Python snippet.

### Recommended Python usage (3.9+)

```python
from zoneinfo import ZoneInfo
from datetime import datetime

tz = ZoneInfo("Asia/Tokyo")
print(datetime.now(tz))
```

On Windows (and some macOS setups without a system tz database):

```bash
pip install tzdata
```

`pytz` remains useful for legacy codebases; new code should prefer `zoneinfo`.

For hosting and production notes, see [`docs/DEPLOY.md`](docs/DEPLOY.md). For full HTTP contracts, see [`docs/API.md`](docs/API.md).

---

## API contracts (programmatic use)

| Resource | URL (local) |
| --- | --- |
| Swagger UI | http://127.0.0.1:8001/docs |
| ReDoc | http://127.0.0.1:8001/redoc |
| OpenAPI 3 JSON | http://127.0.0.1:8001/openapi.json |
| Pydantic models | [`backend/app/models.py`](backend/app/models.py) |

### `POST /api/resolve`

```json
{
  "city": "Tokyo",
  "country": "Japan",
  "prefer_source": "auto"
}
```

`prefer_source`: `auto` | `online` | `offline`

The stable field for clients is **`timezone`** (IANA id). Full field tables, errors, and client examples: [`docs/API.md`](docs/API.md).

### Example

```bash
curl -s -X POST http://127.0.0.1:8001/api/resolve \
  -H "Content-Type: application/json" \
  -d '{"city":"Tokyo","country":"Japan","prefer_source":"auto"}'
```

Sample Python consumer: [`examples/python_client_demo.py`](examples/python_client_demo.py).

---

## Project layout

```text
CityTimeZoneMapper/
├── README.md
├── LICENSE
├── THIRD_PARTY_NOTICES.md
├── SECURITY.md
├── CONTRIBUTING.md
├── Dockerfile
├── render.yaml
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── DEPLOY.md
├── backend/
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── data/cities_offline.json
│   │   └── services/
│   └── tests/
├── frontend/                 # Vite + React
└── examples/
```

---

## Verification

From `backend/` (with the virtualenv activated):

```bash
pip install -r requirements.txt -r requirements-dev.txt
python -m pytest tests/ -v
```

Frontend production build:

```bash
cd frontend
npm ci
npm run build
```

---

## Deployment

Vite is a **build tool**, not a host. Production serves the Vite build from FastAPI in one process/container.

- Guide: [`docs/DEPLOY.md`](docs/DEPLOY.md)
- Artifacts: [`Dockerfile`](Dockerfile), [`render.yaml`](render.yaml)

### Public demo URL (optional)

A community/demo instance may be available at:

`https://city-timezone-mapper.onrender.com/`

**Notes for operators**

- Free-tier hosts sleep when idle; the first request after wake can be slow.
- A public demo can be scraped or rate-limited by upstream geocoders. Keeping the demo up is optional when publishing the source: the repository is self-contained. If abuse or cost becomes an issue, take the demo down or put it behind authentication — that does **not** affect the open-source release.
- Set `CORS_ORIGINS=*` only when you intentionally expose a browser-callable public API.

---

## License and attribution

This project is released under the **MIT License**. See [`LICENSE`](LICENSE).

MIT requires that the copyright notice and permission notice be included in all copies or substantial portions of the Software. When you redistribute this project, retain:

1. [`LICENSE`](LICENSE)
2. [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) (dependency and data-provider attribution)

Suggested short credit:

> Portions © 2026 Jayaram Nambiar. City Timezone Mapper — MIT License.  
> Third-party components: see THIRD_PARTY_NOTICES.md.

---

## Security

See [`SECURITY.md`](SECURITY.md) for reporting vulnerabilities. Do not commit secrets; `.env` files are gitignored. A template is provided as [`.env.example`](.env.example).

---

## Further reading

- [`docs/API.md`](docs/API.md) — OpenAPI access and client examples  
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — design decisions  
- [`docs/DEPLOY.md`](docs/DEPLOY.md) — public hosting  
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution guidelines  
- [Python `zoneinfo`](https://docs.python.org/3/library/zoneinfo.html)  
- [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/)  
- [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api)  
