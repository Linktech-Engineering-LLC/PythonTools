# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-16
 File: PythonTools/weather/types.py
 Version: 1.0.0
 Description: Weather defined types
"""

# PythonTools/weather/indexes.py

from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class WeatherIndexes:
    heat_index: float | None = None
    wind_chill: float | None = None
    humidex: float | None = None
    wet_bulb: float | None = None

    vapor_pressure: float | None = None
    saturation_vapor_pressure: float | None = None
    mixing_ratio: float | None = None
    specific_humidity: float | None = None
    air_density: float | None = None
    pressure_altitude: float | None = None

@dataclass(frozen=True)
class Precipitation:
    precip_amount: float | str | None = None
    precip_probability: int | None = None
    precip_type: str | None = None

    hourly_precip_amount: float | str | None = None
    hourly_precip_probability: int | None = None
    hourly_precip_type: str | None = None

    precip_total: float | str | None = None
    precip_probability_max: int | None = None
    rain_total: float | str | None = None
    snow_total: float | str | None = None
    ice_total: float | str | None = None
   

