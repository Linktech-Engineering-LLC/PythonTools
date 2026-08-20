# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-20
 File: PythonTools/weather/__init__.py
 Version: 1.0.0
 Description: Module description here
"""

from .alerts import normalize_alerts, fetch_cached_alerts
from .codes import WEATHER_CODES, map_context, map_icon
from .formatters import fmt_clouds, fmt_precip, fmt_temp, fmt_wind
from .normalize import (
    convert_units_mode_aware,
    normalize_index_fields,
    merge_daily_periods,
    reorder_hourly_current_first,
    normalize_gusts_kph_mph,
    normalize_gridpoint_precip,
    infer_precip_type,
    map_precipitation,
    infer_precip_components,
)
from .registry import WEATHER_PROVIDERS
from .types import WeatherIndexes, Precipitation
from .indexes import (
    compute_feels_like,
    compute_heat_index,
    compute_wind_chill,
    compute_humidex,
    compute_wet_bulb,
    compute_mixing_ratio,
    compute_indexes_from_fields,
)

__all__ = [
    "WEATHER_PROVIDERS",
    "convert_units_mode_aware",
    "fmt_clouds",
    "fmt_wind",
    "fmt_precip",
    "fmt_temp",
    "map_context",
    "map_icon",
    "WeatherIndexes",
    "compute_heat_index",
    "compute_wind_chill",
    "compute_humidex",
    "compute_wet_bulb",
    "compute_feels_like",
    "compute_indexes_from_fields",
    "normalize_index_fields",
    "fetch_cached_alerts",
    "normalize_alerts",
    "merge_daily_periods",
    "reorder_hourly_current_first",
]