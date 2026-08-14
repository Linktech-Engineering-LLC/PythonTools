# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-14
 File: PythonTools/weather/types.py
 Version: 1.0.0
 Description: Weather defined types
"""

# PythonTools/weather/indexes.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from ..utils.common import ceil1

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

def normalize_index_fields(idx: dict) -> dict:
    return {
        "heat_index": ceil1(idx.get("heat_index")),
        "wind_chill": ceil1(idx.get("wind_chill")),
        "humidex": ceil1(idx.get("humidex")),
        "wet_bulb": ceil1(idx.get("wet_bulb")),

        "vapor_pressure": ceil1(idx.get("vapor_pressure")),
        "saturation_vapor_pressure": ceil1(idx.get("saturation_vapor_pressure")),
        "mixing_ratio": ceil1(idx.get("mixing_ratio")),
        "specific_humidity": ceil1(idx.get("specific_humidity")),
        "air_density": ceil1(idx.get("air_density")),
        "pressure_altitude": ceil1(idx.get("pressure_altitude")),
    }

