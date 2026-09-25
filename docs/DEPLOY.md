# Deploy City Timezone Mapper (public internet access)

**Important:** Vite is a **build tool**, not a hosting provider. You cannot “host on Vite.”  
This project builds the UI with Vite, then serves that build **together with the API** from one public URL.

## Recommended free host: Render

One Docker service = UI + API + `/docs` + `/openapi.json`.

### One-time setup (about 5–10 minutes)

1. Push the latest `main` branch to GitHub (already done if you followed the repo setup).
2. Open [Render](https://render.com) and sign up / log in (GitHub login is easiest).
3. Click **New** → **Blueprint**.
4. Connect the GitHub repo `Jayaram-Nambiar/CityTimeZoneMapper` (authorize Render if asked).
5. Render reads [`render.yaml`](../render.yaml) and creates a **free** web service.
6. Click **Apply** / **Deploy**.
7. When the deploy is live, open the service URL, for example:

   `https://city-timezone-mapper.onrender.com`

Anyone with that link can use the app. API contracts stay at:

| Resource | Path |
| --- | --- |
| UI | `/` |
| Swagger | `/docs` |
| OpenAPI JSON | `/openapi.json` |
| Health | `/api/health` |
| Resolve | `POST /api/resolve` |

### Free-tier notes

- The free instance **sleeps after idle**. The first visit after a nap can take ~30–60 seconds.
- Online geocoding uses **Open-Meteo → Photon → Nominatim**. Public Nominatim alone often fails from cloud IPs (the usual “works on my laptop” trap); the multi-provider chain is the real fix.
- Offline catalog remains a last resort for major cities when every online provider is unreachable.
- Keep the GitHub repository private or public as you prefer; Render can deploy either after you grant access.
- If the repository is public, consider whether a long-lived public demo URL is worth the abuse/rate-limit risk. Taking the demo down does not affect the open-source release.

### Redeploy after changes

Push to `main`. If auto-deploy is enabled, Render rebuilds. Otherwise click **Manual Deploy** in the Render dashboard.

---

## Alternative hosts (same Docker image)

The root [`Dockerfile`](../Dockerfile) also works on:

- [Railway](https://railway.app) — New Project → Deploy from GitHub / Dockerfile  
- [Fly.io](https://fly.io) — `fly launch` in the repo root  
- [Google Cloud Run](https://cloud.google.com/run) — build & deploy the container  

Set env `CORS_ORIGINS=*` (default in the Dockerfile) for public browser + API access.

---

## Local production check (optional)

Build the UI, then serve everything from FastAPI:

```bash
cd frontend
npm ci
npm run build

cd ../backend
.\.venv\Scripts\activate   # Windows
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001 — you should see the UI (not only JSON).

Or with Docker:

```bash
docker build -t city-timezone-mapper .
docker run --rm -p 8001:8001 city-timezone-mapper
```

---

## What not to do

| Approach | Why it fails for this app |
| --- | --- |
| Host only on Vite / “Vite hosting” | Does not exist as a product |
| GitHub Pages / static-only host | Serves the UI but **cannot** run FastAPI |
| Sharing `localhost:5173` | Only works on your machine |

---

## After you have a public URL

1. Share the Render URL with your friend.  
2. Point them at `/docs` for programmatic use.  
3. Optionally add that origin to any extra allow-lists if you later tighten `CORS_ORIGINS`.  
