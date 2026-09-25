# Third-Party Notices

This file lists third-party software and data used by **City Timezone Mapper**,
and the attribution / license conditions that apply when you redistribute this
project. Preserve these notices when you redistribute substantial portions of
the Software (MIT) **and** when you redistribute the listed third-party works
under their own terms.

Project license: see [`LICENSE`](LICENSE) (MIT © 2026 Jayaram Nambiar).

---

## Application dependencies (Python)

| Package | Typical license | Upstream |
| --- | --- | --- |
| FastAPI | MIT | https://github.com/fastapi/fastapi |
| Starlette (via FastAPI) | BSD-3-Clause | https://github.com/encode/starlette |
| Uvicorn | BSD-3-Clause | https://github.com/encode/uvicorn |
| HTTPX | BSD-3-Clause | https://github.com/encode/httpx |
| Pydantic | MIT | https://github.com/pydantic/pydantic |
| timezonefinder | MIT | https://github.com/jannikmi/timezonefinder |
| tzdata | Apache-2.0 | https://github.com/python/tzdata |
| pytz | MIT | https://github.com/stub42/pytz |
| python-multipart | Apache-2.0 | https://github.com/Kludex/python-multipart |

Exact installed versions are recorded in your local environment after
`pip install -r backend/requirements.txt`. License metadata may be empty in
some package distributions; upstream repositories remain authoritative.

---

## Application dependencies (JavaScript / frontend)

| Package | Typical license | Upstream |
| --- | --- | --- |
| React | MIT | https://github.com/facebook/react |
| React DOM | MIT | https://github.com/facebook/react |
| Vite | MIT | https://github.com/vitejs/vite |
| @vitejs/plugin-react | MIT | https://github.com/vitejs/vite-plugin-react |

---

## Runtime / online data services

These services are queried at runtime. They are **not** vendored into this
repository. Follow each provider’s usage policy and attribution rules.

### Open-Meteo Geocoding API

- Site: https://open-meteo.com/
- Docs: https://open-meteo.com/en/docs/geocoding-api
- Location data is based on **GeoNames**. Respect Open-Meteo’s terms of use
  (non-commercial free tier vs commercial offerings).

### Photon (Komoot)

- API: https://photon.komoot.io/
- Built on OpenStreetMap data. OpenStreetMap data is available under the
  **Open Database License (ODbL)** by the OpenStreetMap Foundation.
  https://www.openstreetmap.org/copyright

### Nominatim (OpenStreetMap)

- Public instance: https://nominatim.openstreetmap.org/
- Usage policy: https://operations.osmfoundation.org/policies/nominatim/
- OSM data © OpenStreetMap contributors, ODbL.

### IANA Time Zone Database

- Consumed via Python `zoneinfo` and/or the `tzdata` / `pytz` packages.
- Upstream: https://www.iana.org/time-zones

### timezonefinder polygon data

- Bundled/used by the `timezonefinder` package (MIT). See that project for
  dataset provenance.

---

## Bundled offline city catalog

`backend/app/data/cities_offline.json` is a curated list of major cities
(coordinates + IANA timezone ids) assembled for offline fallback. It is not a
complete dump of GeoNames or OSM. City names and coordinates are factual
reference data; timezone ids follow the IANA tz database naming.

---

## Fonts (frontend CDN)

The UI loads **Fraunces** and **Sora** from Google Fonts in `frontend/index.html`.
Those font families are licensed under the SIL Open Font License (OFL). If you
self-host fonts instead of using the Google Fonts CDN, retain the OFL notices
that ship with the font files.

---

## How to attribute this project (MIT)

When you redistribute this software (source or substantial portions), include:

1. The copyright notice and permission text from [`LICENSE`](LICENSE)
2. This `THIRD_PARTY_NOTICES.md` file (or an equivalent summary of third-party terms)

Suggested short attribution in your own README or About screen:

> Portions © 2026 Jayaram Nambiar. City Timezone Mapper is available under the MIT License.
> Third-party components and data providers are listed in THIRD_PARTY_NOTICES.md.
