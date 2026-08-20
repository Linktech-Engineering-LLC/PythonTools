# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-20
 Modified: 2026-08-20
 File: PythonTools/datetime/moontimes.py
 Version: 1.0.0
 Description: Module description here
"""

# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey

import math
from datetime import datetime, timedelta
from astral import LocationInfo

# ------------------------------------------------------------
# Astral version detection
# ------------------------------------------------------------
try:
    # Astral 3.x
    from astral.moon import (
        moon_phase,
        moon_illumination,
        moonrise,
        moonset,
        moon_altitude,
        moon_azimuth,
    )
    ASTRAL3 = True

except ImportError:
    # Astral 2.x fallback
    from astral.moon import phase as moon_phase
    ASTRAL3 = False

# ------------------------------------------------------------
# Deterministic moon phase + illumination (Meeus)
# ------------------------------------------------------------
def moon_phase_info(date_str: str):
    dt = datetime.strptime(date_str, "%Y-%m-%d")

    known_new_moon = datetime(2000, 1, 6)
    days = (dt - known_new_moon).days + ((dt - known_new_moon).seconds / 86400.0)

    synodic_month = 29.53058867
    moon_age = days % synodic_month

    illumination = (1 - math.cos(2 * math.pi * moon_age / synodic_month)) * 50
    illumination = round(illumination, 1)

    phase_code = int((moon_age / synodic_month) * 8) % 8

    phase_names = [
        "new_moon",
        "waxing_crescent",
        "first_quarter",
        "waxing_gibbous",
        "full_moon",
        "waning_gibbous",
        "last_quarter",
        "waning_crescent",
    ]

    return {
        "moon_phase": phase_names[phase_code],
        "moon_phase_code": phase_code,
        "moon_illumination": illumination,
    }

# ------------------------------------------------------------
# Public API: moon illumination
# ------------------------------------------------------------
def compute_moon_illumination(date_obj):
    if ASTRAL3:
        return moon_illumination(date_obj)
    else:
        return fallback_moon_illumination(date_obj)

# ------------------------------------------------------------
# Public API: numeric moon phase (0–29.53)
# ------------------------------------------------------------
def compute_moon_phase(date_obj):
    return moon_phase(date_obj)

# ------------------------------------------------------------
# Public API: moon altitude + azimuth
# ------------------------------------------------------------
def compute_moon_position(lat, lon, dt):
    if ASTRAL3:
        loc = LocationInfo(latitude=lat, longitude=lon)
        observer = loc.observer
        return {
            "altitude": moon_altitude(observer, dt),
            "azimuth": moon_azimuth(observer, dt),
        }
    else:
        return fallback_moon_position(lat, lon, dt)

# ------------------------------------------------------------
# Public API: moonrise + moonset
# ------------------------------------------------------------
def compute_moon_times(lat, lon, date_obj, tzinfo):
    if ASTRAL3:
        loc = LocationInfo(latitude=lat, longitude=lon)
        observer = loc.observer
        return (
            moonrise(observer, date_obj, tzinfo),
            moonset(observer, date_obj, tzinfo),
        )
    else:
        return fallback_moon_times(lat, lon, date_obj, tzinfo)

# ------------------------------------------------------------
# Fallback: illumination from numeric phase
# ------------------------------------------------------------
def fallback_moon_illumination(date_obj):
    p = moon_phase(date_obj)
    angle = p * (360.0 / 29.53)
    return (1 - math.cos(math.radians(angle))) / 2

# ------------------------------------------------------------
# Fallback: altitude + azimuth (Meeus simplified)
# ------------------------------------------------------------
def fallback_moon_position(lat, lon, dt):
    def julian(dt):
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12*a - 3
        jdn = dt.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045
        jd = jdn + (dt.hour - 12)/24 + dt.minute/1440 + dt.second/86400
        return jd

    jd = julian(dt)
    T = (jd - 2451545.0) / 36525.0

    L = 218.316 + 13.176396*T*36525
    M = 134.963 + 13.064993*T*36525

    lon_moon = L + 6.289 * math.sin(math.radians(M))
    lat_moon = 5.128 * math.sin(math.radians(M))

    GMST = 280.46061837 + 360.98564736629*(jd - 2451545)
    LMST = (GMST + lon) % 360
    HA = LMST - lon_moon

    lat_r = math.radians(lat)
    dec_r = math.radians(lat_moon)
    ha_r = math.radians(HA)

    alt = math.degrees(
        math.asin(
            math.sin(lat_r)*math.sin(dec_r) +
            math.cos(lat_r)*math.cos(dec_r)*math.cos(ha_r)
        )
    )

    az = math.degrees(
        math.atan2(
            -math.sin(ha_r),
            math.tan(dec_r)*math.cos(lat_r) - math.sin(lat_r)*math.cos(ha_r)
        )
    )
    az = (az + 360) % 360

    return {"altitude": alt, "azimuth": az}

# ------------------------------------------------------------
# Fallback: moonrise + moonset (minute scan)
# ------------------------------------------------------------
def fallback_moon_times(lat, lon, date_obj, tzinfo):
    rise_dt = None
    set_dt = None

    dt = datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, tzinfo=tzinfo)
    end = dt + timedelta(days=1)
    step = timedelta(minutes=1)

    prev_alt = fallback_moon_position(lat, lon, dt)["altitude"]

    while dt < end:
        dt_next = dt + step
        alt = fallback_moon_position(lat, lon, dt_next)["altitude"]

        if prev_alt < 0 <= alt and rise_dt is None:
            rise_dt = dt_next

        if prev_alt > 0 >= alt and set_dt is None:
            set_dt = dt_next

        prev_alt = alt
        dt = dt_next

    return {rise_dt, set_dt}
