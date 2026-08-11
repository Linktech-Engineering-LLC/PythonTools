# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-09
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
from math import exp, atan
from typing import Optional, Dict, Any

from ..units import convert_speed, convert_temperature

@dataclass(frozen=True)
class WeatherIndexes:
    heat_index: Optional[float]
    wind_chill: Optional[float]
    humidex: Optional[float]
    wet_bulb: Optional[float]


def compute_heat_index(temp_f: Optional[float], rh: Optional[float]) -> Optional[float]:
    """
    NWS Heat Index formula (Steadman).
    Only valid for T >= 80°F and RH >= 40%.
    """
    if temp_f is None or rh is None:
        return None
    if temp_f < 80 or rh < 40:
        return None

    T = temp_f
    R = rh

    hi = (
        -42.379
        + 2.04901523 * T
        + 10.14333127 * R
        - 0.22475541 * T * R
        - 6.83783e-3 * T * T
        - 5.481717e-2 * R * R
        + 1.22874e-3 * T * T * R
        + 8.5282e-4 * T * R * R
        - 1.99e-6 * T * T * R * R
    )

    return round(hi, 1)


def compute_wind_chill(temp_f: Optional[float], wind_mph: Optional[float]) -> Optional[float]:
    """
    NWS Wind Chill formula.
    Only valid for T <= 50°F and wind >= 3 mph.
    """
    if temp_f is None or wind_mph is None:
        return None
    if temp_f > 50 or wind_mph < 3:
        return None

    v = wind_mph
    wc = (
        35.74
        + 0.6215 * temp_f
        - 35.75 * (v ** 0.16)
        + 0.4275 * temp_f * (v ** 0.16)
    )

    return round(wc, 1)


def compute_humidex(temp_c: Optional[float], dewpoint_c: Optional[float]) -> Optional[float]:
    """
    Canadian Humidex formula.
    """
    if temp_c is None or dewpoint_c is None:
        return None
    # Vapor pressure (kPa)
    e = 6.11 * exp(5417.7530 * ((1 / 273.16) - (1 / (dewpoint_c + 273.15))))
    h = temp_c + 0.5555 * (e - 10)

    return round(h, 1)


def compute_wet_bulb(temp_c: Optional[float], rh: Optional[float]) -> Optional[float]:
    """
    Stull (2011) approximation for wet bulb temperature.
    Valid for typical atmospheric ranges.
    """
    if temp_c is None or rh is None:
        return None
    T = temp_c
    RH = rh

    tw = (
        T * atan(0.151977 * (RH + 8.313659) ** 0.5)
        + atan(T + RH)
        - atan(RH - 1.676331)
        + 0.00391838 * RH ** 1.5 * atan(0.023101 * RH)
        - 4.686035
    )

    return round(tw, 1)


def compute_all_indexes(
    temp_f: Optional[float],
    temp_c: Optional[float],
    dewpoint_c: Optional[float],
    rh: Optional[float],
    wind_mph: Optional[float],
) -> WeatherIndexes:
    """
    Unified index computation for check_weather.
    """
    return WeatherIndexes(
        heat_index=compute_heat_index(temp_f, rh),
        wind_chill=compute_wind_chill(temp_f, wind_mph),
        humidex=compute_humidex(temp_c, dewpoint_c),
        wet_bulb=compute_wet_bulb(temp_c, rh),
    )

def compute_indexes_from_fields(
    temp_c: Optional[float],
    dewpoint_c: Optional[float],
    rh: Optional[float],
    wind_kph: Optional[float],
) -> Dict[str, Any]:
    """
    Provider-agnostic helper that computes all indexes from normalized fields.
    Converts units as needed and returns a dict ready for JSON output.
    """

    # Convert units
    temp_f = convert_temperature(temp_c, "C", "F") if temp_c is not None else None
    wind_mph = convert_speed(wind_kph, "kph", "mph") if wind_kph is not None else None

    indexes = compute_all_indexes(
        temp_f=temp_f,
        temp_c=temp_c,
        dewpoint_c=dewpoint_c,
        rh=rh,
        wind_mph=wind_mph,
    )

    return indexes.__dict__
