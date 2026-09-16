import { useEffect, useState } from "react";

const EXAMPLES = [
  { city: "Tokyo", country: "Japan" },
  { city: "São Paulo", country: "Brazil" },
  { city: "Bengaluru", country: "India" },
  { city: "Vancouver", country: "Canada" },
];

function formatClock(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return new Intl.DateTimeFormat(undefined, {
    weekday: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    timeZoneName: "short",
  }).format(d);
}

export default function App() {
  const [city, setCity] = useState("");
  const [country, setCountry] = useState("");
  const [preferSource, setPreferSource] = useState("auto");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const [health, setHealth] = useState(null);
  const [copied, setCopied] = useState("");

  useEffect(() => {
    fetch("/api/health")
      .then((r) => (r.ok ? r.json() : null))
      .then(setHealth)
      .catch(() => setHealth(null));
  }, []);

  async function onSubmit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    setCopied("");

    try {
      const response = await fetch("/api/resolve", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          city: city.trim(),
          country: country.trim(),
          prefer_source: preferSource,
        }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Lookup failed");
      }
      setResult(payload);
    } catch (err) {
      setError(err.message || "Unable to resolve timezone");
    } finally {
      setLoading(false);
    }
  }

  async function copyText(label, value) {
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(value);
      } else {
        const area = document.createElement("textarea");
        area.value = value;
        area.setAttribute("readonly", "");
        area.style.position = "fixed";
        area.style.left = "-9999px";
        document.body.appendChild(area);
        area.select();
        document.execCommand("copy");
        document.body.removeChild(area);
      }
      setCopied(label);
      window.setTimeout(() => setCopied(""), 1600);
    } catch {
      setError("Copy failed — select the text manually instead.");
    }
  }

  return (
    <div className="page">
      <div className="atmosphere" aria-hidden="true" />
      <header className="topbar">
        <div className="brand-mark" aria-hidden="true">
          <span className="hand" />
        </div>
        <div>
          <p className="eyebrow">City → IANA → Python</p>
          <p className="status-line">
            {health ? (
              <>
                <span className="status-short">
                  API online · {health.offline_cities} cities
                </span>
                <span className="status-full">
                  API online · {health.offline_cities} offline cities · zoneinfo{" "}
                  {health.zoneinfo_available ? "ready" : "missing"}
                </span>
              </>
            ) : (
              <>
                <span className="status-short">Waiting for API on :8001</span>
                <span className="status-full">
                  Waiting for API… start the FastAPI backend on :8001
                </span>
              </>
            )}
          </p>
        </div>
      </header>

      <main className="shell">
        <section className="hero">
          <h1 className="brand">City Timezone Mapper</h1>
          <p className="lede">
            Enter a city and country. Get an IANA timezone id ready for
            Python&nbsp;3.9+ <code>zoneinfo</code> and <code>tzdata</code>,
            with a free online path and offline fallback.
          </p>

          <form className="lookup" onSubmit={onSubmit}>
            <label className="field">
              <span>City</span>
              <input
                value={city}
                onChange={(e) => setCity(e.target.value)}
                placeholder="e.g. Munich"
                required
                autoComplete="address-level2"
                enterKeyHint="next"
                spellCheck={false}
              />
            </label>
            <label className="field">
              <span>Country</span>
              <input
                value={country}
                onChange={(e) => setCountry(e.target.value)}
                placeholder="e.g. Germany"
                required
                autoComplete="country-name"
                enterKeyHint="go"
                spellCheck={false}
              />
            </label>
            <label className="field">
              <span>Source</span>
              <select
                value={preferSource}
                onChange={(e) => setPreferSource(e.target.value)}
                aria-label="Lookup source preference"
              >
                <option value="auto">Auto (online, then offline)</option>
                <option value="online">Online only (Nominatim)</option>
                <option value="offline">Offline catalog only</option>
              </select>
            </label>
            <button className="cta" type="submit" disabled={loading}>
              {loading ? "Resolving…" : "Resolve timezone"}
            </button>
          </form>

          <div className="examples">
            {EXAMPLES.map((ex) => (
              <button
                key={`${ex.city}-${ex.country}`}
                type="button"
                className="chip"
                onClick={() => {
                  setCity(ex.city);
                  setCountry(ex.country);
                }}
              >
                {ex.city}, {ex.country}
              </button>
            ))}
          </div>
        </section>

        <section className="result-pane" aria-live="polite">
          {error && <div className="banner error">{error}</div>}

          {!result && !error && (
            <div className="placeholder">
              <p className="placeholder-title">No lookup yet</p>
              <p>
                Results include coordinates, confidence, current local time,
                and copy-ready Python snippets for <code>zoneinfo</code> and{" "}
                <code>pytz</code>.
              </p>
            </div>
          )}

          {result && (
            <article className="result">
              <div className="result-head">
                <div>
                  <p className="muted">Matched</p>
                  <h2>{result.matched_name || `${result.city}, ${result.country}`}</h2>
                </div>
                <div className="badges">
                  <span className={`badge source-${result.source}`}>
                    {result.source}
                  </span>
                  <span className="badge">{result.confidence} confidence</span>
                </div>
              </div>

              <div className="tz-block">
                <p className="muted">IANA timezone</p>
                <div className="tz-row">
                  <code className="tz-id">{result.timezone}</code>
                  <button
                    type="button"
                    className="ghost"
                    onClick={() => copyText("tz", result.timezone)}
                  >
                    {copied === "tz" ? "Copied" : "Copy"}
                  </button>
                </div>
                <p className="local-time">
                  Local now · {formatClock(result.libraries.current_local_time_iso)}
                  <span className="offset">UTC{result.libraries.utc_offset}</span>
                  {result.libraries.is_dst ? <span className="offset">DST</span> : null}
                </p>
              </div>

              {result.coordinates && (
                <p className="coords">
                  {result.coordinates.latitude.toFixed(4)}°,{" "}
                  {result.coordinates.longitude.toFixed(4)}°
                </p>
              )}

              <div className="lib-grid">
                <div className="lib-card preferred">
                  <div className="lib-head">
                    <h3>zoneinfo + tzdata</h3>
                    <span className="pill">Recommended</span>
                  </div>
                  <pre>{`from zoneinfo import ZoneInfo
from datetime import datetime

tz = ZoneInfo("${result.timezone}")
now = datetime.now(tz)`}</pre>
                  <button
                    type="button"
                    className="ghost"
                    onClick={() =>
                      copyText(
                        "zi",
                        `from zoneinfo import ZoneInfo\nfrom datetime import datetime\n\ntz = ZoneInfo("${result.timezone}")\nnow = datetime.now(tz)`,
                      )
                    }
                  >
                    {copied === "zi" ? "Copied" : "Copy snippet"}
                  </button>
                </div>

                <div className="lib-card">
                  <div className="lib-head">
                    <h3>pytz</h3>
                    <span className="pill quiet">Legacy</span>
                  </div>
                  <pre>{`import pytz
from datetime import datetime

tz = pytz.timezone("${result.timezone}")
now = datetime.now(tz)`}</pre>
                  <button
                    type="button"
                    className="ghost"
                    onClick={() =>
                      copyText(
                        "pytz",
                        `import pytz\nfrom datetime import datetime\n\ntz = pytz.timezone("${result.timezone}")\nnow = datetime.now(tz)`,
                      )
                    }
                  >
                    {copied === "pytz" ? "Copied" : "Copy snippet"}
                  </button>
                </div>
              </div>

              {result.notes?.length > 0 && (
                <ul className="notes">
                  {result.notes.map((note) => (
                    <li key={note}>{note}</li>
                  ))}
                </ul>
              )}
            </article>
          )}
        </section>
      </main>

      <footer className="footer">
        <p>
          Online path uses OpenStreetMap Nominatim + timezonefinder. Offline
          path uses a bundled city catalog. New Python code should prefer{" "}
          <code>zoneinfo</code> with <code>tzdata</code>.
        </p>
      </footer>
    </div>
  );
}
