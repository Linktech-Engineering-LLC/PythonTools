# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-09
 File: PythonTools/weather/provider_nws.py
 Version: 1.0.0
 Description: Weather Provider NSW Fetch methods
"""

import requests
from datetime import date
from typing import Any, Dict

from .builders import build_nws_url
from .codes import nws_text_to_wmo
from ..datetime import compute_sun_times
from .providers import WEATHER_PROVIDERS
from ..units import convert_speed, convert_temperature

def fetch_hourly_nws(lat, lon, timeout, meta):
    url = build_nws_url(lat, lon, "hourly")
    raw = requests.get(url, timeout=timeout).json()

    periods = raw["properties"]["periods"]

    result = []
    for p in periods:
        start = p.get("startTime")
        date_str = start.split("T")[0] if start else None
        date_obj = date.fromisoformat(date_str) if date_str else None
        sunrise, sunset = compute_sun_times(lat, lon, date_obj, meta["timezone"])
        wmo = nws_text_to_wmo(p["shortForecast"])   # maps text → WMO code

        entry = {
            "time": p["startTime"],
            "temperature_c": convert_temperature(p["temperature"], p["temperatureUnit"], "C"),
            "wind_kph": convert_speed(parse_nws_speed(p["windSpeed"]),"mph","kph"),
            "condition": wmo,
            "sunrise": sunrise,
            "sunset": sunset,
        }
        result.append(entry)

    return {"hours":result}, url

def parse_nws_speed(value):
    """
    Extract the first numeric speed from NWS strings.
    Examples:
        "5 mph" → 5
        "10 to 20 mph" → 10
        "Calm" → None
        "Light and variable" → None
    """
    if not value:
        return None

    parts = value.split()
    try:
        return float(parts[0])
    except Exception:
        return None
def fetch_current_nws(lat: float, lon: float, timeout: int, meta: Dict[str, Any]):
    url = build_nws_url(lat, lon, "current")

    headers = {"User-Agent": "NMS_Tools/1.0"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()

    data = r.json()
    periods = data.get("properties", {}).get("periods", [])

    if not periods:
        return None, url

    p = periods[0]

    # Compute sunrise/sunset using Astral
    start = p.get("startTime")
    date_str = start.split("T")[0] if start else None
    date_obj = date.fromisoformat(date_str) if date_str else None
    sunrise, sunset = compute_sun_times(lat, lon, date_obj, meta["timezone"])

    result = {
        "time": p.get("startTime"),
        "temperature_c": convert_temperature(p["temperature"], p["temperatureUnit"], "C"),
        "wind_kph": convert_speed(parse_nws_speed(p.get("windSpeed")),"mph","kph"),
        "condition": nws_text_to_wmo(p.get("shortForecast")),
        "sunrise": sunrise,
        "sunset": sunset,
    }

    return result, url
def fetch_weekly_nws(lat: float, lon: float, timeout: int, meta: Dict[str, Any]):
    url = build_nws_url(lat, lon, "weekly")

    headers = {"User-Agent": "NMS_Tools/1.0"}
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()

    data = r.json()
    periods = data.get("properties", {}).get("periods", [])

    normalized = []
    for p in periods:
        start = p.get("startTime")
        date_str = start.split("T")[0] if start else None
        date_obj = date.fromisoformat(date_str) if date_str else None
        sunrise, sunset = compute_sun_times(lat, lon, date_obj, meta["timezone"])
        
        normalized.append({
            "date": date_str,
            "sunrise": sunrise,
            "sunset": sunset,
            "condition": nws_text_to_wmo(p.get("shortForecast")),
            "temp_max_c": convert_temperature(p.get("temperature"), p.get("temperatureUnit"), "C"),
            "temp_min_c": convert_temperature(p.get("temperature"), p.get("temperatureUnit"), "C"),
            "precip_mm": 0.0,  # NWS weekly lacks precip
            "precipitation_probability_max": p.get("probabilityOfPrecipitation", {}).get("value"),
            "wind_kph_max": convert_speed(parse_nws_speed(p.get("windSpeed")),"mph","kph"),
        })

    return {"days": normalized}, url
def fetch_full_nws(lat: float, lon: float, timeout: int, meta: dict):
    pass
def define_nws_providers():
    WEATHER_PROVIDERS["nws"].update({
        "fetch_current": fetch_current_nws,
        "fetch_hourly": fetch_hourly_nws,
        "fetch_weekly": fetch_weekly_nws,
        "fetch_full": fetch_full_nws,
    })
def resolve_nws_meta(lat: float, lon: float) -> Dict[str, Any]:
    url = f"https://api.weather.gov/points/{lat},{lon}"
    headers = {"User-Agent": "NMS_Tools/1.0"}

    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()

    props = r.json().get("properties", {})

    return {
        "office": props.get("gridId"),
        "gridX": props.get("gridX"),
        "gridY": props.get("gridY")
    }
