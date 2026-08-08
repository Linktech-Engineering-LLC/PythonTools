# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-08
 Modified: 2026-08-08
 File: PythonTools/datetime/suntimes.py
 Version: 1.0.0
 Description: Sunlight time management functions
"""

import math
from astral.moon import moonrise, moonset
try:
    from astral.moon import moon_illumination, moon_altitude, moon_azimuth
    ASTRAL3 = True
except ImportError:
    from astral.moon import phase as moon_phase
    ASTRAL3 = False
from astral.sun import (
    sun, 
    elevation,
    azimuth
)
from astral import LocationInfo
from datetime import datetime, timezone, timedelta
from timezonefinder import TimezoneFinder   
from typing import Optional
from zoneinfo import ZoneInfo

def compute_golden_blue_hours(lat, lon, date_obj, tzinfo):
    loc = LocationInfo(latitude=lat, longitude=lon)
    observer = loc.observer

    golden = []
    blue = []

    dt = datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, tzinfo=tzinfo)
    end = dt + timedelta(days=1)
    step = timedelta(minutes=5)

    prev = elevation(observer, dt)

    while dt < end:
        dt_next = dt + step
        elev = elevation(observer, dt_next)

        # Golden hour: 6° >= elev >= -4°
        if 6 >= elev >= -4:
            golden.append(dt_next)

        # Blue hour: -4° > elev >= -6°
        if -4 > elev >= -6:
            blue.append(dt_next)

        dt = dt_next

    return {
        "golden": golden,
        "blue": blue,
    }
def compute_moon_illumination(date_obj):
    if ASTRAL3:
        return moon_illumination(date_obj)
    else:
        return fallback_moon_illumination(date_obj)
def compute_moon_phase(date_obj):
    if ASTRAL3:
        return moon_phase(date_obj)
    else:
        return moon_phase(date_obj)  # Astral 2 version
def compute_moon_position(lat, lon, dt):
    loc = LocationInfo(latitude=lat, longitude=lon)
    observer = loc.observer
    if ASTRAL3:
        return {
            "altitude": moon_altitude(observer, dt),
            "azimuth": moon_azimuth(observer, dt),
        }
    else:
        return fallback_moon_position(lat, lon, dt)
def compute_moon_times(lat, lon, date_obj, tzinfo):
    loc = LocationInfo(latitude=lat, longitude=lon)
    observer = loc.observer
    if ASTRAL3:
        return {
            "moonrise": moonrise(observer, date_obj, tzinfo),
            "moonset": moonset(observer, date_obj, tzinfo),
        }
    else:
        return fallback_moon_times(lat, lon, date_obj, tzinfo)
def compute_solar_noon(lat, lon, date_obj, tzinfo):
    loc = LocationInfo(latitude=lat, longitude=lon)
    s = sun(loc.observer, date=date_obj, tzinfo=tzinfo)
    return s["noon"]
def compute_sun_position(lat, lon, dt):
    loc = LocationInfo(latitude=lat, longitude=lon)
    observer = loc.observer
    if ASTRAL3:
        return {
            "elevation": elevation(observer, dt),
            "azimuth": azimuth(observer, dt),
        }
    else:
        return fallback_sun_position(lat, lon, dt)
def compute_sun_times(lat, lon, date_obj, tzinfo):
    loc = LocationInfo(latitude=lat, longitude=lon)
    s = sun(loc.observer, date=date_obj, tzinfo=tzinfo)
    sunrise=s["sunrise"].replace(second=0, microsecond=0)
    sunset=s["sunset"].replace(second=0,microsecond=0)
    return sunrise, sunset
def compute_twilight(lat, lon, date_obj, tzinfo):
    loc = LocationInfo(latitude=lat, longitude=lon)
    s = sun(loc.observer, date=date_obj, tzinfo=tzinfo)

    return {
        "civil_dawn": s["dawn"],
        "civil_dusk": s["dusk"],
        "nautical_dawn": s["nautical_dawn"],
        "nautical_dusk": s["nautical_dusk"],
        "astronomical_dawn": s["astronomical_dawn"],
        "astronomical_dusk": s["astronomical_dusk"],
    }
def ensure_dt(x):
    if x is None:
        return None

    # Already a datetime → normalize timezone
    if isinstance(x, datetime):
        if x.tzinfo is None:
            return x.replace(tzinfo=timezone.utc)
        return x

    # Open‑Meteo → string
    if isinstance(x, str):
        dt = datetime.fromisoformat(x)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt

    raise TypeError(f"Unsupported datetime type: {type(x)}")
def fallback_moon_illumination(date_obj):
    """
    Compute approximate moon illumination from Astral-2 moon phase.
    Returns a float between 0.0 and 1.0.
    """
    p = moon_phase(date_obj)  # 0–29.53
    # Convert phase to angle
    angle = p * (360.0 / 29.53)
    # Illumination formula
    illum = (1 - math.cos(math.radians(angle))) / 2
    return illum
def fallback_moon_position(lat, lon, dt):
    """
    Compute approximate moon altitude and azimuth using simplified
    astronomical formulas (Meeus-based). Works without Astral-3.
    Returns altitude and azimuth in degrees.
    """
    # Convert to Julian date
    def julian(dt):
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12*a - 3
        jdn = dt.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045
        jd = jdn + (dt.hour - 12)/24 + dt.minute/1440 + dt.second/86400
        return jd

    jd = julian(dt)
    T = (jd - 2451545.0) / 36525.0

    # Moon mean longitude
    L = 218.316 + 13.176396*T*36525

    # Moon mean anomaly
    M = 134.963 + 13.064993*T*36525

    # Moon latitude & longitude (very simplified)
    lon_moon = L + 6.289 * math.sin(math.radians(M))
    lat_moon = 5.128 * math.sin(math.radians(M))

    # Convert to altitude/azimuth
    # Hour angle approximation
    GMST = 280.46061837 + 360.98564736629*(jd - 2451545)
    LMST = (GMST + lon) % 360
    HA = LMST - lon_moon

    # Convert to radians
    lat_r = math.radians(lat)
    dec_r = math.radians(lat_moon)
    ha_r = math.radians(HA)

    # Altitude
    alt = math.degrees(
        math.asin(
            math.sin(lat_r)*math.sin(dec_r) +
            math.cos(lat_r)*math.cos(dec_r)*math.cos(ha_r)
        )
    )

    # Azimuth
    az = math.degrees(
        math.atan2(
            -math.sin(ha_r),
            math.tan(dec_r)*math.cos(lat_r) - math.sin(lat_r)*math.cos(ha_r)
        )
    )
    az = (az + 360) % 360

    return {"altitude": alt, "azimuth": az}
def fallback_moon_times(lat, lon, date_obj, tzinfo):
    """
    Compute approximate moonrise and moonset by scanning altitude
    minute-by-minute. Works without Astral-3.
    Returns timezone-aware datetimes or None.
    """
    rise_dt = None
    set_dt = None

    # Start at midnight local time
    dt = datetime(date_obj.year, date_obj.month, date_obj.day, 0, 0, tzinfo=tzinfo)
    end = dt + timedelta(days=1)
    step = timedelta(minutes=1)

    prev_alt = fallback_moon_position(lat, lon, dt)["altitude"]

    while dt < end:
        dt_next = dt + step
        alt = fallback_moon_position(lat, lon, dt_next)["altitude"]

        # Horizon crossing detection
        if prev_alt < 0 <= alt and rise_dt is None:
            rise_dt = dt_next

        if prev_alt > 0 >= alt and set_dt is None:
            set_dt = dt_next

        prev_alt = alt
        dt = dt_next

    return {"moonrise": rise_dt, "moonset": set_dt}
def fallback_sun_position(lat, lon, dt):
    """
    Compute solar elevation and azimuth using NOAA's simplified SPA algorithm.
    Works without Astral-3.
    Returns elevation and azimuth in degrees.
    """
    # Convert to Julian day
    def julian(dt):
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12*a - 3
        jdn = dt.day + ((153*m + 2)//5) + 365*y + y//4 - y//100 + y//400 - 32045
        jd = jdn + (dt.hour - 12)/24 + dt.minute/1440 + dt.second/86400
        return jd

    jd = julian(dt)
    n = jd - 2451545.0

    # Mean longitude
    L = (280.46 + 0.9856474*n) % 360

    # Mean anomaly
    g = math.radians((357.528 + 0.9856003*n) % 360)

    # Ecliptic longitude
    lam = math.radians(L + 1.915*math.sin(g) + 0.020*math.sin(2*g))

    # Obliquity of the ecliptic
    eps = math.radians(23.439 - 0.0000004*n)

    # Right ascension and declination
    alpha = math.atan2(math.cos(eps)*math.sin(lam), math.cos(lam))
    delta = math.asin(math.sin(eps)*math.sin(lam))

    # Local sidereal time
    GMST = (280.46061837 + 360.98564736629*(jd - 2451545)) % 360
    LMST = math.radians((GMST + lon) % 360)

    # Hour angle
    H = LMST - alpha

    # Convert to altitude/azimuth
    lat_r = math.radians(lat)

    elev = math.degrees(
        math.asin(
            math.sin(lat_r)*math.sin(delta) +
            math.cos(lat_r)*math.cos(delta)*math.cos(H)
        )
    )

    az = math.degrees(
        math.atan2(
            -math.sin(H),
            math.tan(delta)*math.cos(lat_r) - math.sin(lat_r)*math.cos(H)
        )
    )
    az = (az + 360) % 360

    return {"elevation": elev, "azimuth": az}
def get_timezone(lat: float, lon: float) -> ZoneInfo:
    tf = TimezoneFinder()
    tz = tf.timezone_at(lat=lat, lng=lon)
    return ZoneInfo(tz) if tz else ZoneInfo("UTC")
def is_daylight(now, sunrise, sunset):
    return sunrise <= now < sunset

def is_civil_twilight(now, civil_dawn, civil_dusk):
    return civil_dawn <= now < civil_dusk

def is_dark(now, sunset, next_sunrise):
    return now >= sunset or now < next_sunrise

