# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-09
 File: PythonTools/weather/__init__.py
 Version: 1.0.0
 Description: Module description here
"""

from .builders import build_nws_url, build_open_meteo_url
from .codes import WEATHER_CODES
from .formatters import fmt_clouds, fmt_precip, fmt_temp, fmt_wind
from .normalize import convert_units_mode_aware
from .providers import WEATHER_PROVIDERS
from .provider_open_meteo import fetch_weekly_open_meteo, fetch_hourly_open_meteo, fetch_current_open_meteo
from .provider_nws import fetch_hourly_nws, fetch_current_nws, fetch_weekly_nws, resolve_nws_meta
from .register import register_providers

__all__ = [
    "WEATHER_PROVIDERS",
    "build_nws_url",
    "build_open_meteo_url",
    "fetch_weekly_open_meteo",
    "fetch_hourly_open_meteo",
    "fetch_current_open_meteo",
    "fetch_hourly_nws",
    "fetch_current_nws",
    "fetch_weekly_nws",
    "resolve_nws_meta",
    "convert_units_mode_aware",
    "register_providers",
    "fmt_clouds",
    "fmt_wind",
    "fmt_precip",
    "fmt_temp",
]