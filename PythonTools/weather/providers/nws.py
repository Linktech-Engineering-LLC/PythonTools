# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-10
 Modified: 2026-08-11
 File: PythonTools/weather/providers/nws.py
 Version: 1.0.0
 Description: Weather Provider NWS functions
"""

import requests
from datetime import date, datetime
from typing import Any, Dict

from .builders import build_nws_url
from ..codes import nws_text_to_wmo, map_icon, map_context
from ..indexes import compute_indexes_from_fields
from ...datetime import compute_sun_times, is_daylight
from ..registry import WEATHER_PROVIDERS
from ...units import convert_speed, convert_temperature, haversine

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
        entry["index"] = compute_indexes_from_fields(
            temp_c=entry["temperature_c"],
            rh=None,
            wind_kph=entry["wind_kph"],
            dewpoint_c=None,
        )
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
    headers = {"User-Agent": "NMS_Tools/1.0"}

    #
    # 1. Try NWS observations/latest (full detail)
    #
    try:
        obs, obs_url, station_id = fetch_valid_nws_observation(lat, lon, timeout, meta)

        if obs:
            rc = normalize_nws_observation(obs, lat, lon, meta), obs_url
            rc[0]["station_id"] = station_id
            return rc

    except Exception:
        # Observation unavailable → fallback to forecastHourly
        pass

    #
    # 2. Fallback: use forecastHourly (your existing logic)
    #
    url = build_nws_url(lat, lon, "current")
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()

    data = r.json()
    periods = data.get("properties", {}).get("periods", [])

    if not periods:
        return None, url

    p = periods[0]

    # Compute sunrise/sunset
    start = p.get("startTime")
    date_str = start.split("T")[0] if start else None
    date_obj = date.fromisoformat(date_str) if date_str else None
    sunrise, sunset = compute_sun_times(lat, lon, date_obj, meta["timezone"])

    result = {
        "time": p.get("startTime"),
        "temperature_c": convert_temperature(p["temperature"], p["temperatureUnit"], "C"),
        "wind_kph": convert_speed(parse_nws_speed(p.get("windSpeed")), "mph", "kph"),
        "condition": nws_text_to_wmo(p.get("shortForecast")),
        "sunrise": sunrise,
        "sunset": sunset,
    }

    # No dewpoint/humidity → indexes will be null (correct)
    result["index"] = compute_indexes_from_fields(
        temp_c=result["temperature_c"],
        dewpoint_c=None,
        rh=None,
        wind_kph=result["wind_kph"],
    )

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
        
        result = {
            "date": date_str,
            "sunrise": sunrise,
            "sunset": sunset,
            "condition": nws_text_to_wmo(p.get("shortForecast")),
            "temp_max_c": convert_temperature(p.get("temperature"), p.get("temperatureUnit"), "C"),
            "temp_min_c": convert_temperature(p.get("temperature"), p.get("temperatureUnit"), "C"),
            "precip_mm": 0.0,  # NWS weekly lacks precip
            "precipitation_probability_max": p.get("probabilityOfPrecipitation", {}).get("value"),
            "wind_kph_max": convert_speed(parse_nws_speed(p.get("windSpeed")),"mph","kph"),
        }
        result["index"] = compute_indexes_from_fields(
            temp_c=result["temp_max_c"],
            rh=None,
            wind_kph=result["wind_kph_max"],
            dewpoint_c=None,
        )
        normalized.append(result)
    return {"days": normalized}, url
def fetch_full_nws(lat: float, lon: float, timeout: int, meta: dict):
    pass
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
def normalize_nws_observation(obs: Dict[str, Any], lat: float, lon: float, meta: Dict[str, Any]):
    """
    Normalize NWS observations/latest into your unified schema.
    """

    # Extract fields safely
    temp_c = obs.get("temperature", {}).get("value")
    dewpoint_c = obs.get("dewpoint", {}).get("value")
    rh = obs.get("relativeHumidity", {}).get("value")
    wind_mps = obs.get("windSpeed", {}).get("value")  # m/s
    wind_gust_mps = obs.get("windGust", {}).get("value")
    visibility_m = obs.get("visibility", {}).get("value")
    pressure_pa = obs.get("barometricPressure", {}).get("value")

    # Convert units
    wind_kph = convert_speed(wind_mps, "mps", "kph") if wind_mps is not None else None
    wind_gust_kph = convert_speed(wind_gust_mps, "mps", "kph") if wind_gust_mps is not None else None
    visibility_km = visibility_m / 1000.0 if visibility_m is not None else None
    pressure_hpa = pressure_pa / 100.0 if pressure_pa is not None else None

    # Condition mapping
    raw_weather = obs.get("textDescription")
    condition = nws_text_to_wmo(raw_weather)

    # Sunrise/sunset
    ts = obs.get("timestamp")
    now = datetime.fromisoformat(ts) if ts else datetime.now
    date_str = ts.split("T")[0] if ts else None
    date_obj = date.fromisoformat(date_str) if date_str else None
    sunrise, sunset = compute_sun_times(lat, lon, date_obj, meta["timezone"])

    # Build result
    result = {
        "time": ts,
        "temperature_c": temp_c,
        "dewpoint_c": dewpoint_c,
        "humidity": rh,
        "wind_kph": wind_kph,
        "wind_gust_kph": wind_gust_kph,
        "visibility_m": visibility_m,
        "pressure_msl": pressure_hpa,
        "condition": condition,
        "sunrise": sunrise,
        "sunset": sunset,
        "context": map_context(condition),
        "icon": map_icon(condition, is_daylight(sunrise=sunrise, sunset=sunset, now=now)),
    }

    # Indexes (now fully available!)
    result["index"] = compute_indexes_from_fields(
        temp_c=temp_c,
        dewpoint_c=dewpoint_c,
        rh=rh,
        wind_kph=wind_kph,
    )

    # Additional converted fields
    result["temperature_f"] = convert_temperature(temp_c, "C", "F") if temp_c is not None else None
    result["dewpoint_f"] = convert_temperature(dewpoint_c, "C", "F") if dewpoint_c is not None else None
    result["wind_mph"] = convert_speed(wind_kph, "kph", "mph") if wind_kph is not None else None
    result["wind_gust_mph"] = convert_speed(wind_gust_kph, "kph", "mph") if wind_gust_kph is not None else None
    result["visibility_mi"] = visibility_km * 0.621371 if visibility_km is not None else None
    result["pressure_inhg"] = pressure_hpa * 0.02953 if pressure_hpa is not None else None

    return result
def fetch_valid_nws_observation(lat: float, lon: float, timeout: int, meta: Dict[str, Any]):
    base = WEATHER_PROVIDERS["nws"]["base"]
    headers = {"User-Agent": "NMS_Tools/1.0"}

    # ------------------------------------------------------------
    # Step 1: Resolve primary gridpoint
    # ------------------------------------------------------------
    point_url = f"{base}/points/{lat},{lon}"
    point_data = requests.get(point_url, timeout=timeout).json()["properties"]

    grid_id = point_data["gridId"]
    grid_x = point_data["gridX"]
    grid_y = point_data["gridY"]

    # Helper: fetch stations for a grid cell
    def fetch_grid_stations(x, y):
        url = f"{base}/gridpoints/{grid_id}/{x},{y}/stations"
        r = requests.get(url, timeout=timeout)
        if r.status_code != 200:
            return []
        return r.json().get("features", [])

    # Helper: try stations in order
    def try_station_ids(station_ids):
        for sid in station_ids:
            obs_url = f"{base}/stations/{sid}/observations/latest"
            try:
                r = requests.get(obs_url, headers=headers, timeout=timeout)
                r.raise_for_status()
                obs = r.json().get("properties", {})
                if is_valid_observation(obs):
                    return obs, obs_url, sid
            except Exception:
                continue
        return None

    # ------------------------------------------------------------
    # Step 2: Expanded gridpoint stations (ASOS/AWOS prioritized)
    # ------------------------------------------------------------
    expanded_stations = []

    # Include primary grid
    expanded_stations.extend(fetch_grid_stations(grid_x, grid_y))

    # Include neighbors
    neighbors = [
        (grid_x - 1, grid_y),
        (grid_x + 1, grid_y),
        (grid_x, grid_y - 1),
        (grid_x, grid_y + 1),
        (grid_x - 1, grid_y - 1),
        (grid_x - 1, grid_y + 1),
        (grid_x + 1, grid_y - 1),
        (grid_x + 1, grid_y + 1),
    ]

    for nx, ny in neighbors:
        expanded_stations.extend(fetch_grid_stations(nx, ny))

    # Deduplicate by stationIdentifier
    unique = {}
    for s in expanded_stations:
        sid = s["properties"]["stationIdentifier"]
        unique[sid] = s

    expanded = list(unique.values())

    # Enrich with full metadata + compute distance
    enriched = []
    for s in expanded:
        sid = s["properties"]["stationIdentifier"]

        # Fetch full station metadata
        meta_url = f"{base}/stations/{sid}"
        meta_r = requests.get(meta_url, timeout=timeout)
        if meta_r.status_code != 200:
            continue

        meta_c = meta_r.json()

        # GeoJSON coordinates: [lon, lat]
        coords = meta_c.get("geometry", {}).get("coordinates", None)
        if not coords or len(coords) != 2:
            continue

        slon, slat = coords[0], coords[1]
        stype = meta_c.get("properties", {}).get("stationType", "").upper()

        dist = haversine(lat, lon, slat, slon)
        enriched.append((dist, sid, stype))

    # Sort by distance
    enriched.sort(key=lambda x: x[0])

    # Split ASOS/AWOS first
    asos_awos = [sid for dist, sid, stype in enriched if stype in ("ASOS", "AWOS")]
    others    = [sid for dist, sid, stype in enriched if stype not in ("ASOS", "AWOS")]

    # Try ASOS/AWOS first
    result = try_station_ids(asos_awos)
    if result:
        return result

    # Then try everything else
    result = try_station_ids(others)
    if result:
        return result

    # ------------------------------------------------------------
    # Nothing worked
    # ------------------------------------------------------------
    return None, None, None
def is_valid_observation(obs: Dict[str, Any]) -> bool:
    """Return True if the observation is usable."""

    # Must have timestamp
    if not obs.get("timestamp"):
        return False

    # Must have temperature
    temp = obs.get("temperature", {}).get("value")
    if temp is None or temp < -60 or temp > 60:
        return False

    # Must have wind speed
    wind_mps = obs.get("windSpeed", {}).get("value") or 0

    wind_kph = convert_speed(wind_mps, "mps", "kph") or 0

    # Gust optional
    gust_mps = obs.get("windGust", {}).get("value")
    gust_kph = convert_speed(gust_mps, "mps", "kph") if gust_mps is not None else 0
    gust_kph = 0 if gust_kph is None else gust_kph
    
    # Extreme wind sanity check
    if wind_kph > 60 or gust_kph > 90:
        severe_signals = 0

        # humidity high
        rh = obs.get("relativeHumidity", {}).get("value")
        if rh is not None and rh > 85:
            severe_signals += 1

        # dewpoint high
        dew = obs.get("dewpoint", {}).get("value")
        if dew is not None and dew > 20:
            severe_signals += 1

        # pressure dropping
        pres = obs.get("barometricPressure", {}).get("value")
        if pres is not None and pres < 99000:
            severe_signals += 1

        # visibility low
        vis = obs.get("visibility", {}).get("value")
        if vis is not None and vis < 5000:
            severe_signals += 1

        # present weather codes (TS, RA, FC)
        wx = obs.get("textDescription", "")
        if any(code in wx for code in ["TS", "RA", "FC"]):
            severe_signals += 1

        # cloud layers (CB)
        clouds = obs.get("cloudLayers", [])
        if any(layer.get("amount") == "CB" for layer in clouds):
            severe_signals += 1

        # If no severe signals → broken station
        if severe_signals == 0:
            return False

    # Dewpoint sanity check
    dew = obs.get("dewpoint", {}).get("value")
    if dew is not None:
        if dew < -60 or dew > 40:
            return False
        if dew > temp:
            return False

    # Humidity sanity check
    rh = obs.get("relativeHumidity", {}).get("value")
    if rh is not None and (rh < 0 or rh > 100):
        return False

    # Pressure sanity check
    pres = obs.get("barometricPressure", {}).get("value")
    if pres is not None and (pres < 80000 or pres > 110000):
        return False

    return True
