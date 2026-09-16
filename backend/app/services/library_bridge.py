from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import pytz

from app.models import TimeLibraryMapping


def build_library_mapping(iana_id: str) -> TimeLibraryMapping:
    """Map an IANA timezone id to zoneinfo (preferred) and pytz usage snippets."""
    now_utc = datetime.now(timezone.utc)

    try:
        zi = ZoneInfo(iana_id)
        local_zi = now_utc.astimezone(zi)
        offset = local_zi.strftime("%z")
        offset_fmt = f"{offset[:3]}:{offset[3:]}" if offset else "+00:00"
        is_dst = bool(local_zi.dst()) if local_zi.dst() is not None else False
        current_iso = local_zi.isoformat()
        zoneinfo_block = {
            "recommended": True,
            "import": "from zoneinfo import ZoneInfo",
            "usage": f'ZoneInfo("{iana_id}")',
            "note": (
                "Preferred for Python 3.9+. On Windows/macOS without a system "
                "tz database, install the tzdata package."
            ),
        }
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Unknown IANA timezone id: {iana_id}") from exc

    pytz_tz = pytz.timezone(iana_id)
    local_pytz = now_utc.astimezone(pytz_tz)
    pytz_block = {
        "recommended": False,
        "import": "import pytz",
        "usage": f'pytz.timezone("{iana_id}")',
        "note": (
            "Legacy. Prefer zoneinfo for new code. pytz is retained here for "
            "compatibility checks against existing codebases."
        ),
        "localized_example": local_pytz.isoformat(),
    }

    return TimeLibraryMapping(
        iana_id=iana_id,
        zoneinfo=zoneinfo_block,
        pytz=pytz_block,
        current_local_time_iso=current_iso,
        utc_offset=offset_fmt,
        is_dst=is_dst,
    )
