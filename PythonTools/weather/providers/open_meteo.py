# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-10
 Modified: 2026-08-20
 File: PythonTools/weather/providers/open_meteo.py
 Version: 1.0.0
 Description: Module description here
"""

import json
import urllib.request
from typing import Any, Dict

from .builders import build_open_meteo_url
from ..indexes import compute_indexes_from_fields
from ..normalize import normalize_index_fields, normalize_gusts_kph_mph
from ...datetime import parse_iso, moon_phase_info, compute_moon_times
from ..registry import WEATHER_PROVIDERS
from ...utils.common import ceil1

def fetch_hourly_open_meteo(lat: float, lon: float, timeout: int, meta: Dict[str, Any]):
    url = build_open_meteo_url(lat, lon, "hourly")

    raw = json.loads(urllib.request.urlopen(url, timeout=timeout).read())
    hourly = raw["hourly"]
    daily = raw["daily"]

    sunrise = daily["sunrise"][0]
    sunset  = daily["sunset"][0]

    result = []
    for i, t in enumerate(hourly["time"]):
        gust_raw = hourly["windgusts_10m"][i]
        gust_kph, gust_mph = normalize_gusts_kph_mph(gust_raw)
        date_obj = parse_iso(t).date()
        moon = moon_phase_info(date_obj.isoformat())
        moonrise, moonset = compute_moon_times(lat, lon, date_obj, meta["timezone"])

        entry = {
            "time": t,
            "condition": hourly["weathercode"][i],
            "sunrise": sunrise,
            "sunset": sunset,
            "moon_phase": moon["moon_phase"],
            "moon_phase_code": moon["moon_phase_code"],
            "moon_illumination": moon["moon_illumination"],
            "moonrise": moonrise,
            "moonset": moonset,
            "temperature_c": hourly["temperature_2m"][i],
            "apparent_temperature_c": hourly["apparent_temperature"][i],
            "dewpoint_c": hourly["dewpoint_2m"][i],
            "humidity": hourly["relativehumidity_2m"][i],
            "pressure_msl": hourly["pressure_msl"][i],
            "visibility_m": hourly["visibility"][i],
            "precip_mm": hourly["precipitation"][i],
            "precipitation_probability": hourly["precipitation_probability"][i],
            "cloudcover": hourly["cloudcover"][i],
            "wind_kph": hourly["windspeed_10m"][i],
            "wind_gust_kph": ceil1(gust_kph),
            "wind_gust_mph": ceil1(gust_mph),
        }

        indexes = compute_indexes_from_fields(
            temp_c = hourly["temperature_2m"][i],
            dewpoint_c = hourly["dewpoint_2m"][i],
            rh = hourly["relativehumidity_2m"][i],
            wind_kph = hourly["windspeed_10m"][i],
            pressure_hpa = hourly["pressure_msl"][i],
        )
        entry["index"] = normalize_index_fields(indexes)

        result.append(entry)

    return {"hours": result}, url
def fetch_current_open_meteo(lat: float, lon: float, timeout: int, meta: Dict[str, Any]):
    url = build_open_meteo_url(lat, lon, "current")

    with urllib.request.urlopen(url, timeout=timeout) as resp:
        raw = json.loads(resp.read())

    current = raw.get("current_weather", {})
    hourly = raw.get("hourly", {})
    daily = raw.get("daily", {})

    sunrise = daily.get("sunrise", [None])[0]
    sunset  = daily.get("sunset", [None])[0]

    current_time = current.get("time")
    times = hourly.get("time", [])
    date_obj = parse_iso(current_time).date()
    moon = moon_phase_info(date_obj.isoformat())
    moonrise, moonset = compute_moon_times(lat, lon, date_obj, meta["timezone"])
    # Align current time to nearest hourly index
    idx = 0
    if current_time and times:
        ct = parse_iso(current_time)
        hourly_dt = [parse_iso(t) for t in times]
        idx = min(range(len(hourly_dt)), key=lambda i: abs(hourly_dt[i] - ct))

    def h(field, default=None):
        arr = hourly.get(field)
        if not arr or idx >= len(arr):
            return default
        return arr[idx]
    # RAW result — no normalization, no icons, no context
    result = {
        "time": current_time,
        "sunrise": sunrise,
        "sunset": sunset,
        "moon_phase": moon["moon_phase"],
        "moon_phase_code": moon["moon_phase_code"],
        "moon_illumination": moon["moon_illumination"],
        "moonrise": moonrise,
        "moonset": moonset,
        "temperature_c": current.get("temperature", h("temperature_2m")),
        "wind_kph": current.get("windspeed", h("windspeed_10m")),
        "wind_gust_kph": h("windgusts_10m"),
        "humidity": h("relativehumidity_2m"),
        "precip_mm": h("precipitation"),
        "cloudcover": h("cloudcover"),
        "condition": current.get("weathercode", h("weathercode")),  # WMO code
        "apparent_temperature_c": h("apparent_temperature"),
        "dewpoint_c": h("dewpoint_2m"),
        "visibility_m": h("visibility"),
        "pressure_msl": h("pressure_msl"),
        "precipitation_probability": h("precipitation_probability"),
    }
    indexes = compute_indexes_from_fields(
        temp_c=result["temperature_c"],
        wind_kph=result["wind_kph"],
        dewpoint_c=result["dewpoint_c"],
        rh=result["humidity"],
        pressure_hpa=result["pressure_msl"],
    )
    result["index"] = normalize_index_fields(indexes)
    return result, url
def fetch_weekly_open_meteo(lat: float, lon: float, timeout: int, meta: Dict[str, Any]):
    url = build_open_meteo_url(lat, lon, "weekly")

    with urllib.request.urlopen(url, timeout=timeout) as resp:
        raw = json.loads(resp.read())

    daily = raw.get("daily", {})
    dates = daily.get("time", [])

    # NWS observations (added earlier in main())
    obs = meta.get("cached_obs")
    if not obs:
        raise RuntimeError("Open-Meteo weekly requires cached NWS observations")

    # Extract observation fields
    dewpoint_c = obs.get("dewpoint", {}).get("value")
    rh = obs.get("relativeHumidity", {}).get("value")

    pressure_pa = obs.get("barometricPressure", {}).get("value")
    pressure_hpa = pressure_pa / 100 if pressure_pa else None

    days = []
    for i, d in enumerate(dates[:7]):  # next 7 days

        def h(field: str, default=None):
            arr = daily.get(field)
            if not arr or i >= len(arr):
                return default
            return arr[i]
        date_obj = parse_iso(d).date()
        moon = moon_phase_info(date_obj.isoformat())
        moonrise, moonset = compute_moon_times(lat, lon, date_obj, meta["timezone"])

        temp_max_c = h("temperature_2m_max")
        wind_kph_max = h("windspeed_10m_max")
        indexes = compute_indexes_from_fields(
            temp_c=temp_max_c,
            dewpoint_c=dewpoint_c,
            rh=rh,
            wind_kph=wind_kph_max,
            pressure_hpa=pressure_hpa
        )
        gust_raw = h("windgusts_10m_max")
        gust_kph, gust_mph = normalize_gusts_kph_mph(gust_raw)
        days.append({
            "date": d,
            "sunrise": h("sunrise"),
            "sunset": h("sunset"),
            "moon_phase": moon["moon_phase"],
            "moon_phase_code": moon["moon_phase_code"],
            "moon_illumination": moon["moon_illumination"],
            "moonrise": moonrise,
            "moonset": moonset,
            "condition": h("weathercode"),
            "temp_max_c": temp_max_c,
            "temp_min_c": h("temperature_2m_min"),
            "precip_mm": h("precipitation_sum"),
            "precipitation_probability_max": h("precipitation_probability_max"),
            "wind_kph_max": wind_kph_max,
            "wind_gust_kph": ceil1(gust_kph),
            "wind_gust_mph": ceil1(gust_mph),

            # Full index engine using NWS obs + Open-Meteo forecast
            "index": normalize_index_fields(indexes),
        })

    return {"days": days}, url
def fetch_full_open_meteo(lat: float, lon: float, timeout: int, meta: Dict[str, Any]):
    # 1. Fetch current
    current, current_url = fetch_current_open_meteo(lat, lon, timeout, meta)

    # 2. Fetch hourly
    hourly, hourly_url = fetch_hourly_open_meteo(lat, lon, timeout, meta)

    # 3. Fetch weekly
    weekly, weekly_url = fetch_weekly_open_meteo(lat, lon, timeout, meta)

    # 4. Build unified provider block
    return {
        "current": current,
        "hourly": hourly,
        "weekly": weekly,
        "provider": "open-meteo",
        "urls": {
            "current": current_url,
            "hourly": hourly_url,
            "weekly": weekly_url
        }
    }
