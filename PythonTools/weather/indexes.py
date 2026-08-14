# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-14
 Modified: 2026-08-14
 File: PythonTools/weather/indexes.py
 Version: 1.0.0
 Description: Weather Index Utilities
"""

from math import exp, atan
from typing import Optional, Dict, Any

from typing import Optional

from .types import WeatherIndexes
from ..units.temperature import convert_temperature
from ..units.speed import convert_speed

def compute_feels_like(temp_c, dewpoint_c, rh, wind_kph, is_day):
    """
    Unified feels-like engine.
    Returns (feels_like_c, feels_like_f, source)
    """

    # Convert to required units
    temp_f = convert_temperature(temp_c, "C", "F")
    wind_mph = convert_speed(wind_kph, "kph", "mph") if wind_kph else None

    # 1. Heat Index (F) — only valid during daytime
    hi = None
    if is_day and temp_f is not None and rh is not None and temp_f >= 80:
        hi = compute_heat_index(temp_f, rh)

    # 2. Wind Chill (F)
    wc = None
    if temp_f is not None and wind_mph is not None and temp_f <= 50 and wind_mph >= 3:
        wc = compute_wind_chill(temp_f, wind_mph)

    # 3. Humidex (C)
    hx = None
    if temp_c is not None and dewpoint_c is not None:
        hx = compute_humidex(temp_c, dewpoint_c)

    # 4. Wet Bulb (C)
    wb = None
    if temp_c is not None and rh is not None:
        wb = compute_wet_bulb(temp_c, rh)

    # Priority selection
    if hi is not None:
        feels_like_f = hi
        feels_like_c = convert_temperature(hi, "F", "C")
        return feels_like_c, feels_like_f, "heat_index"

    if wc is not None:
        feels_like_f = wc
        feels_like_c = convert_temperature(wc, "F", "C")
        return feels_like_c, feels_like_f, "wind_chill"

    if hx is not None:
        feels_like_c = hx
        feels_like_f = convert_temperature(hx, "C", "F")
        return feels_like_c, feels_like_f, "humidex"

    if wb is not None:
        feels_like_c = wb
        feels_like_f = convert_temperature(wb, "C", "F")
        return feels_like_c, feels_like_f, "wet_bulb"

    # Fallback
    feels_like_c = temp_c
    feels_like_f = temp_f
    return feels_like_c, feels_like_f, "none"
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
    pressure_hpa: Optional[float],
) -> WeatherIndexes:
    """
    Unified index computation for check_weather.
    """
    return WeatherIndexes(
        heat_index=compute_heat_index(temp_f, rh),
        wind_chill=compute_wind_chill(temp_f, wind_mph),
        humidex=compute_humidex(temp_c, dewpoint_c),
        wet_bulb=compute_wet_bulb(temp_c, rh),

        vapor_pressure=compute_vapor_pressure(dewpoint_c),
        saturation_vapor_pressure=compute_saturation_vapor_pressure(temp_c),
        mixing_ratio=compute_mixing_ratio(
            compute_vapor_pressure(dewpoint_c),
            pressure_hpa
        ),
        specific_humidity=compute_specific_humidity(
            compute_mixing_ratio(
                compute_vapor_pressure(dewpoint_c),
                pressure_hpa
            ),
            pressure_hpa
        ),
        air_density=compute_air_density(temp_c, pressure_hpa, rh),
        pressure_altitude=compute_pressure_altitude(pressure_hpa),
    )
def compute_indexes_from_fields(
    temp_c: Optional[float],
    dewpoint_c: Optional[float],
    rh: Optional[float],
    wind_kph: Optional[float],
    pressure_hpa: Optional[float],
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
        pressure_hpa=pressure_hpa,
    )

    return indexes.__dict__
def compute_vapor_pressure(dewpoint_c: Optional[float]) -> Optional[float]:
    if dewpoint_c is None:
        return None
    return 6.11 * exp(5417.7530 * ((1 / 273.16) - (1 / (dewpoint_c + 273.15))))
def compute_saturation_vapor_pressure(temp_c: Optional[float]) -> Optional[float]:
    if temp_c is None:
        return None
    return 6.11 * exp(5417.7530 * ((1 / 273.16) - (1 / (temp_c + 273.15))))
def compute_mixing_ratio(vp: Optional[float], pressure_hpa: Optional[float]) -> Optional[float]:
    if vp is None or pressure_hpa is None:
        return None
    return 622 * vp / (pressure_hpa - vp)
def compute_specific_humidity(mr: Optional[float], pressure_hpa: Optional[float]) -> Optional[float]:
    if mr is None or pressure_hpa is None:
        return None
    return mr / (1 + mr)
def compute_air_density(temp_c: Optional[float], pressure_hpa: Optional[float], rh: Optional[float]) -> Optional[float]:
    if temp_c is None or pressure_hpa is None or rh is None:
        return None

    temp_k = temp_c + 273.15
    p = pressure_hpa * 100  # convert hPa → Pa

    # approximate vapor pressure
    vp = compute_vapor_pressure(temp_c)
    if vp is None or rh is None:
        return None

    vp = vp * (rh / 100)  # actual vapor pressure
    pd = p - vp           # dry air partial pressure

    Rd = 287.05
    Rv = 461.495

    return (pd / (Rd * temp_k)) + (vp / (Rv * temp_k))
def compute_pressure_altitude(pressure_hpa: Optional[float]) -> Optional[float]:
    if pressure_hpa is None:
        return None
    return 145366.45 * (1 - (pressure_hpa / 1013.25) ** 0.190284)
