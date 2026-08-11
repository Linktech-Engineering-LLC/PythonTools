# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-09
 File: PythonTools/weather/providers/register.py
 Version: 1.0.0
 Description: Registers the WEATHER_PROVIDERS executables
"""

from ..registry import WEATHER_PROVIDERS
from .open_meteo import fetch_full_open_meteo, fetch_current_open_meteo, fetch_hourly_open_meteo, fetch_weekly_open_meteo
from .nws import fetch_full_nws, fetch_weekly_nws, fetch_hourly_nws, fetch_current_nws

def register_providers():
    WEATHER_PROVIDERS["open-meteo"].update({
        "fetch_current": fetch_current_open_meteo,
        "fetch_hourly": fetch_hourly_open_meteo,
        "fetch_weekly": fetch_weekly_open_meteo,
        "fetch_full": fetch_full_open_meteo,
    })

    WEATHER_PROVIDERS["nws"].update({
        "fetch_current": fetch_current_nws,
        "fetch_hourly": fetch_hourly_nws,
        "fetch_weekly": fetch_weekly_nws,
        "fetch_full": fetch_full_nws,
    })
