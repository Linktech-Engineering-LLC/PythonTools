# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-15
 File: PythonTools/weather/types.py
 Version: 1.0.0
 Description: Weather defined types
"""

# PythonTools/weather/indexes.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class WeatherIndexes:
    heat_index: Optional[float]
    wind_chill: Optional[float]
    humidex: Optional[float]
    wet_bulb: Optional[float]

    vapor_pressure: Optional[float]
    saturation_vapor_pressure: Optional[float]
    mixing_ratio: Optional[float]
    specific_humidity: Optional[float]
    air_density: Optional[float]
    pressure_altitude: Optional[float]


