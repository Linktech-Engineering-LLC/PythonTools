# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-09
 File: PythonTools/weather/normalize.py
 Version: 1.0.0
 Description: Weather Normalization and Enrichment Utilities
"""

from datetime import datetime, date
from typing import Any, Dict

from .codes import WEATHER_CODES
from ..datetime import ensure_dt
from ..units import convert_temperature, convert_speed, convert_distance,convert_pressure

def enrich(entry: Dict[str, Any],
           units: str,
           meta: Dict[str, Any],
           logging_enabled: bool,
           logger=None) -> Dict[str, Any]:

    # --- 1. Unit conversion (provider-agnostic) ---
    out = convert_units_any(entry, units)

    # --- 2. Extract WMO code (providers already supply this) ---
    code = entry.get("condition")

    # --- 3. Validate WMO code ---
    if code is None or not isinstance(code, int) or code not in WEATHER_CODES:
        if logger and logging_enabled:
            logger.error(f"Unknown or unmapped weather condition: {code!r}")

        out["condition"] = None
        out["context"] = "Unknown"
        out["icon"] = "wi-na.svg"
        return out

    # --- 4. Map WMO → canonical context ---
    info = WEATHER_CODES[code]
    out["context"] = info["canonical"]

    # --- 5. Icon selection (requires sunrise/sunset/time) ---
    sunrise = entry.get("sunrise")
    sunset = entry.get("sunset")
    # Weekly mode: date-only → build aware datetime using sunrise's timezone
    if entry.get("time"):
        now = entry["time"]
    elif entry.get("date"):
        # Use sunrise's timezone
        tz = meta["timezone"]
        now = datetime.fromisoformat(entry["date"]).replace(hour=12, tzinfo=tz)
    else:
        now = entry.get("startTime")

    if sunrise and sunset and now:
        out["icon"] = select_icon(code, sunrise, sunset, now, WEATHER_CODES)
    else:
        out["icon"] = "wi-na.svg"

    return out
def convert_units_mode_aware(
    data: Dict[str, Any],
    units: str,
    mode: str,
    meta: Dict[str, Any],
    logging_enabled: bool,
    logger=None
) -> Dict[str, Any]:

    match mode:
        case "current":
            out = enrich(data, units, meta, logging_enabled, logger)

        case "hourly":
            out = dict(data)
            out["hours"] = [
                enrich(h, units, meta, logging_enabled, logger)
                for h in data.get("hours", [])
            ]
            out["units"] = units
            return out

        case "weekly":
            out = dict(data)
            sliced = slice_weekly_days(data["days"])
            out["days"] = [
                enrich(d, units, meta, logging_enabled, logger)
                for d in sliced
            ]
            out["units"] = units
            return out

        case _:
            return data

    out["units"] = units
    return out
def convert_units_any(data: Dict[str, Any], units: str) -> Dict[str, Any]:
    """
    Convert any weather dictionary (current, hourly, weekly) to include
    both metric and imperial fields.
    """
    out = dict(data)

    # Temperature fields
    for key in ["temperature", "apparent_temperature", "dewpoint",
                "temp_max", "temp_min"]:
        c = out.get(f"{key}_c")
        if c is not None:
            out[f"{key}_f"] = convert_temperature(c, "C", "F")

    # Wind fields
    wind_fields = [
        ("wind_kph", "wind_mph"),
        ("wind_gust_kph", "wind_gust_mph"),
        ("wind_kph_max", "wind_mph_max"),
    ]

    for kph_key, mph_key in wind_fields:
        kph = out.get(kph_key)
        if kph is not None:
            out[mph_key] = convert_speed(kph, "kph","mph")

    # Precip fields
    for key in ["precip"]:
        mm = out.get(f"{key}_mm")
        if mm is not None:
            out[f"{key}_in"] = convert_distance(mm, "mm", "in")

    # Visibility
    if out.get("visibility_m") is not None:
        out["visibility_km"] = convert_distance(out["visibility_m"], "m", "km")
        out["visibility_mi"] = convert_distance(out["visibility_m"], "m", "mi")

    # Pressure
    if out.get("pressure_msl") is not None:
        out["pressure_inhg"] = convert_pressure(out["pressure_msl"], "hpa","inhg")

    return out
def slice_weekly_days(days):
    today = date.today()

    # Find first index where date >= today
    start = next(
        (i for i, d in enumerate(days) if date.fromisoformat(d["date"]) >= today),
        0
    )

    # Always return 7 days if available
    return days[start:start+7]
def select_icon(weather_code, sunrise, sunset, now, mapping):
    """
    Selects the correct icon (day or night) based on sunrise/sunset times.

    Parameters:
        weather_code (int): WMO weather code.
        sunrise (str): ISO timestamp for sunrise, e.g. "2026-04-27T06:28".
        sunset (str): ISO timestamp for sunset, e.g. "2026-04-27T20:12".
        now (str or datetime): Current local time.
        mapping (dict): WEATHER_CODES mapping with day_icon/night_icon.

    Returns:
        str: The icon filename to use.
    """

    # Normalize "now" to datetime
    if isinstance(now, str):
        now = datetime.fromisoformat(now)

    sunrise_dt = ensure_dt(sunrise)
    sunset_dt = ensure_dt(sunset)
    now_dt = ensure_dt(now)
    
    entry = mapping.get(weather_code)

    if not entry or sunrise_dt is None or sunset_dt is None or now_dt is None:
        # Fallback to NA icon if code missing
        return "wi-na.svg"

    # Handle polar day (sun never sets)
    if sunrise_dt == sunset_dt:
        return entry["day_icon"]

    # Handle polar night (sun never rises)
    if sunrise_dt > sunset_dt:
        return entry["night_icon"]

    # Normal case: between sunrise and sunset = day
    if sunrise_dt <= now_dt < sunset_dt:
        return entry["day_icon"]

    return entry["night_icon"]
def slice_next_24_hours(hourly):
    # Parse timestamps into datetime objects
    times = [datetime.fromisoformat(t) for t in hourly["time"]]

    # Round current time down to the hour
    now = datetime.now().replace(minute=0, second=0, microsecond=0)

    # Find first index >= now
    start = next((i for i, t in enumerate(times) if t >= now), 0)

    # Slice next 24 hours
    end = start + 24
    return range(start, min(end, len(times)))
