# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-15
 File: PythonTools/weather/normalize.py
 Version: 1.0.0
 Description: Weather Normalization and Enrichment Utilities
"""

from datetime import datetime, date
from typing import Any, Dict

from .codes import WEATHER_CODES
from ..datetime import ensure_dt
from ..units import convert_temperature, convert_speed, convert_distance,convert_pressure
from ..utils.common import ceil1

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
    if out.get("wind_gust_kph") is not None:
        out["wind_gust_mph"] = convert_speed(out["wind_gust_kph"], "kph", "mph")
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
def normalize_index_fields(idx: dict) -> dict:
    return {
        "heat_index": ceil1(idx.get("heat_index")),
        "wind_chill": ceil1(idx.get("wind_chill")),
        "humidex": ceil1(idx.get("humidex")),
        "wet_bulb": ceil1(idx.get("wet_bulb")),

        "vapor_pressure": ceil1(idx.get("vapor_pressure")),
        "saturation_vapor_pressure": ceil1(idx.get("saturation_vapor_pressure")),
        "mixing_ratio": ceil1(idx.get("mixing_ratio")),
        "specific_humidity": ceil1(idx.get("specific_humidity")),
        "air_density": ceil1(idx.get("air_density")),
        "pressure_altitude": ceil1(idx.get("pressure_altitude")),
    }
def merge_daily_periods(days: list, hourly: list):
    """
    Merge multiple forecast periods (NWS) or daily blocks (Open-Meteo)
    into unified daily records.
    """

    # ------------------------------------------------------------
    # Step 1: Group periods by date
    # ------------------------------------------------------------
    grouped = {}
    for p in days:
        d = p["date"]
        grouped.setdefault(d, []).append(p)

    merged = []

    # ------------------------------------------------------------
    # Step 2: Merge each date's periods
    # ------------------------------------------------------------
    for d, plist in grouped.items():

        # Temperature merge
        temp_max_c = max(p.get("temp_max_c") for p in plist if p.get("temp_max_c") is not None)
        temp_min_c = min(p.get("temp_min_c") for p in plist if p.get("temp_min_c") is not None)

        # Wind merge
        wind_kph_max = max(p.get("wind_kph_max") for p in plist if p.get("wind_kph_max") is not None)

        # Precip merge
        precip_prob = max(
            (p.get("precipitation_probability_max") for p in plist
             if p.get("precipitation_probability_max") is not None),
            default=None
        )

        # Gust merge
        gust_kph_max = max(
            (p.get("wind_gust_kph") for p in plist if p.get("wind_gust_kph") is not None),
            default=None
        )
        gust_mph_max = max(
            (p.get("wind_gust_mph") for p in plist if p.get("wind_gust_mph") is not None),
            default=None
        )

        # ------------------------------------------------------------
        # Dewpoint merge (from hourly)
        # ------------------------------------------------------------
        dewpoints = [
            h.get("dewpoint_c")
            for h in hourly
            if h.get("dewpoint_c") is not None and h["time"][:10] == d
        ]

        if dewpoints:
            dewpoint_c = round(sum(dewpoints) / len(dewpoints), 1)
            dewpoint_f = round(dewpoint_c * 9/5 + 32, 1)
        else:
            dewpoint_c = None
            dewpoint_f = None

        # ------------------------------------------------------------
        # Humidity merge (from hourly)
        # ------------------------------------------------------------
        humidities = [
            h.get("humidity")
            for h in hourly
            if h.get("humidity") is not None and h["time"][:10] == d
        ]

        humidity = round(sum(humidities) / len(humidities), 1) if humidities else None

        # Feels-like merge
        feels = [p.get("feels_like_max_c") for p in plist if p.get("feels_like_max_c") is not None]
        feels_like_max_c = round(max(feels), 1) if feels else None
        feels_like_max_f = round(feels_like_max_c * 9/5 + 32, 1) if feels_like_max_c is not None else None

        feels_min = [p.get("feels_like_min_c") for p in plist if p.get("feels_like_min_c") is not None]
        feels_like_min_c = round(min(feels_min), 1) if feels_min else None
        feels_like_min_f = round(feels_like_min_c * 9/5 + 32, 1) if feels_like_min_c is not None else None

        # Source from max-feels period
        feels_like_source = None
        if feels:
            max_val = max(feels)
            for p in plist:
                if p.get("feels_like_max_c") == max_val:
                    feels_like_source = p.get("feels_like_source")
                    break

        # Choose daytime period if available
        daytime = None
        for p in plist:
            icon = p.get("icon", "")
            if "day" in icon:
                daytime = p
                break

        if daytime is None:
            daytime = plist[0]

        # Build merged daily record
        merged.append({
            "date": d,
            "sunrise": daytime.get("sunrise"),
            "sunset": daytime.get("sunset"),

            "condition": daytime.get("condition"),
            "context": daytime.get("context"),
            "icon": daytime.get("icon"),

            "temp_max_c": temp_max_c,
            "temp_min_c": temp_min_c,
            "temp_max_f": ceil1(convert_temperature(temp_max_c, "C", "F")),
            "temp_min_f": ceil1(convert_temperature(temp_min_c, "C", "F")),

            "precip_mm": daytime.get("precip_mm", 0.0),
            "precip_in": daytime.get("precip_in", 0.0),
            "precipitation_probability_max": precip_prob,

            "wind_kph_max": wind_kph_max,
            "wind_mph_max": ceil1(convert_speed(wind_kph_max, "kph", "mph")),
            "wind_gust_kph_max": gust_kph_max,
            "wind_gust_mph_max": gust_mph_max,

            "dewpoint_c": dewpoint_c,
            "dewpoint_f": dewpoint_f,
            "humidity": humidity,

            "index": daytime.get("index"),

            "feels_like_max_c": feels_like_max_c,
            "feels_like_max_f": feels_like_max_f,
            "feels_like_min_c": feels_like_min_c,
            "feels_like_min_f": feels_like_min_f,
            "feels_like_source": feels_like_source,
        })

    # Sort + today-first logic unchanged
    merged.sort(key=lambda x: x["date"])
    today_str = date.today().isoformat()
    today_entry = next((m for m in merged if m["date"] == today_str), None)
    if today_entry:
        merged.remove(today_entry)
        merged.insert(0, today_entry)

    return merged
def reorder_hourly_current_first(hours: list, tz: str):
    """
    Ensure the first hourly entry is always the current hour.
    """
    if not hours:
        return hours

    # Current local hour (rounded down)
    now = datetime.now().astimezone().replace(minute=0, second=0, microsecond=0)
    now_iso = now.isoformat()

    # Find the index of the matching hour block
    idx = None
    for i, h in enumerate(hours):
        t = datetime.fromisoformat(h["time"])
        if t.hour == now.hour and t.date() == now.date():
            idx = i
            break

    # If found, rotate list
    if idx is not None:
        return hours[idx:] + hours[:idx]

    # Otherwise leave unchanged
    return hours
def normalize_gusts_kph_mph(gust_value):
    """
    Normalize gust values into kph and mph.
    gust_value may be:
        - None
        - numeric (Open-Meteo, kph)
        - string like '25 mph' (NWS)
    """
    if gust_value is None:
        return None, None

    # NWS: string like "25 mph"
    if isinstance(gust_value, str):
        try:
            mph = float(gust_value.split()[0])
            kph = mph * 1.60934
            return kph, mph
        except Exception:
            return None, None

    # Open-Meteo: numeric kph
    if isinstance(gust_value, (int, float)):
        kph = float(gust_value)
        mph = kph / 1.60934
        return kph, mph

    return None, None
