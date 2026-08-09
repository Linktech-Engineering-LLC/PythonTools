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

import math

from ..temperature import f_to_c, c_to_f


# ---------------------------------------------------------------------------
# Heat Index (NWS)
# ---------------------------------------------------------------------------

def compute_heat_index(temp_f, humidity):
    """
    Compute the NWS Heat Index in Fahrenheit and Celsius.

    NWS formula applies only when:
        temp_f >= 80°F and humidity >= 40%
    Otherwise, heat index = temp_f.

    Returns:
        (heat_index_f, heat_index_c)
    """
    if temp_f is None or humidity is None:
        return None, None

    # If outside valid range, return temperature itself
    if temp_f < 80 or humidity < 40:
        hi_f = float(temp_f)
        return hi_f, f_to_c(hi_f)

    # NWS Rothfusz regression
    T = temp_f
    R = humidity

    hi_f = (
        -42.379
        + 2.04901523 * T
        + 10.14333127 * R
        - 0.22475541 * T * R
        - 0.00683783 * T * T
        - 0.05481717 * R * R
        + 0.00122874 * T * T * R
        + 0.00085282 * T * R * R
        - 0.00000199 * T * T * R * R
    )

    return hi_f, f_to_c(hi_f)


# ---------------------------------------------------------------------------
# Wind Chill (NWS)
# ---------------------------------------------------------------------------

def compute_wind_chill(temp_f, wind_mph):
    """
    Compute NWS Wind Chill in Fahrenheit and Celsius.

    Valid only when:
        temp_f <= 50°F and wind_mph >= 3 mph

    Returns:
        (wind_chill_f, wind_chill_c)
    """
    if temp_f is None or wind_mph is None:
        return None, None

    if temp_f > 50 or wind_mph < 3:
        return None, None

    wc_f = (
        35.74
        + 0.6215 * temp_f
        - 35.75 * (wind_mph ** 0.16)
        + 0.4275 * temp_f * (wind_mph ** 0.16)
    )

    return wc_f, f_to_c(wc_f)


# ---------------------------------------------------------------------------
# Humidex
# ---------------------------------------------------------------------------

def compute_humidex(temp_c, dewpoint_c):
    """
    Compute Humidex (Canada formula).

    Returns:
        humidex (float)
    """
    if temp_c is None or dewpoint_c is None:
        return None

    # Vapor pressure (hPa)
    e = 6.11 * math.exp(5417.7530 * ((1 / 273.16) - (1 / (dewpoint_c + 273.15))))

    humidex = temp_c + 0.5555 * (e - 10.0)
    return humidex


# ---------------------------------------------------------------------------
# Wet Bulb Temperature (Stull approximation)
# ---------------------------------------------------------------------------

def compute_wet_bulb(temp_c, humidity):
    """
    Compute Wet Bulb Temperature using Stull's approximation.

    Returns:
        wet_bulb_c (float)
    """
    if temp_c is None or humidity is None:
        return None

    # Stull formula
    Tw = (
        temp_c * math.atan(0.151977 * math.sqrt(humidity + 8.313659))
        + math.atan(temp_c + humidity)
        - math.atan(humidity - 1.676331)
        + 0.00391838 * (humidity ** 1.5) * math.atan(0.023101 * humidity)
        - 4.686035
    )

    return Tw


# ---------------------------------------------------------------------------
# Unified Index Computation
# ---------------------------------------------------------------------------

def compute_indexes(temp_f, dewpoint_f, humidity, wind_mph):
    """
    Compute all indexes and return a unified dict.

    Inputs:
        temp_f      - temperature in Fahrenheit
        dewpoint_f  - dewpoint in Fahrenheit
        humidity    - relative humidity (%)
        wind_mph    - wind speed (mph)

    Returns:
        {
            "heat_index_f": float or None,
            "heat_index_c": float or None,
            "wind_chill_f": float or None,
            "wind_chill_c": float or None,
            "humidex": float or None,
            "wet_bulb_c": float or None
        }
    """

    # Convert dewpoint to Celsius for humidex
    dewpoint_c = f_to_c(dewpoint_f) if dewpoint_f is not None else None
    temp_c = f_to_c(temp_f) if temp_f is not None else None

    hi_f, hi_c = compute_heat_index(temp_f, humidity)
    wc_f, wc_c = compute_wind_chill(temp_f, wind_mph)
    humidex = compute_humidex(temp_c, dewpoint_c)
    wet_bulb_c = compute_wet_bulb(temp_c, humidity)

    return {
        "heat_index_f": hi_f,
        "heat_index_c": hi_c,
        "wind_chill_f": wc_f,
        "wind_chill_c": wc_c,
        "humidex": humidex,
        "wet_bulb_c": wet_bulb_c,
    }
