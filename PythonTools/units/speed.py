# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-08
 Modified: 2026-08-08
 File: PythonTools/units/speed.py
 Version: 1.0.0
 Description: Speed Conversion Utilities
"""

def mph_to_kph(value):
    if value is None:
        return None
    return round(value * 1.60934, 2)

def kph_to_mph(value):
    if value is None:
        return None
    return round(value / 1.60934, 2)

def mph_to_mps(value):
    if value is None:
        return None
    return round(value * 0.44704, 2)

def mps_to_mph(value):
    if value is None:
        return None
    return round(value / 0.44704, 2)

def kph_to_mps(value):
    if value is None:
        return None
    return round(value / 3.6, 2)

def mps_to_kph(value):
    if value is None:
        return None
    return round(value * 3.6, 2)


def convert_speed(value, from_unit, to_unit):
    """
    Convert speed between mph, kph, mps using match-case.
    Delegates to helper functions to avoid duplication.
    """
    if value is None:
        return None

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit == to_unit:
        return round(value, 2)

    match (from_unit, to_unit):
        case ("mph", "kph"):
            return mph_to_kph(value)
        case ("kph", "mph"):
            return kph_to_mph(value)
        case ("mph", "mps"):
            return mph_to_mps(value)
        case ("mps", "mph"):
            return mps_to_mph(value)
        case ("kph", "mps"):
            return kph_to_mps(value)
        case ("mps", "kph"):
            return mps_to_kph(value)
        case _:
            return round(value, 2)
