# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-08
 Modified: 2026-08-20
 File: PythonTools/datetime/suntimes.py
 Version: 1.0.0
 Description: Sunlight time management functions
"""

import math
from astral.sun import sun
try:
    from astral.sun import elevation, azimuth
    ASTRAL3 = True
except ImportError:
    ASTRAL3 = False

from astral import LocationInfo
from datetime import datetime, timedelta

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

