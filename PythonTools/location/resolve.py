# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-11
 Modified: 2026-08-11
 File: PythonTools/location/resolve.py
 Version: 1.0.0
 Description: Module description here
"""

# PythonTools/location/resolve.py

import requests
from .normalize import normalize_city, normalize_country, normalize_state
from .us_states import US_STATES
from .providers import ProviderError, build_location_url
from .geo_types import LocationInfo, GeoPoint


class LocationNotFoundError(Exception):
    pass

def _try_latlon(query: str):
    """Detect and parse lat/long."""
    if "," not in query:
        return None

    parts = query.split(",", 1)
    try:
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        return LocationInfo(
            query=query,
            provider="direct",
            point=GeoPoint(lat, lon),
            city=None,
            state=None,
            country=None,
            zip=None,
            url=None,
        )
    except ValueError:
        return None


def _try_zip(country: str, zip_code: str, timeout: float):
    """ZIP → Zippopotam.us lookup."""
    if not zip_code.isdigit():
        return None

    url = build_location_url("zippopotam.us", "zip", country=country, zip=zip_code)
    r = requests.get(url, timeout=timeout)

    if r.status_code != 200:
        return None

    data = r.json()
    place = data["places"][0]

    return LocationInfo(
        query=zip_code,
        provider="zippopotam.us",
        point=GeoPoint(float(place["latitude"]), float(place["longitude"])),
        city=place["place name"],
        state=place.get("state"),
        country=country,
        zip=zip_code,
        url=url,
    )


def _try_open_meteo_global(city: str, timeout: float):
    url = build_location_url("open-meteo-geocode", "global", city=city)
    r = requests.get(url, timeout=timeout)

    if r.status_code != 200:
        return None

    results = r.json().get("results", [])
    if not results:
        return None

    entry = results[0]
    return LocationInfo(
        query=city,
        provider="open-meteo",
        point=GeoPoint(entry["latitude"], entry["longitude"]),
        city=entry.get("name"),
        state=entry.get("admin1"),
        country=entry.get("country"),
        zip=None,
        url=url,
    )


def _try_open_meteo_country(city: str, country: str, timeout: float):
    url = build_location_url("open-meteo-geocode", "country", city=city, country=country)
    r = requests.get(url, timeout=timeout)

    if r.status_code != 200:
        return None

    results = r.json().get("results", [])
    if not results:
        return None

    entry = results[0]
    return LocationInfo(
        query=city,
        provider="open-meteo",
        point=GeoPoint(entry["latitude"], entry["longitude"]),
        city=entry.get("name"),
        state=entry.get("admin1"),
        country=country,
        zip=None,
        url=url,
    )


def _try_zippopotam_city(country: str, city: str, timeout: float):
    url = build_location_url("zippopotam.us", "city", country=country, city=city)
    r = requests.get(url, timeout=timeout)

    if r.status_code != 200:
        return None

    data = r.json()
    place = data["places"][0]

    return LocationInfo(
        query=city,
        provider="zippopotam.us",
        point=GeoPoint(float(place["latitude"]), float(place["longitude"])),
        city=place["place name"],
        state=place.get("state"),
        country=country,
        zip=data.get("post code"),
        url=url,
    )


def resolve_location(query: str, country: str = "US", timeout: float = 5.0):
    """
    Provider-agnostic geolocation resolver.
    Returns LocationInfo or raises LocationNotFoundError.
    """

    query = query.strip()
    country = normalize_country(country)

    # 1. Lat/Long
    latlon = _try_latlon(query)
    if latlon:
        return latlon

    # 2. ZIP
    zip_result = _try_zip(country, query, timeout)
    if zip_result:
        return zip_result

    # 3. City/state split
    parts = [p.strip() for p in query.split(",")]
    city = normalize_city(parts[0])

    state_filter = None
    if len(parts) >= 2:
        raw_state = parts[1].strip()
        upper = raw_state.upper()
        state_filter = US_STATES.get(upper, raw_state)

    # 4. Global Open-Meteo search
    global_result = _try_open_meteo_global(city, timeout)
    if global_result:
        if state_filter:
            if global_result.state and global_result.state.upper().startswith(state_filter.upper()):
                return global_result
        else:
            return global_result

    # 5. Country-filtered Open-Meteo search
    country_result = _try_open_meteo_country(city, country, timeout)
    if country_result:
        return country_result

    # 6. Zippopotam city fallback
    zip_city = _try_zippopotam_city(country, city, timeout)
    if zip_city:
        return zip_city

    raise LocationNotFoundError(query)
