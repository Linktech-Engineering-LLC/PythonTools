# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-20
 File: PythonTools/datetime/format.py
 Version: 1.0.0
 Description: Module description here
"""

from datetime import datetime, timezone
from timezonefinder import TimezoneFinder   
from zoneinfo import ZoneInfo

def current_timestamp() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S %Z%z")
def ensure_dt(x):
    if x is None:
        return None

    # Already a datetime → normalize timezone
    if isinstance(x, datetime):
        if x.tzinfo is None:
            return x.replace(tzinfo=timezone.utc)
        return x

    # Open‑Meteo → string
    if isinstance(x, str):
        dt = datetime.fromisoformat(x)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    raise TypeError(f"Unsupported datetime type: {type(x)}")
def format_age(seconds: float) -> str:
    if seconds is None:
        return "unknown"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    else:
        return f"{s}s"
def get_timezone(lat: float, lon: float) -> ZoneInfo:
    tf = TimezoneFinder()
    tz = tf.timezone_at(lat=lat, lng=lon)
    return ZoneInfo(tz) if tz else ZoneInfo("UTC")
def is_daylight(now, sunrise, sunset):
    return sunrise <= now < sunset
def is_civil_twilight(now, civil_dawn, civil_dusk):
    return civil_dawn <= now < civil_dusk
def is_dark(now, sunset, next_sunrise):
    return now >= sunset or now < next_sunrise
def normalize_ts(ts: str) -> str:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
def normalize_ts_local(ts: str, tzinfo):
    # OM timestamps may be "YYYY-MM-DDTHH:MM" (no offset)
    if len(ts) == 16:
        ts = ts + ":00+00:00"
    elif ts.endswith("Z"):
        ts = ts.replace("Z", "+00:00")

    dt = datetime.fromisoformat(ts)
    return dt.astimezone(tzinfo).strftime("%Y-%m-%dT%H:00")
def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts)
