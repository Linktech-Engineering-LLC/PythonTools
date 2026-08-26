# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-26
 File: PythonTools/location/providers.py
 Version: 1.0.0
 Description: Module description here
"""

import json
import urllib.request

from .geo_types import LocationInfo, GeoPoint
from ..net.http import http_get_json


class ProviderError(Exception):
    pass

LOCATION_PROVIDERS = {
    "zippopotam.us": {
        "base": "https://api.zippopotam.us",
        "endpoints": {
            "zip": "{base}/{country}/{zip}",
            "city": "{base}/{country}/{city}",
        }
    },

    "open-meteo-geocode": {
        "base": "https://geocoding-api.open-meteo.com/v1/search",
        "endpoints": {
            "global": "{base}?name={city}",
            "country": "{base}?name={city}&country={country}",
        }
    }
}
def build_location_url(provider: str, endpoint: str, **kwargs) -> str:
    info = LOCATION_PROVIDERS.get(provider)
    if not info:
        raise ProviderError(f"Unknown location provider: {provider}")

    ep = info["endpoints"].get(endpoint)
    if not ep:
        raise ProviderError(f"Unknown endpoint '{endpoint}' for provider '{provider}'")

    return ep.format(base=info["base"], **kwargs)


def reverse_geocode(lat: float, lon: float, timeout: float = 5.0):
    url = (
        "https://nominatim.openstreetmap.org/reverse"
        f"?lat={lat}&lon={lon}&format=json&addressdetails=1"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "PythonTools/1.0"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception:
        return None

    addr = data.get("address", {})

    return LocationInfo(
        query=f"{lat},{lon}",
        provider="nominatim",
        point=GeoPoint(lat, lon),
        city=addr.get("city") or addr.get("town") or addr.get("village"),
        state=addr.get("state"),
        country=addr.get("country"),
        zip=addr.get("postcode"),
        url=url,
    )
