# API contracts — programmatic use

City Time Zone Mapper exposes a small **HTTP JSON API**. The UI is only one client; any language that can make HTTP requests can use the same contracts.

Base URL when running locally:

```text
http://127.0.0.1:8001
```

Start the backend first (`uvicorn` on port **8001**). See the root [`README.md`](../README.md) if you have not set that up yet.

---

## 1. Where to find the official contracts

FastAPI publishes the API contract automatically from the Pydantic models in `backend/app/models.py`.

| Resource | URL (local) | What it is |
| --- | --- | --- |
| **Swagger UI** | http://127.0.0.1:8001/docs | Interactive explorer — try requests in the browser |
| **ReDoc** | http://127.0.0.1:8001/redoc | Readable reference documentation |
| **OpenAPI JSON** | http://127.0.0.1:8001/openapi.json | Machine-readable OpenAPI 3 schema (codegen / clients) |
| **Source models** | `backend/app/models.py` | Canonical request/response types in code |

### Download the OpenAPI schema

```bash
curl -o openapi.json http://127.0.0.1:8001/openapi.json
```

PowerShell:

```powershell
Invoke-WebRequest http://127.0.0.1:8001/openapi.json -OutFile openapi.json
```

You can feed `openapi.json` into generators (OpenAPI Generator, `openapi-typescript`, Insomnia/Postman import, etc.).

### Generate a typed client (optional)

Example with [openapi-python-client](https://github.com/openapi-generators/openapi-python-client) once the backend is running:

```bash
pip install openapi-python-client
openapi-python-client generate --url http://127.0.0.1:8001/openapi.json
```

---

## 2. Endpoints

### `GET /`

Service index (human-readable pointers to docs and routes).

### `GET /api/health`

Liveness / dependency check.

**Response (`HealthResponse`)**

| Field | Type | Meaning |
| --- | --- | --- |
| `status` | string | `"ok"` when healthy |
| `python_version` | string | Runtime version |
| `zoneinfo_available` | boolean | Stdlib `zoneinfo` importable |
| `tzdata_available` | boolean | `tzdata` package importable |
| `offline_cities` | integer | Size of offline catalog |
| `server_time_utc` | datetime (ISO-8601) | Server clock in UTC |

### `POST /api/resolve`

Resolve `city` + `country` to an IANA timezone id and library mapping.

**Request (`ResolveRequest`)** — JSON body:

| Field | Type | Required | Default | Notes |
| --- | --- | --- | --- | --- |
| `city` | string (1–120) | yes | — | e.g. `"Tokyo"` |
| `country` | string (1–120) | yes | — | e.g. `"Japan"` |
| `prefer_source` | `"auto"` \| `"online"` \| `"offline"` | no | `"auto"` | Resolution strategy |

**Response (`ResolveResponse`)**

| Field | Type | Meaning |
| --- | --- | --- |
| `city` | string | Echo of input city |
| `country` | string | Echo of input country |
| `matched_name` | string \| null | Best matched place label |
| `timezone` | string | **IANA id** (primary contract), e.g. `Asia/Tokyo` |
| `coordinates` | object \| null | `{ "latitude": number, "longitude": number }` |
| `source` | `"online"` \| `"offline"` | Which path produced the answer |
| `confidence` | `"high"` \| `"medium"` \| `"low"` | Match quality hint |
| `libraries` | object | Python consumption helpers (see below) |
| `notes` | string[] | Human-readable resolution notes |

**`libraries` (`TimeLibraryMapping`)**

| Field | Type | Meaning |
| --- | --- | --- |
| `iana_id` | string | Same as `timezone` |
| `zoneinfo` | object | Recommended import/usage notes for `zoneinfo` |
| `pytz` | object | Legacy import/usage notes for `pytz` |
| `current_local_time_iso` | string | Local time at resolve moment (ISO-8601) |
| `utc_offset` | string | e.g. `+09:00` |
| `is_dst` | boolean | Whether DST appears active at that moment |

### Error shape

Failures return JSON:

```json
{ "detail": "Human-readable error message" }
```

Typical HTTP statuses:

| Status | When |
| --- | --- |
| `400` | Invalid input / unknown timezone id while mapping |
| `404` | Place could not be resolved |
| `502` | Online-only mode and upstream geocoding failed |

---

## 3. Minimal programmatic examples

### Python (`httpx`)

```python
import httpx
from zoneinfo import ZoneInfo
from datetime import datetime

BASE = "http://127.0.0.1:8001"

with httpx.Client(timeout=20.0) as client:
    health = client.get(f"{BASE}/api/health")
    health.raise_for_status()

    response = client.post(
        f"{BASE}/api/resolve",
        json={
            "city": "Bengaluru",
            "country": "India",
            "prefer_source": "auto",
        },
    )
    response.raise_for_status()
    data = response.json()

iana = data["timezone"]  # e.g. "Asia/Kolkata"
print(iana)
print(datetime.now(ZoneInfo(iana)).isoformat())
```

A fuller CLI sample ships at [`examples/python_client_demo.py`](../examples/python_client_demo.py).

### JavaScript / Node (`fetch`)

```js
const BASE = "http://127.0.0.1:8001";

const response = await fetch(`${BASE}/api/resolve`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    city: "Munich",
    country: "Germany",
    prefer_source: "auto",
  }),
});

if (!response.ok) {
  const err = await response.json();
  throw new Error(err.detail || response.statusText);
}

const data = await response.json();
console.log(data.timezone); // e.g. "Europe/Berlin"
```

### curl

```bash
curl -s http://127.0.0.1:8001/api/health

curl -s -X POST http://127.0.0.1:8001/api/resolve \
  -H "Content-Type: application/json" \
  -d '{"city":"Tokyo","country":"Japan","prefer_source":"auto"}'
```

### PowerShell

```powershell
Invoke-RestMethod http://127.0.0.1:8001/api/health

Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8001/api/resolve `
  -ContentType "application/json" `
  -Body '{"city":"Tokyo","country":"Japan","prefer_source":"auto"}'
```

---

## 4. Integration tips

1. **Treat `timezone` as the stable contract.** Persist/pass that IANA string; rebuild local times with `zoneinfo` in your app.  
2. **Call `/api/health` before batches** if you are wiring automation.  
3. **Prefer `prefer_source: "auto"`** unless you are deliberately testing one path.  
4. **Be gentle with online mode** — Nominatim is a shared community service. Cache repeated city/country pairs in your own code when possible.  
5. **CORS** is enabled for local Vite origins (`5173` / `4173`). Browser apps on other origins may need the backend CORS allow-list updated in `backend/app/main.py`. Server-to-server clients are unaffected.  
6. **Codegen from `/openapi.json`** if you want typed SDKs instead of hand-written HTTP calls.

---

## 5. Related docs

- Setup: [`README.md`](../README.md)  
- End-user UI: [`USER_GUIDE.md`](USER_GUIDE.md)  
- Design rationale: [`ARCHITECTURE.md`](ARCHITECTURE.md)  
