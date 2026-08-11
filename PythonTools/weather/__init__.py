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

from .codes import WEATHER_CODES, map_context, map_icon
from .formatters import fmt_clouds, fmt_precip, fmt_temp, fmt_wind
from .indexes import (
    compute_all_indexes,
    compute_heat_index,
    compute_humidex,
    compute_wet_bulb,
    compute_wind_chill,
    WeatherIndexes,
    compute_indexes_from_fields,
)
from .normalize import convert_units_mode_aware
from .registry import WEATHER_PROVIDERS

__all__ = [
    "WEATHER_PROVIDERS",
    "convert_units_mode_aware",
    "fmt_clouds",
    "fmt_wind",
    "fmt_precip",
    "fmt_temp",
    "compute_indexes_from_fields",
    "map_context",
    "map_icon",
]