# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-03
 File: PythonTools/location/providers.py
 Version: 1.0.0
 Description: Module description here
"""

PROVIDERS = {
    "zippopotam.us": {
        "type": "geolocation",
        "url": "https://api.zippopotam.us",
    },
    "open-meteo": {
        "type": "weather",
        "url": "https://api.open-meteo.com/v1/forecast",
    },
    "nws": {
        "type": "weather",
        "url": "https://api.weather.gov",
    }
    # Add more providers here
}
