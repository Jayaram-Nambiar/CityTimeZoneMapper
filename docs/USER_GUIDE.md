# User Guide — City Time Zone Mapper

This guide is for **people using the app**, not just developers. It explains what the tool does, how to run a lookup, how to read the results, and how to use those results in Python.

If you need to install the project from scratch, follow the **Clone and run locally** section in the root [`README.md`](../README.md).

---

## 1. What this app solves

You know a **city** and its **country**, and you need the correct **timezone name** for that place — the kind of name Python libraries understand, such as:

- `Asia/Kolkata`
- `America/New_York`
- `Europe/Berlin`

Those names are called **IANA timezone ids** (sometimes people say “Olson” or “tz database” names). They are better than saying “UTC+5:30” alone, because they also encode **daylight saving rules** over time.

---

## 2. Before you start

You need both parts running on your computer (or a shared host, if one is set up later):

1. **Backend API** on http://127.0.0.1:8001  
2. **Frontend UI** on http://127.0.0.1:5173  

Check the status line under the logo:

- **API online** → you are good to look up cities  
- **Waiting for API…** → start the backend first (see the README)

On a phone browser pointed at your machine, the page is designed to reflow: large tap targets, readable type, and no awkward horizontal scrolling for the main flow.

---

## 3. Your first lookup (2 minutes)

1. Open http://127.0.0.1:5173  
2. Type a city, for example `Tokyo`  
3. Type a country, for example `Japan`  
4. Leave **Source** on **Auto (online, then offline)**  
5. Tap **Resolve timezone**

You should see:

- a matched place name  
- an IANA timezone such as `Asia/Tokyo`  
- the current local time there  
- Python snippets you can copy  

### Try sample chips

Under the form, tap a ready-made example (`Tokyo`, `São Paulo`, `Bengaluru`, `Vancouver`). This fills the fields so you can resolve immediately.

---

## 4. Choosing a lookup source

| Option | When to use it |
| --- | --- |
| **Auto** | Everyday use. Tries the free online path first; if that fails, uses the offline catalog. |
| **Online only** | You want the freshest geocoding from OpenStreetMap for less common places. Needs internet. |
| **Offline catalog only** | No internet, or Nominatim is slow/blocked. Works well for major cities in the bundled list. |

### What “online” really means

1. Ask **Nominatim** (OpenStreetMap) for coordinates of that city/country.  
2. Ask **timezonefinder** (local library, no paid key) which timezone polygon contains those coordinates.  

### What “offline” really means

1. Match your city/country against a **bundled JSON list** of major cities.  
2. Confirm/compute the timezone with timezonefinder when coordinates exist.  

Offline is **not** every village on Earth — that is intentional, to keep the project light and free of huge databases.

---

## 5. Reading the results panel

### Matched name

The place the system believes you meant (from Nominatim’s display name, or from the offline catalog).

### Source badge

- **online** — resolved via Nominatim + timezonefinder  
- **offline** — resolved via the bundled catalog  

### Confidence badge

- **high** — strong name/country match (especially offline exact matches, or a clear online hit)  
- **medium** — partial / fuzzy offline match; double-check spelling if something looks off  

### IANA timezone

This is the main answer. Example: `Europe/Berlin`.

Use **Copy** to put it on the clipboard.

### Local now / UTC offset / DST

Shows an approximate “what time is it there right now”, the UTC offset string, and whether daylight saving is active at that moment.

### Coordinates

Latitude/longitude used for the timezone polygon lookup (when available).

### Python cards

Two cards appear:

1. **zoneinfo + tzdata** — **Recommended** for new Python 3.9+ projects  
2. **pytz** — labeled **Legacy**, kept so older tutorials and codebases still map cleanly  

Tap **Copy snippet** and paste into your editor.

---

## 6. Using the result in Python (beginner)

### Recommended (modern)

```python
from zoneinfo import ZoneInfo
from datetime import datetime

tz = ZoneInfo("Asia/Tokyo")  # paste your IANA id here
print(datetime.now(tz))
```

On Windows (and some Mac setups), also install the timezone database package once:

```bash
pip install tzdata
```

### Legacy (pytz)

```python
import pytz
from datetime import datetime

tz = pytz.timezone("Asia/Tokyo")
print(datetime.now(tz))
```

You usually do **not** need both in new code. Prefer `zoneinfo`.

---

## 7. Tips for better matches

- Prefer the common English (or local) city spelling: `Munich` / `München` often both work online; offline may only list one spelling.  
- Put the country clearly: `India`, not only a state name.  
- ISO-ish country codes often work offline too (`in`, `us`, `jp`) because the catalog stores `country_code`.  
- If Auto fails for a small town, try Online only, or geocode manually and reason from coordinates.  
- Be kind to Nominatim: it is a shared free service — avoid hammering it with bulk scripts.

---

## 8. Mobile browser notes

The UI is built to work on modern mobile browsers (Safari iOS, Chrome Android, etc.):

- layout stacks into a single column on narrow screens  
- buttons/inputs are large enough for thumbs  
- input text is sized to avoid iOS zoom-on-focus quirks  
- long timezone ids wrap instead of overflowing  
- code blocks scroll horizontally inside their card if needed  

If you are testing from a phone against a PC running the app, both devices must reach the host (same LAN / correct IP). `127.0.0.1` on a phone refers to the **phone itself**, not your laptop — use your laptop’s LAN IP for remote testing, or run both sides on the same device.

---

## 9. Common problems

| What you see | What to do |
| --- | --- |
| Connection refused on the UI URL | Start the frontend (`npm run dev` in `frontend`). |
| “Waiting for API…” | Start the backend on port 8001. |
| “Could not resolve timezone…” | Check spelling; try Auto; try a larger nearby city; try Online only. |
| Online fails repeatedly | Network or Nominatim limits — use Offline for major cities. |
| Copy button fails | Select the text manually; some browsers restrict clipboard outside secure contexts. |

---

## 10. Privacy & fairness (plain language)

- Lookups you type are sent to **your local backend**.  
- In **online** mode, the backend asks **Nominatim** for geocoding (subject to their public usage policy).  
- No commercial API key is stored in this project for timezone lookup.  
- Do not use the public Nominatim endpoint for heavy batch jobs.

---

## 11. Where to go next

- Install & develop: [`README.md`](../README.md)  
- Call the API from code (OpenAPI / examples): [`API.md`](API.md)  
- Why the system is designed this way: [`ARCHITECTURE.md`](ARCHITECTURE.md)  
- Live API explorer (when backend is running): http://127.0.0.1:8001/docs  
- Raw OpenAPI schema: http://127.0.0.1:8001/openapi.json  
- Alternate readable docs: http://127.0.0.1:8001/redoc  
