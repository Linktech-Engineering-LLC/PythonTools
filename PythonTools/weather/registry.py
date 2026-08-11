# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-09
 File: PythonTools/weather/providers.py
 Version: 1.0.0
 Description: Module description here
"""

WEATHER_PROVIDERS = {
    "open-meteo": {
        "base": "https://api.open-meteo.com/v1/forecast",
        "supports": ["current", "hourly", "weekly"],
    },
    "nws": {
        "base": "https://api.weather.gov",
        "supports": ["current", "hourly", "weekly", "alerts"],
    }
}
