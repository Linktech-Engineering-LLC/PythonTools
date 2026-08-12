# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-12
 File: PythonTools/weather/indexes.py
 Version: 1.0.0
 Description: Weather Indexes Module

Provider‑agnostic computation of meteorological indexes:
    - Heat Index (NWS formula)
    - Wind Chill (NWS formula)
    - Humidex
    - Wet Bulb Temperature (Stull approximation)

All functions are deterministic, freeze‑safe, and require only
basic Python math operations. No external dependencies.
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


