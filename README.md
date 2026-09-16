# City Time Zone Mapper

Resolve a **city + country** to an **IANA timezone id** (for example `Asia/Tokyo`), then map that id into Python's timezone libraries.

## What it does

1. **Online path (free/open-source):** [OpenStreetMap Nominatim](https://nominatim.org/) geocodes the place → [timezonefinder](https://github.com/jannikmi/timezonefinder) converts lat/lon to an IANA id.
2. **Offline fallback:** a bundled major-city catalog + timezonefinder, used automatically when Nominatim is unavailable or returns no match.
3. **Python mapping:** responses include ready-to-use guidance for:
   - `zoneinfo` + `tzdata` (**recommended** for Python 3.9+)
   - `pytz` (legacy / compatibility)

## Stack

| Layer | Tech |
| --- | --- |
| Backend | FastAPI, httpx, timezonefinder, tzdata, pytz |
| Frontend | React + Vite |
| Output | IANA timezone strings consumable by `ZoneInfo("...")` |

## Quick start

### Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

API docs: http://127.0.0.1:8001/docs

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://127.0.0.1:5173 (proxies `/api` to the backend)

### Example API call

```bash
curl -X POST http://127.0.0.1:8001/api/resolve \
  -H "Content-Type: application/json" \
  -d "{\"city\":\"Tokyo\",\"country\":\"Japan\",\"prefer_source\":\"auto\"}"
```

`prefer_source` accepts `auto` | `online` | `offline`.

### Python client demo

With the API running:

```bash
pip install httpx tzdata pytz
python examples/python_client_demo.py "Bengaluru" "India" http://127.0.0.1:8001
```

## Why zoneinfo instead of pytz?

For new code on Python 3.9+, the standard library `zoneinfo` module is the recommended approach. Install `tzdata` so Windows (and some macOS setups) have a current IANA database:

```python
from zoneinfo import ZoneInfo
from datetime import datetime

tz = ZoneInfo("America/New_York")
print(datetime.now(tz))
```

`pytz` remains useful for older codebases; this project surfaces both so you can migrate deliberately.

## Project layout

```
backend/app/           FastAPI app, services, offline city data
frontend/src/          React UI
examples/              Sample Python consumer
```

## Notes

- Nominatim is a shared community service: keep a descriptive User-Agent, avoid bulk scraping, and prefer caching for production workloads.
- The offline catalog covers major cities; obscure places are better served by the online path.
- No commercial timezone API keys are required.

## License

MIT
