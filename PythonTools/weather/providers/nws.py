# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-10
 Modified: 2026-08-20
 File: PythonTools/weather/providers/nws.py
 Version: 1.0.0
 Description: Weather Provider NWS functions
"""

import requests
from datetime import date, datetime
from typing import Any, Dict

from .builders import build_nws_url, build_nws_alerts_url
from ..codes import nws_text_to_wmo, map_icon, map_context
from ...datetime import (
    compute_sun_times, 
    is_daylight, 
    normalize_ts_local, 
    moon_phase_info,
    compute_moon_times
)
from ..registry import WEATHER_PROVIDERS
from ..indexes import (
    convert_speed, 
    convert_temperature, 
    compute_feels_like, 
    compute_indexes_from_fields,
)
from ..normalize import (
    normalize_index_fields, 
    normalize_gusts_kph_mph,
    infer_precip_type,
    infer_precip_components,
)
from .open_meteo import fetch_weekly_open_meteo, fetch_hourly_open_meteo
from ...units import haversine, convert_distance
from ...utils import ceil1

def fetch_hourly_nws(lat, lon, timeout, meta):
    #
    # 0. Cached observation fallback
    #
    obs = meta.get("cached_obs")
    obs_url = meta.get("cached_obs_url")

    #
    # 1. Fetch NWS hourly forecast
    #
    url = build_nws_url(lat, lon, "hourly")
    raw = requests.get(url, timeout=timeout).json()
    periods = raw["properties"]["periods"]

    #
    # 2. Fetch Open‑Meteo hourly (precipitation + weathercode)
    #
    om_hourly, om_url = fetch_hourly_open_meteo(lat, lon, timeout, meta)
    # om_hourly["hours"] contains:
    #   time, precipitation, precipitation_probability, weathercode, etc.

    om_by_time = {
        normalize_ts_local(h["time"], meta["timezone"]): h
        for h in om_hourly.get("hours", [])
    }

    normalized = []

    #
    # 3. Merge NWS hourly + Open‑Meteo hourly precipitation
    #
    for p in periods:
        start = p.get("startTime")
        ct = datetime.fromisoformat(start)
        date_str = start.split("T")[0]
        date_obj = date.fromisoformat(date_str)
        moon = moon_phase_info(date_str)
        moonrise, moonset = compute_moon_times(lat, lon, date_obj, meta["timezone"])
        sunrise, sunset = compute_sun_times(lat, lon, date_obj, meta["timezone"])
        is_day = is_daylight(ct, sunrise, sunset)

        #
        # NWS hourly base fields
        #
        temp_c = ceil1(convert_temperature(p.get("temperature"), p.get("temperatureUnit"), "C"))
        temp_f = ceil1(convert_temperature(temp_c, "C", "F"))

        dewpoint_c = p.get("dewpoint", {}).get("value")
        rh = p.get("relativeHumidity", {}).get("value")
        precip_prob_nws = p.get("probabilityOfPrecipitation", {}).get("value")
        precip_type_nws = infer_precip_type(nws_text_to_wmo(p.get("shortForecast")))

        wind_kph = convert_speed(parse_nws_speed(p.get("windSpeed")), "mph", "kph")
        wind_mph = convert_speed(wind_kph, "kph", "mph")
        gust_raw = p.get("windGust")
        gust_kph, gust_mph = normalize_gusts_kph_mph(gust_raw)

        #
        # Observation fallback
        #
        if obs:
            if dewpoint_c is None:
                dewpoint_c = obs.get("dewpoint", {}).get("value")

            if rh is None:
                rh = obs.get("relativeHumidity", {}).get("value")

            if wind_kph is None:
                wind_mps_obs = obs.get("windSpeed", {}).get("value")
                if wind_mps_obs is not None:
                    wind_kph = convert_speed(wind_mps_obs, "mps", "kph")
                    wind_mph = convert_speed(wind_kph, "kph", "mph")

        dewpoint_c = ceil1(dewpoint_c) if dewpoint_c is not None else None
        rh = ceil1(rh) if rh is not None else None
        wind_kph = ceil1(wind_kph) if wind_kph is not None else None
        wind_mph = ceil1(wind_mph) if wind_mph is not None else None

        #
        # 4. Open‑Meteo hourly precipitation for this time
        #
        om = om_by_time.get(normalize_ts_local(start, meta["timezone"]), {})

        precip_mm = om.get("precip_mm")
        weathercode = om.get("condition")
        precip_prob_om = om.get("precipitation_probability")

        # infer rain/snow/ice components
        components = infer_precip_components(weathercode, precip_mm)

        #
        # 5. Indexes
        #
        pressure_pa = obs.get("barometricPressure", {}).get("value") if obs else None
        pressure_hpa = pressure_pa / 100 if pressure_pa is not None else None

        indexes = compute_indexes_from_fields(
            temp_c=temp_c,
            dewpoint_c=dewpoint_c,
            rh=rh,
            wind_kph=wind_kph,
            pressure_hpa=pressure_hpa,
        )

        #
        # 6. Unified feels-like
        #
        fl_c, fl_f, fl_src = compute_feels_like(
            temp_c=temp_c,
            dewpoint_c=dewpoint_c,
            rh=rh,
            wind_kph=wind_kph,
            is_day=is_day,
        )

        #
        # 7. Final merged hourly record
        #
        result = {
            "time": start,

            "temperature_c": temp_c,
            "temperature_f": temp_f,

            "dewpoint_c": dewpoint_c,
            "dewpoint_f": ceil1(convert_temperature(dewpoint_c, "C", "F")) if dewpoint_c else None,
            "humidity": rh,

            #
            # Open‑Meteo precipitation amounts
            #
            "precip_amount": precip_mm,
            "precip_mm": precip_mm,
            "precip_in": precip_mm / 25.4 if precip_mm is not None else None,

            "rain_mm": components["rain_mm"],
            "snow_mm": components["snow_mm"],
            "ice_mm": components["ice_mm"],

            #
            # Precipitation probability + type
            #
            "precip_probability": precip_prob_nws or precip_prob_om,
            "precip_type": precip_type_nws,

            "wind_kph": wind_kph,
            "wind_mph": wind_mph,
            "wind_gust_kph": gust_kph,
            "wind_gust_mph": gust_mph,

            "sunrise": sunrise,
            "sunset": sunset,
            "moon_phase": moon["moon_phase"],
            "moon_phase_code": moon["moon_phase_code"],
            "moon_illumination": moon["moon_illumination"],
            "moonrise": moonrise,
            "moonset": moonset,
            "condition": nws_text_to_wmo(p.get("shortForecast")),
            "context": map_context(nws_text_to_wmo(p.get("shortForecast"))),
            "icon": map_icon(nws_text_to_wmo(p.get("shortForecast")), is_day),

            "index": normalize_index_fields(indexes),

            "feels_like_c": ceil1(fl_c),
            "feels_like_f": ceil1(fl_f),
            "feels_like_source": fl_src,
        }

        normalized.append(result)

    return {"hours": normalized}, (obs_url or url)
def fetch_current_nws(lat: float, lon: float, timeout: int, meta: Dict[str, Any]):
    headers = {"User-Agent": "NMS_Tools/1.0"}

    #
    # 1. Try NWS observations/latest (real station data)
    #
    try:
        obs, obs_url, station_id = fetch_valid_nws_observation(lat, lon, timeout, meta)
    except Exception:
        obs = None
        obs_url = None
        station_id = None

    #
    # 2. Fetch NWS forecastHourly (for context, precip probability, weathercode)
    #
    url_fc = build_nws_url(lat, lon, "current")
    r_fc = requests.get(url_fc, headers=headers, timeout=timeout)
    r_fc.raise_for_status()

    data_fc = r_fc.json()
    periods = data_fc.get("properties", {}).get("periods", [])
    fc = periods[0] if periods else None

    #
    # 3. Fetch Open‑Meteo hourly (for precip amount, visibility, cloud cover)
    #
    om_hourly, om_url = fetch_hourly_open_meteo(lat, lon, timeout, meta)
    tz = meta["timezone"]

    # Normalize OM timestamps to local time
    om_by_time = {
        normalize_ts_local(h["time"], tz): h
        for h in om_hourly.get("hours", [])
    }

    # Determine the timestamp we want to match
    if fc:
        start = fc.get("startTime")
    elif obs:
        start = obs.get("timestamp")
    else:
        return None, url_fc

    om = om_by_time.get(normalize_ts_local(start, tz), {})

    #
    # 4. Extract fields from NWS observation (if available)
    #
    if obs:
        temp_c_raw = obs.get("temperature", {}).get("value")
        dewpoint_c_raw = obs.get("dewpoint", {}).get("value")
        rh_raw = obs.get("relativeHumidity", {}).get("value")
        wind_mps_raw = obs.get("windSpeed", {}).get("value")
        pressure_pa = obs.get("barometricPressure", {}).get("value")
        precip_mm_raw = obs.get("precipitationLastHour", {}).get("value")
    else:
        temp_c_raw = None
        dewpoint_c_raw = None
        rh_raw = None
        wind_mps_raw = None
        pressure_pa = None
        precip_mm_raw = None

    #
    # 5. Fill missing fields using forecastHourly
    #
    if fc:
        if temp_c_raw is None:
            temp_c_raw = convert_temperature(fc["temperature"], fc["temperatureUnit"], "C")

        if dewpoint_c_raw is None:
            dewpoint_c_raw = fc.get("dewpoint", {}).get("value")

        if rh_raw is None:
            rh_raw = fc.get("relativeHumidity", {}).get("value")

        if wind_mps_raw is None:
            wind_mps_raw = parse_nws_speed(fc.get("windSpeed"))

    #
    # 6. Fill missing precipitation using Open‑Meteo
    #
    if precip_mm_raw is None:
        precip_mm_raw = om.get("precip_mm")

    precip_in_raw = precip_mm_raw / 25.4 if precip_mm_raw is not None else None

    #
    # 7. Convert wind
    #
    wind_kph_raw = convert_speed(wind_mps_raw, "mps", "kph") if wind_mps_raw is not None else None
    wind_mph_raw = convert_speed(wind_kph_raw, "kph", "mph") if wind_kph_raw is not None else None

    #
    # 8. Sunrise/sunset
    #
    date_str = start.split("T")[0]
    date_obj = date.fromisoformat(date_str)
    sunrise, sunset = compute_sun_times(lat, lon, date_obj, tz)
    moonrise, moonset = compute_moon_times(lat, lon, date_obj, meta["timezone"])
    moon = moon_phase_info(date_str)
    is_day = is_daylight(datetime.fromisoformat(start), sunrise, sunset)

    #
    # 9. Indexes (RAW)
    #
    pressure_hpa = pressure_pa / 100 if pressure_pa is not None else None

    indexes_raw = compute_indexes_from_fields(
        temp_c=temp_c_raw,
        dewpoint_c=dewpoint_c_raw,
        rh=rh_raw,
        wind_kph=wind_kph_raw,
        pressure_hpa=pressure_hpa,
    )

    #
    # 10. Feels-like (RAW)
    #
    fl_c_raw, fl_f_raw, fl_src = compute_feels_like(
        temp_c=temp_c_raw,
        dewpoint_c=dewpoint_c_raw,
        rh=rh_raw,
        wind_kph=wind_kph_raw,
        is_day=is_day,
    )

    #
    # 11. Weather code + context from forecastHourly
    #
    if fc:
        wmo = nws_text_to_wmo(fc.get("shortForecast"))
    else:
        wmo = None

    #
    # 12. Final merged current record
    #
    result = {
        "time": start,

        "temperature_c": ceil1(temp_c_raw),
        "temperature_f": ceil1(convert_temperature(temp_c_raw, "C", "F")),

        "dewpoint_c": ceil1(dewpoint_c_raw),
        "dewpoint_f": ceil1(convert_temperature(dewpoint_c_raw, "C", "F")) if dewpoint_c_raw else None,

        "humidity": ceil1(rh_raw),

        "wind_kph": ceil1(wind_kph_raw),
        "wind_mph": ceil1(wind_mph_raw),

        "sunrise": sunrise,
        "sunset": sunset,
        "moon_phase": moon["moon_phase"],
        "moon_phase_code": moon["moon_phase_code"],
        "moon_illumination": moon["moon_illumination"],
        "moonrise": moonrise,
        "moonset": moonset,
        "condition": wmo,
        "context": map_context(wmo),
        "icon": map_icon(wmo, is_day),

        #
        # Precipitation (merged)
        #
        "precip_mm": ceil1(precip_mm_raw) if precip_mm_raw is not None else None,
        "precip_in": ceil1(precip_in_raw) if precip_in_raw is not None else None,
        "precip_probability": fc.get("probabilityOfPrecipitation", {}).get("value") if fc else None,
        "precip_type": infer_precip_type(wmo),

        #
        # Indexes
        #
        "index": normalize_index_fields(indexes_raw),

        #
        # Feels-like
        #
        "feels_like_c": ceil1(fl_c_raw),
        "feels_like_f": ceil1(fl_f_raw),
        "feels_like_source": fl_src,
    }

    if station_id:
        result["station_id"] = station_id

    return result, (obs_url or url_fc or om_url)
def fetch_weekly_nws(lat: float, lon: float, timeout: int, meta: Dict[str, Any]):
    #
    # 1. Fetch NWS weekly forecast (temperature, wind, humidity, etc.)
    #
    url = build_nws_url(lat, lon, "weekly")
    headers = {"User-Agent": "NMS_Tools/1.0"}

    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()

    data = r.json()
    periods = data.get("properties", {}).get("periods", [])

    #
    # 2. Fetch Open-Meteo weekly precipitation
    #
    om_precip, om_url = fetch_weekly_open_meteo(lat, lon, timeout, meta)
    # om_precip = { "days": [ { "date": "...", "precip_mm": ..., "snow_mm": ..., ... }, ... ] }

    # Convert Open-Meteo list into dict keyed by date
    om_daily = {d["date"]: d for d in om_precip.get("days", [])}

    #
    # 3. Cached observation fallback (raw values)
    #
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

    #
    # 4. Merge NWS weekly + Open-Meteo precipitation
    #
    for p in periods:
        start = p.get("startTime")
        date_str = start.split("T")[0]
        date_obj = date.fromisoformat(date_str)
        ct = datetime.fromisoformat(start)
        moon = moon_phase_info(date_str)
        moonrise, moonset = compute_moon_times(lat, lon, date_obj, meta["timezone"])

        sunrise, sunset = compute_sun_times(lat, lon, date_obj, meta["timezone"])
        is_day = is_daylight(ct, sunrise, sunset)

        #
        # RAW temperature
        #
        temp_c_raw = convert_temperature(p.get("temperature"), p.get("temperatureUnit"), "C")

        #
        # RAW wind
        #
        wind_kph_max_raw = convert_speed(parse_nws_speed(p.get("windSpeed")), "mph", "kph")
        gust_raw = p.get("windGust")
        gust_kph, gust_mph = normalize_gusts_kph_mph(gust_raw)

        #
        # RAW humidity from period
        #
        rh_period_raw = p.get("relativeHumidity", {}).get("value")
        rh_effective_raw = rh_period_raw if rh_period_raw is not None else rh_obs

        #
        # RAW dewpoint
        #
        dewpoint_c_raw = dewpoint_c_obs

        #
        # RAW wind for feels-like
        #
        wind_kph_raw = wind_obs_kph or wind_kph_max_raw
        pressure_pa = obs.get("barometricPressure", {}).get("value") if obs else None
        pressure_hpa = pressure_pa / 100 if pressure_pa is not None else None

        #
        # Indexes (RAW values)
        #
        idx_max_raw = compute_indexes_from_fields(
            temp_c=temp_c_raw,
            dewpoint_c=dewpoint_c_raw,
            rh=rh_effective_raw,
            wind_kph=wind_kph_raw,
            pressure_hpa=pressure_hpa,
        )

        idx_min_raw = compute_indexes_from_fields(
            temp_c=temp_c_raw,
            dewpoint_c=dewpoint_c_raw,
            rh=rh_effective_raw,
            wind_kph=wind_kph_raw,
            pressure_hpa=pressure_hpa,
        )

        #
        # Unified feels-like (RAW values)
        #
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

        #
        # 5. Open-Meteo precipitation for this date
        #
        om = om_daily.get(date_str, {})

        precip_mm = om.get("precip_mm")
        snow_mm = om.get("snow_mm")
        ice_mm = om.get("ice_mm")
        precip_prob = om.get("precipitation_probability_max")
        precip_type = om.get("precip_type")

        #
        # Presentation layer (CEILING ROUNDING)
        #
        condition = nws_text_to_wmo(p.get("shortForecast"))

        result = {
            "date": date_str,
            "sunrise": sunrise,
            "sunset": sunset,
            "moon_phase": moon["moon_phase"],
            "moon_phase_code": moon["moon_phase_code"],
            "moon_illumination": moon["moon_illumination"],
            "moonrise": moonrise,
            "moonset": moonset,
            "condition": condition,
            "context": map_context(condition),
            "icon": map_icon(condition, is_day),

            "temp_max_c": ceil1(temp_c_raw),
            "temp_min_c": ceil1(temp_c_raw),
            "temp_max_f": ceil1(convert_temperature(temp_c_raw, "C", "F")),
            "temp_min_f": ceil1(convert_temperature(temp_c_raw, "C", "F")),

            #
            # Open-Meteo precipitation (rounded)
            #
            "precip_mm": ceil1(precip_mm) if precip_mm is not None else None,
            "precip_in": ceil1(convert_distance(precip_mm, "mm", "in")) if precip_mm is not None else None,

            "snow_mm": ceil1(snow_mm) if snow_mm is not None else None,
            "snow_in": ceil1(convert_distance(snow_mm, "mm", "in")) if snow_mm is not None else None,

            "ice_mm": ceil1(ice_mm) if ice_mm is not None else None,
            "ice_in": ceil1(convert_distance(ice_mm, "mm", "in")) if ice_mm is not None else None,

            "precipitation_probability_max": precip_prob,
            "precip_type": precip_type,

            #
            # Wind
            #
            "wind_kph_max": ceil1(wind_kph_max_raw),
            "wind_mph_max": ceil1(convert_speed(wind_kph_max_raw, "kph", "mph")),
            "wind_gust_kph": gust_kph,
            "wind_gust_mph": gust_mph,

            #
            # Dewpoint / humidity
            #
            "dewpoint_c": ceil1(dewpoint_c_raw),
            "dewpoint_f": ceil1(convert_temperature(dewpoint_c_raw, "C", "F")) if dewpoint_c_raw else None,
            "humidity": rh_effective_raw,  # MUST NOT be rounded

            #
            # Indexes
            #
            "index": normalize_index_fields(idx_max_raw),

            #
            # Feels-like
            #
            "feels_like_max_c": ceil1(fl_max_c_raw),
            "feels_like_max_f": ceil1(fl_max_f_raw),
            "feels_like_min_c": ceil1(fl_min_c_raw),
            "feels_like_min_f": ceil1(fl_min_f_raw),
            "feels_like_source": fl_src,
        }

        normalized.append(result)

    return {"days": normalized}, url
def fetch_full_nws(lat: float, lon: float, timeout: int, meta: Dict[str, Any]):
    # 1. Fetch current
    current, current_url = fetch_current_nws(lat, lon, timeout, meta)

    # 2. Fetch hourly
    hourly, hourly_url = fetch_hourly_nws(lat, lon, timeout, meta)

    # 3. Fetch weekly
    weekly, weekly_url = fetch_weekly_nws(lat, lon, timeout, meta)

    # 4. Build unified provider block
    return {
        "current": current,
        "hourly": hourly,
        "weekly": weekly,
        "provider": "nws",
        "urls": {
            "current": current_url,
            "hourly": hourly_url,
            "weekly": weekly_url
        }
    }
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
    ct = datetime.fromisoformat(ts) if ts else datetime.now()

    date_obj = ct.date()
    sunrise, sunset = compute_sun_times(lat, lon, date_obj, meta["timezone"])
    is_day = is_daylight(ct, sunrise, sunset)

    # Condition → WMO
    condition = nws_text_to_wmo(obs.get("textDescription"))

    # Compute indexes
    indexes = compute_indexes_from_fields(
        temp_c=temp_c,
        dewpoint_c=dewpoint_c,
        rh=rh,
        wind_kph=wind_kph,
        pressure_hpa=pressure_hpa,
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
        "index": normalize_index_fields(indexes),

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

    # Must have wind speed (0 is acceptable)
    wind_mps = obs.get("windSpeed", {}).get("value")
    if wind_mps is None:
        return False

    # Optional sanity checks (non-fatal)
    dew = obs.get("dewpoint", {}).get("value")
    if dew is not None:
        if dew < -60 or dew > 40:
            return False
        if dew > temp:
            return False

    rh = obs.get("relativeHumidity", {}).get("value")
    if rh is not None and (rh < 0 or rh > 100):
        return False

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
def fetch_gridpoint_nws(lat: float, lon: float, timeout: int, meta: dict):
    """
    Fetch NWS Gridpoint forecastGridData for precipitation amounts.
    Requires meta to contain: office, gridX, gridY.
    """

    office = meta["office"]
    gridX = meta["gridX"]
    gridY = meta["gridY"]

    url = f"https://api.weather.gov/gridpoints/{office}/{gridX},{gridY}/forecastGridData"
    headers = {"User-Agent": "NMS_Tools/1.0"}

    r = requests.get(url, headers=headers, timeout=timeout)
    r.raise_for_status()

    data = r.json().get("properties", {})

    return {
        "quant_precip": data.get("quantitativePrecipitation", {}).get("values", []),
        "snowfall": data.get("snowfallAmount", {}).get("values", []),
        "ice": data.get("iceAccumulation", {}).get("values", []),
        "pop": data.get("probabilityOfPrecipitation", {}).get("values", []),
        "weather": data.get("weather", {}).get("values", []),
    }, url
def parse_nws_speed(s: str | None) -> float | None:
    """
    Parse NWS windSpeed strings like:
    - "7 mph"
    - "10 to 15 mph"
    - "Calm"
    - "Light"
    - "Variable"
    - None
    Returns speed in mph (float) or None.
    """

    if not s:
        return None

    s = s.strip().lower()

    # Calm / Light / Variable → treat as 0 mph
    if s in ("calm", "light", "variable"):
        return 0.0

    # Range: "10 to 15 mph"
    if "to" in s:
        parts = s.replace("mph", "").strip().split("to")
        try:
            low = float(parts[0].strip())
            high = float(parts[1].strip())
            return (low + high) / 2.0
        except:
            return None

    # Single value: "7 mph"
    if "mph" in s:
        try:
            return float(s.replace("mph", "").strip())
        except:
            return None

    # Unknown format
    return None
