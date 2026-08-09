# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-09
 File: PythonTools/weather/provider_open_meteo.py
 Version: 1.0.0
 Description: Weather Provider Open-Meteo fetch methods
"""

import json
import urllib

from .builders import build_open_meteo_url
from ..datetime import parse_iso
from .providers import WEATHER_PROVIDERS

def fetch_hourly_open_meteo(lat, lon, timeout, meta):
    url = build_open_meteo_url(lat, lon, "hourly")

    raw = json.loads(urllib.request.urlopen(url, timeout=timeout).read())
    hourly = raw["hourly"]
    daily = raw["daily"]

    sunrise = daily["sunrise"][0]
    sunset  = daily["sunset"][0]

    result = []
    for i, t in enumerate(hourly["time"]):
        entry = {
            "time": t,
            "temperature_c": hourly["temperature_2m"][i],
            "wind_kph": hourly["windspeed_10m"][i],
            "condition": hourly["weathercode"][i],   # WMO code
            "sunrise": sunrise,
            "sunset": sunset,
        }
        result.append(entry)

    return {"hours": result}, url
def fetch_current_open_meteo(lat: float, lon: float, timeout: int, meta: dict):
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

    return result, url

def fetch_weekly_open_meteo(lat: float, lon: float, timeout: int, meta: dict):
    url = build_open_meteo_url(lat, lon, "weekly")

    with urllib.request.urlopen(url, timeout=timeout) as resp:
        raw = json.loads(resp.read())

    daily = raw.get("daily", {})
    dates = daily.get("time", [])

    days = []
    for i, d in enumerate(dates[:7]):  # next 7 days

        def h(field: str, default=None):
            arr = daily.get(field)
            if not arr or i >= len(arr):
                return default
            return arr[i]

        days.append({
            "date": d,
            "sunrise": h("sunrise"),
            "sunset": h("sunset"),
            "condition": h("weathercode"),  # WMO code
            "temp_max_c": h("temperature_2m_max"),
            "temp_min_c": h("temperature_2m_min"),
            "precip_mm": h("precipitation_sum"),
            "precipitation_probability_max": h("precipitation_probability_max"),
            "wind_kph_max": h("windspeed_10m_max"),
        })

    # RAW weekly result — no normalization, no icons, no context
    return {"days": days}, url
def fetch_full_open_meteo(lat: float, lon: float, timeout: int, meta: dict):
    pass
def define_open_meteo_providers():
    WEATHER_PROVIDERS["open-meteo"].update({
        "fetch_current": fetch_current_open_meteo,
        "fetch_hourly": fetch_hourly_open_meteo,
        "fetch_weekly": fetch_weekly_open_meteo,
        "fetch_full": fetch_full_open_meteo,
    })