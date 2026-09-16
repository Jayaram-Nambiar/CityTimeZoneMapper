# City Time Zone Mapper

**Turn a city + country into an IANA timezone id** (for example `Asia/Tokyo`) that works cleanly with Python’s timezone libraries — especially `zoneinfo` + `tzdata` on Python 3.9+.

This repository is a small full-stack app:

- a **React** web UI for quick lookups
- a **FastAPI** backend that resolves places online (free/open-source) and falls back offline
- copy-ready Python snippets for both **modern** (`zoneinfo`) and **legacy** (`pytz`) code

Private GitHub repo: [Jayaram-Nambiar/CityTimeZoneMapper](https://github.com/Jayaram-Nambiar/CityTimeZoneMapper)

---

## Table of contents

1. [Who this is for](#1-who-this-is-for)
2. [What you get](#2-what-you-get)
3. [How a lookup works](#3-how-a-lookup-works)
4. [Prerequisites](#4-prerequisites)
5. [Clone and run locally (quick start)](#5-clone-and-run-locally-quick-start)
6. [Step-by-step setup (beginner walkthrough)](#6-step-by-step-setup-beginner-walkthrough)
7. [Using the app](#7-using-the-app)
8. [API contracts (programmatic use)](#8-api-contracts-programmatic-use)
9. [Project layout](#9-project-layout)
10. [Architecture decisions (why we built it this way)](#10-architecture-decisions-why-we-built-it-this-way)
11. [Troubleshooting](#11-troubleshooting)
12. [Further reading](#12-further-reading)
13. [Host on the public internet](#13-host-on-the-public-internet)
14. [License](#14-license)

---

## 1. Who this is for

- A friend or teammate who needs **city → timezone** resolution without buying a commercial API key
- Developers who want the result to plug into **Python** (`ZoneInfo("...")`) with minimal friction
- Anyone learning how geocoding + timezone polygons + IANA ids fit together

If you only need a **user-facing how-to**, start with [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md).  
If you want to **call the API from code**, start with [`docs/API.md`](docs/API.md).  
If you want **design rationale in depth**, read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

---

## 2. What you get

| Capability | Details |
| --- | --- |
| Online resolution | OpenStreetMap **Nominatim** (geocode city/country → lat/lon) + **timezonefinder** (lat/lon → IANA id) |
| Offline fallback | Bundled major-city catalog (`cities_offline.json`) + timezonefinder |
| Python mapping | Response includes usage for `zoneinfo`/`tzdata` (recommended) and `pytz` (legacy) |
| UI | Responsive React app (desktop + mobile browsers) |
| Docs | This README, a user guide, and an architecture note |

**No paid timezone API is required.**

---

## 3. How a lookup works

```text
City + Country
      │
      ▼
┌─────────────────────┐
│ prefer_source=auto  │  (default)
└──────────┬──────────┘
           │
     try online ──► Nominatim geocode ──► timezonefinder ──► IANA id
           │                                      │
           │ fail / no match                      │
           ▼                                      ▼
     offline catalog ──► (optional recomputed TZ) ──► IANA id
                                                      │
                                                      ▼
                                   zoneinfo + pytz mapping + local time
```

IANA ids look like `Europe/Berlin` or `America/New_York`. Those strings are the standard names Python expects.

---

## 4. Prerequisites

Install these once on your machine:

| Tool | Suggested version | Why |
| --- | --- | --- |
| [Python](https://www.python.org/downloads/) | **3.9+** (project tested on 3.11) | Backend + `zoneinfo` |
| [Node.js](https://nodejs.org/) | **18+** (tested on 24) | Frontend tooling (Vite) |
| [Git](https://git-scm.com/) | any recent | Clone the repo |
| A terminal | PowerShell, Terminal, or bash | Run commands |

Optional but useful:

- A code editor such as [VS Code](https://code.visualstudio.com/) or Cursor
- Access to the private GitHub repo (ask the owner to invite your GitHub account)

Check versions:

```bash
python --version
node --version
npm --version
git --version
```

---

## 5. Clone and run locally (quick start)

If you already know Git/Python/Node, this is enough:

```bash
git clone https://github.com/Jayaram-Nambiar/CityTimeZoneMapper.git
cd CityTimeZoneMapper
```

**Terminal A — backend**

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

**Terminal B — frontend**

```bash
cd frontend
npm install
npm run dev
```

Open:

- UI → http://127.0.0.1:5173  
- API docs → http://127.0.0.1:8001/docs  

> **Why port 8001?** Port `8000` is often already used by other local apps. This project defaults to **8001** for the API. The Vite dev server proxies `/api` to that port.

---

## 6. Step-by-step setup (beginner walkthrough)

### 6.1 Get the code

1. Accept a GitHub collaborator invite if the repo is private.
2. Clone:

```bash
git clone https://github.com/Jayaram-Nambiar/CityTimeZoneMapper.git
cd CityTimeZoneMapper
```

### 6.2 Start the backend

1. Open a terminal in the project root.
2. Move into `backend` and create an isolated Python environment (keeps dependencies tidy):

```bash
cd backend
python -m venv .venv
```

3. Activate it:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

If PowerShell blocks activation, run once (as yourself, not as admin unless required by policy):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

4. Install Python packages:

```bash
pip install -r requirements.txt
```

5. Start the API:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```

Leave this terminal open. You should see something like `Application startup complete`.

Sanity check: open http://127.0.0.1:8001/api/health — you should see JSON with `"status": "ok"`.

### 6.3 Start the frontend

1. Open a **second** terminal.
2. Install and run the UI:

```bash
cd frontend
npm install
npm run dev
```

3. Visit http://127.0.0.1:5173  

The top status line should say the API is online. If it says “Waiting for API…”, the backend is not reachable on port 8001.

### 6.4 (Optional) Try the Python example client

With the backend running:

```bash
# from project root, with httpx/tzdata/pytz available
# easiest: use the backend venv
backend\.venv\Scripts\python examples\python_client_demo.py "Bengaluru" "India" http://127.0.0.1:8001
```

---

## 7. Using the app

1. Enter a **city** (e.g. `Munich`) and **country** (e.g. `Germany`).
2. Choose a **source**:
   - **Auto** — try online first, then offline (recommended)
   - **Online only** — Nominatim + timezonefinder
   - **Offline catalog only** — bundled cities (works without internet for those cities)
3. Click **Resolve timezone**.
4. Copy the IANA id or the Python snippet you need.

For screenshots-in-words, tips, and common mistakes, see [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md).

---

## 8. API contracts (programmatic use)

The backend is a normal HTTP JSON API. The React UI is just one client — scripts, notebooks, and other services can use the same contracts.

### How to access the contracts

With the backend running on port **8001**:

| What you need | Open / fetch |
| --- | --- |
| Interactive try-it-out UI (Swagger) | http://127.0.0.1:8001/docs |
| Readable reference (ReDoc) | http://127.0.0.1:8001/redoc |
| Machine-readable OpenAPI 3 schema | http://127.0.0.1:8001/openapi.json |
| Source-of-truth Pydantic models | [`backend/app/models.py`](backend/app/models.py) |

Download the schema for codegen or Postman/Insomnia import:

```bash
curl -o openapi.json http://127.0.0.1:8001/openapi.json
```

Full field tables, error codes, and Python / JavaScript / curl examples: **[`docs/API.md`](docs/API.md)**.

### Endpoints (summary)

#### `GET /api/health`

Returns service status, Python version, whether `zoneinfo`/`tzdata` are available, and offline city count.

#### `POST /api/resolve`

Request body:

```json
{
  "city": "Tokyo",
  "country": "Japan",
  "prefer_source": "auto"
}
```

`prefer_source`: `auto` | `online` | `offline`

Successful responses include:

- `timezone` — IANA id (the stable value to store and pass to `ZoneInfo(...)`)
- `source` — `online` or `offline`
- `coordinates` — when available
- `libraries` — `zoneinfo` / `pytz` guidance plus current local time

Example with curl (Git Bash / macOS / Linux):

```bash
curl -X POST http://127.0.0.1:8001/api/resolve \
  -H "Content-Type: application/json" \
  -d '{"city":"Tokyo","country":"Japan","prefer_source":"auto"}'
```

PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8001/api/resolve `
  -ContentType "application/json" `
  -Body '{"city":"Tokyo","country":"Japan","prefer_source":"auto"}'
```

Ready-made Python client sample: [`examples/python_client_demo.py`](examples/python_client_demo.py).

---

## 9. Project layout

```text
CityTimeZoneMapper/
├── README.md
├── LICENSE
├── Dockerfile                ← production image (UI build + API)
├── render.yaml               ← free Render Blueprint
├── docs/
│   ├── API.md
│   ├── USER_GUIDE.md
│   ├── ARCHITECTURE.md
│   └── DEPLOY.md             ← public hosting walkthrough
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py           ← API + serves frontend/dist in production
│       ├── models.py
│       ├── data/cities_offline.json
│       └── services/
├── frontend/                 ← Vite/React (dev server or production build)
└── examples/
    └── python_client_demo.py
```
---

## 10. Architecture decisions (why we built it this way)

Short version below; full discussion is in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

| Decision | Rationale |
| --- | --- |
| **FastAPI + React** | Clear split: JSON API for machines, polished UI for humans. Easy to call from Python scripts too. |
| **IANA timezone ids as the contract** | Portable across `zoneinfo`, `pytz`, Java, databases, calendars. |
| **Nominatim (free) + timezonefinder** | Avoid paid keys; use open geocoding then local TZ polygons. |
| **Offline city catalog fallback** | App still useful when the network or Nominatim is unavailable. |
| **`zoneinfo` + `tzdata` preferred over `pytz`** | Official recommendation for new Python 3.9+ code; `pytz` kept for migration/comparison. |
| **Vite proxy in development** | Browser calls `/api/...` same-origin; no CORS pain during local work. |
| **Responsive mobile-first CSS** | Friend may open the UI on a phone; touch targets, safe areas, and no iOS input zoom. |

---

## 11. Troubleshooting

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Browser `ERR_CONNECTION_REFUSED` on `:5173` | Frontend not running | `cd frontend && npm run dev` |
| UI says “Waiting for API…” | Backend down or wrong port | Start uvicorn on **8001**; check `/api/health` |
| `Address already in use` on 8001 | Another process owns the port | Stop that process or change both uvicorn port and `frontend/vite.config.js` proxy target |
| Online lookups fail, offline works | Network / Nominatim rate limit | Retry later, or use **Offline catalog only** for major cities |
| `ZoneInfoNotFoundError` in your own script | Missing tz database on Windows | `pip install tzdata` |
| PowerShell won’t activate `.venv` | Execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Clone denied | Private repo access | Ask owner to add your GitHub user as collaborator |

---

## 12. Further reading

- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — end-user guide  
- [`docs/API.md`](docs/API.md) — OpenAPI contracts + programmatic clients  
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — deeper design rationale  
- [`docs/DEPLOY.md`](docs/DEPLOY.md) — public hosting (Render / Docker)  
- Live Swagger UI (backend running): http://127.0.0.1:8001/docs  
- OpenAPI JSON: http://127.0.0.1:8001/openapi.json  
- [Python `zoneinfo`](https://docs.python.org/3/library/zoneinfo.html)  
- [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/)  
- [timezonefinder](https://timezonefinder.readthedocs.io/)

---

## 13. Host on the public internet

Vite does **not** host websites. This repo is set up so a **Vite production build** is served by FastAPI in one container — one public URL for humans and for API clients.

**Fastest free path:** deploy the included [`render.yaml`](render.yaml) + [`Dockerfile`](Dockerfile) on [Render](https://render.com)’s free tier.

Step-by-step: **[`docs/DEPLOY.md`](docs/DEPLOY.md)**

After deploy, share:

- App UI → `https://<your-service>.onrender.com/`
- API docs → `https://<your-service>.onrender.com/docs`
- OpenAPI → `https://<your-service>.onrender.com/openapi.json`

---

## 14. License

MIT — see [`LICENSE`](LICENSE).
