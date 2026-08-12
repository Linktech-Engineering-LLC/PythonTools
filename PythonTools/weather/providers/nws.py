# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-10
 Modified: 2026-08-12
 File: PythonTools/weather/providers/nws.py
 Version: 1.0.0
 Description: Weather Provider NWS functions
"""

from astral import now
from astral import now
import requests
from datetime import date, datetime
from typing import Any, Dict

from .builders import build_nws_url
from ..codes import nws_text_to_wmo, map_icon, map_context
from ...datetime import compute_sun_times, is_daylight
from ..registry import WEATHER_PROVIDERS
from ...units import convert_speed, convert_temperature, haversine, compute_feels_like, compute_indexes_from_fields
from ...utils import round1, ceil1

def fetch_hourly_nws(lat, lon, timeout, meta):
    #
    # Use cached observation URL if available
    #
    obs = meta.get("cached_obs")
    obs_url = meta.get("cached_obs_url")  # you should store this in main dispatcher

    #
    # Fetch hourly forecast
    #
    url = build_nws_url(lat, lon, "hourly")
    raw = requests.get(url, timeout=timeout).json()

    periods = raw["properties"]["periods"]

    normalized = []

    for p in periods:
        start = p.get("startTime")
        date_str = start.split("T")[0] if start else None
        now = datetime.fromisoformat(start) if start else datetime.now()

        date_obj = date.fromisoformat(date_str) if date_str else None
        sunrise, sunset = compute_sun_times(lat, lon, date_obj, meta["timezone"])
        is_day = is_daylight(now, sunrise, sunset)

        #
        # Base fields from forecastHourly
        #
        temp_c = ceil1(convert_temperature(p.get("temperature"), p.get("temperatureUnit"), "C"))
        temp_f = ceil1(convert_temperature(temp_c, "C", "F"))

        dewpoint_c = ceil1(p.get("dewpoint", {}).get("value"))
        rh = ceil1(p.get("relativeHumidity", {}).get("value"))

        wind_kph = ceil1(convert_speed(parse_nws_speed(p.get("windSpeed")), "mph", "kph"))
        wind_mph = ceil1(convert_speed(wind_kph, "kph", "mph"))

        #
        # Observation fallback (if forecastHourly missing values)
        #
        if obs:
            if dewpoint_c is None:
                dewpoint_c = ceil1(obs.get("dewpoint", {}).get("value"))

            if rh is None:
                rh = ceil1(obs.get("relativeHumidity", {}).get("value"))

            if wind_kph is None:
                wind_mps_obs = obs.get("windSpeed", {}).get("value")
                if wind_mps_obs is not None:
                    wind_kph = ceil1(convert_speed(wind_mps_obs, "mps", "kph"))
                    wind_mph = ceil1(convert_speed(wind_kph, "kph", "mph"))

        #
        # Full index set
        #
        indexes = compute_indexes_from_fields(
            temp_c=temp_c,
            dewpoint_c=dewpoint_c,
            rh=rh,
            wind_kph=wind_kph,
        )

        #
        # Unified feels-like
        #
        fl_c, fl_f, fl_src = compute_feels_like(
            temp_c=temp_c,
            dewpoint_c=dewpoint_c,
            rh=rh,
            wind_kph=wind_kph,
            is_day=is_day,
        )

        result = {
            "time": start,
            "temperature_c": temp_c,
            "temperature_f": temp_f,

            "dewpoint_c": ceil1(dewpoint_c),
            "dewpoint_f": ceil1(convert_temperature(ceil1(dewpoint_c), "C", "F")) if dewpoint_c else None,
            "humidity": ceil1(rh),

            "wind_kph": ceil1(wind_kph),
            "wind_mph": ceil1(wind_mph),

            "sunrise": sunrise,
            "sunset": sunset,

            "condition": nws_text_to_wmo(p.get("shortForecast")),
            "context": map_context(nws_text_to_wmo(p.get("shortForecast"))),
            "icon": map_icon(nws_text_to_wmo(p.get("shortForecast")), is_day),

            "index": indexes,

            "feels_like_c": ceil1(fl_c),
            "feels_like_f": ceil1(fl_f),
            "feels_like_source": fl_src,
        }

        normalized.append(result)

    #
    # Return cached observation URL if available
    #
    return {"hours": normalized}, (obs_url or url)

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
    # 2. Fallback: use forecastHourly
    #
    url = build_nws_url(lat, lon, "current")
    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()

    data = r.json()
    periods = data.get("properties", {}).get("periods", [])

    if not periods:
        return None, url

    p = periods[0]

    # Raw values (NO rounding here)
    temp_c_raw = convert_temperature(p["temperature"], p["temperatureUnit"], "C")
    dewpoint_c_raw = p.get("dewpoint", {}).get("value")
    rh_raw = p.get("relativeHumidity", {}).get("value")
    wind_mps_raw = parse_nws_speed(p.get("windSpeed"))

    # Observation fallback
    obs = meta.get("cached_obs")
    if obs:
        if dewpoint_c_raw is None:
            dewpoint_c_raw = obs.get("dewpoint", {}).get("value")

        if rh_raw is None:
            rh_raw = obs.get("relativeHumidity", {}).get("value")

        if wind_mps_raw is None:
            wind_mps_raw = obs.get("windSpeed", {}).get("value")

    # Convert wind
    wind_kph_raw = convert_speed(wind_mps_raw, "mps", "kph")
    wind_mph_raw = convert_speed(wind_kph_raw, "kph", "mph")

    # Compute sunrise/sunset
    start = p.get("startTime")
    date_str = start.split("T")[0]
    date_obj = date.fromisoformat(date_str)
    sunrise, sunset = compute_sun_times(lat, lon, date_obj, meta["timezone"])
    is_day = is_daylight(datetime.fromisoformat(start), sunrise, sunset)

    # Compute indexes (RAW values)
    indexes_raw = compute_indexes_from_fields(
        temp_c=temp_c_raw,
        dewpoint_c=dewpoint_c_raw,
        rh=rh_raw,
        wind_kph=wind_kph_raw,
    )

    # Unified feels-like (RAW values)
    fl_c_raw, fl_f_raw, fl_src = compute_feels_like(
        temp_c=temp_c_raw,
        dewpoint_c=dewpoint_c_raw,
        rh=rh_raw,
        wind_kph=wind_kph_raw,
        is_day=is_day,
    )

    # Presentation layer (CEILING ROUNDING)
    result = {
        "time": start,
        "temperature_c": ceil1(temp_c_raw),
        "temperature_f": ceil1(convert_temperature(temp_c_raw, "C", "F")),
        "wind_kph": ceil1(wind_kph_raw),
        "wind_mph": ceil1(wind_mph_raw),
        "sunrise": sunrise,
        "sunset": sunset,
        "condition": nws_text_to_wmo(p.get("shortForecast")),
        "context": map_context(nws_text_to_wmo(p.get("shortForecast"))),
        "icon": map_icon(nws_text_to_wmo(p.get("shortForecast")), is_day),

        "dewpoint_c": ceil1(dewpoint_c_raw),
        "dewpoint_f": ceil1(convert_temperature(dewpoint_c_raw, "C", "F")) if dewpoint_c_raw else None,
        "humidity": rh_raw,  # humidity should NOT be rounded

        "index": {
            "heat_index": ceil1(indexes_raw["heat_index"]),
            "wind_chill": ceil1(indexes_raw["wind_chill"]),
            "humidex": ceil1(indexes_raw["humidex"]),
            "wet_bulb": ceil1(indexes_raw["wet_bulb"]),
        },

        "feels_like_c": ceil1(fl_c_raw),
        "feels_like_f": ceil1(fl_f_raw),
        "feels_like_source": fl_src,  # NEVER ROUND THIS
    }

    return result, url
def fetch_weekly_nws(lat: float, lon: float, timeout: int, meta: Dict[str, Any]):
    url = build_nws_url(lat, lon, "weekly")
    headers = {"User-Agent": "NMS_Tools/1.0"}

    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()

    data = r.json()
    periods = data.get("properties", {}).get("periods", [])

    # Cached observation (raw values)
    obs = meta.get("cached_obs")
    if obs:
        dewpoint_c_obs = obs.get("dewpoint", {}).get("value")
        rh_obs = obs.get("relativeHumidity", {}).get("value")
        wind_obs_mps = obs.get("windSpeed", {}).get("value")
        wind_obs_kph = convert_speed(wind_obs_mps, "mps", "kph") if wind_obs_mps else None
    else:
        dewpoint_c_obs = None
        rh_obs = None
        wind_obs_kph = None

    normalized = []

    for p in periods:
        start = p.get("startTime")
        date_str = start.split("T")[0]
        date_obj = date.fromisoformat(date_str)
        now = datetime.fromisoformat(start)

        sunrise, sunset = compute_sun_times(lat, lon, date_obj, meta["timezone"])
        is_day = is_daylight(now, sunrise, sunset)

        # RAW temperature
        temp_c_raw = convert_temperature(p.get("temperature"), p.get("temperatureUnit"), "C")

        # RAW wind
        wind_kph_max_raw = convert_speed(parse_nws_speed(p.get("windSpeed")), "mph", "kph")

        # RAW humidity from period
        rh_period_raw = p.get("relativeHumidity", {}).get("value")

        # Effective humidity (raw)
        rh_effective_raw = rh_period_raw if rh_period_raw is not None else rh_obs

        # RAW dewpoint
        dewpoint_c_raw = dewpoint_c_obs

        # RAW wind for feels-like
        wind_kph_raw = wind_obs_kph or wind_kph_max_raw

        # Indexes (RAW values)
        idx_max_raw = compute_indexes_from_fields(
            temp_c=temp_c_raw,
            dewpoint_c=dewpoint_c_raw,
            rh=rh_effective_raw,
            wind_kph=wind_kph_raw,
        )

        idx_min_raw = compute_indexes_from_fields(
            temp_c=temp_c_raw,
            dewpoint_c=dewpoint_c_raw,
            rh=rh_effective_raw,
            wind_kph=wind_kph_raw,
        )

        # Unified feels-like (RAW values)
        fl_max_c_raw, fl_max_f_raw, fl_src = compute_feels_like(
            temp_c=temp_c_raw,
            dewpoint_c=dewpoint_c_raw,
            rh=rh_effective_raw,
            wind_kph=wind_kph_raw,
            is_day=is_day,
        )

        fl_min_c_raw, fl_min_f_raw, _ = compute_feels_like(
            temp_c=temp_c_raw,
            dewpoint_c=dewpoint_c_raw,
            rh=rh_effective_raw,
            wind_kph=wind_kph_raw,
            is_day=is_day,
        )

        # Presentation layer (CEILING ROUNDING)
        result = {
            "date": date_str,
            "sunrise": sunrise,
            "sunset": sunset,
            "condition": nws_text_to_wmo(p.get("shortForecast")),
            "context": map_context(nws_text_to_wmo(p.get("shortForecast"))),
            "icon": map_icon(nws_text_to_wmo(p.get("shortForecast")), is_day),

            "temp_max_c": ceil1(temp_c_raw),
            "temp_min_c": ceil1(temp_c_raw),
            "temp_max_f": ceil1(convert_temperature(temp_c_raw, "C", "F")),
            "temp_min_f": ceil1(convert_temperature(temp_c_raw, "C", "F")),

            "precip_mm": 0.0,
            "precip_in": 0.0,
            "precipitation_probability_max": p.get("probabilityOfPrecipitation", {}).get("value"),

            "wind_kph_max": ceil1(wind_kph_max_raw),
            "wind_mph_max": ceil1(convert_speed(wind_kph_max_raw, "kph", "mph")),

            "dewpoint_c": ceil1(dewpoint_c_raw),
            "dewpoint_f": ceil1(convert_temperature(dewpoint_c_raw, "C", "F")) if dewpoint_c_raw else None,

            # humidity MUST NOT be rounded
            "humidity": rh_effective_raw,

            "index": {
                "heat_index": ceil1(idx_max_raw["heat_index"]),
                "wind_chill": ceil1(idx_max_raw["wind_chill"]),
                "humidex": ceil1(idx_max_raw["humidex"]),
                "wet_bulb": ceil1(idx_max_raw["wet_bulb"]),
            },

            "feels_like_max_c": ceil1(fl_max_c_raw),
            "feels_like_max_f": ceil1(fl_max_f_raw),
            "feels_like_min_c": ceil1(fl_min_c_raw),
            "feels_like_min_f": ceil1(fl_min_f_raw),

            # NEVER ROUND THIS
            "feels_like_source": fl_src,
        }

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
    Normalize NWS observations/latest into unified schema.
    Adds:
      - full index set (heat_index, wind_chill, humidex, wet_bulb)
      - unified feels-like (C + F + source)
      - dewpoint/humidity/wind conversions
      - sunrise/sunset
      - context/icon
    """

    # Base fields from NWS obs
    temp_c = obs.get("temperature", {}).get("value")
    dewpoint_c = obs.get("dewpoint", {}).get("value")
    rh = obs.get("relativeHumidity", {}).get("value")

    wind_mps = obs.get("windSpeed", {}).get("value")
    wind_kph = convert_speed(wind_mps, "mps", "kph") if wind_mps else None
    wind_mph = convert_speed(wind_kph, "kph", "mph") if wind_kph else None

    pressure_pa = obs.get("barometricPressure", {}).get("value")
    pressure_hpa = pressure_pa / 100.0 if pressure_pa else None
    pressure_inhg = pressure_hpa * 0.02953 if pressure_hpa else None

    # Time + solar
    ts = obs.get("timestamp")
    now = datetime.fromisoformat(ts) if ts else datetime.now()

    date_obj = now.date()
    sunrise, sunset = compute_sun_times(lat, lon, date_obj, meta["timezone"])
    is_day = is_daylight(now, sunrise, sunset)

    # Condition → WMO
    condition = nws_text_to_wmo(obs.get("textDescription"))

    # Compute indexes
    indexes = compute_indexes_from_fields(
        temp_c=temp_c,
        dewpoint_c=dewpoint_c,
        rh=rh,
        wind_kph=wind_kph,
    )

    # Unified feels-like
    fl_c, fl_f, fl_src = compute_feels_like(
        temp_c=temp_c,
        dewpoint_c=dewpoint_c,
        rh=rh,
        wind_kph=wind_kph,
        is_day=is_day,
    )

    # Build result
    result = {
        "time": ts,
        "temperature_c": ceil1(temp_c),
        "temperature_f": ceil1(convert_temperature(temp_c, "C", "F")) if temp_c else None,

        "dewpoint_c": ceil1(dewpoint_c),
        "dewpoint_f": ceil1(convert_temperature(dewpoint_c, "C", "F")) if dewpoint_c else None,
        "humidity": ceil1(rh),

        "wind_kph": ceil1(wind_kph),
        "wind_mph": ceil1(wind_mph),

        "pressure_msl": ceil1(pressure_hpa),
        "pressure_inhg": ceil1(pressure_inhg),

        "sunrise": sunrise,
        "sunset": sunset,

        "condition": condition,
        "context": map_context(condition),
        "icon": map_icon(condition, is_day),

        # Full index set
        "index": indexes,

        # Unified feels-like
        "feels_like_c": ceil1(fl_c),
        "feels_like_f": ceil1(fl_f),
        "feels_like_source": fl_src,
    }

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
def fetch_observation_for_date(lat, lon, target_date, timeout, meta):
    obs, url, station_id = fetch_valid_nws_observation(lat, lon, timeout, meta)
    if not obs:
        return None

    ts = obs.get("timestamp")
    if not ts:
        return obs

    obs_date = ts.split("T")[0]
    if obs_date == target_date:
        return obs

    return obs  # nearest available
