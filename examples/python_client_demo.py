"""CLI example: resolve a city/country and use zoneinfo (preferred) vs pytz.

Usage (from repo root, with the API running):
  python examples/python_client_demo.py "Tokyo" "Japan"
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

import httpx
import pytz


def main() -> None:
    city = sys.argv[1] if len(sys.argv) > 1 else "Tokyo"
    country = sys.argv[2] if len(sys.argv) > 2 else "Japan"
    base = sys.argv[3] if len(sys.argv) > 3 else "http://127.0.0.1:8001"

    response = httpx.post(
        f"{base}/api/resolve",
        json={"city": city, "country": country, "prefer_source": "auto"},
        timeout=20.0,
    )
    response.raise_for_status()
    data = response.json()
    iana = data["timezone"]

    print(json.dumps(data, indent=2))
    print()
    print("zoneinfo (recommended):", datetime.now(ZoneInfo(iana)).isoformat())
    print("pytz (legacy):         ", datetime.now(pytz.timezone(iana)).isoformat())


if __name__ == "__main__":
    main()
