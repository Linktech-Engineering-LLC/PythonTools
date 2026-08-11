# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-11
 File: PythonTools/location/providers.py
 Version: 1.0.0
 Description: Module description here
"""

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
