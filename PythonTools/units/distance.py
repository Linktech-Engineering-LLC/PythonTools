# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-08
 Modified: 2026-08-08
 File: PythonTools/units/distance.py
 Version: 1.0.0
 Description: Distance Conversion Utilities
"""
# ============================================================
# Distance / Length Conversion Utilities
# ============================================================

def mm_to_in(value):
    if value is None:
        return None
    return round(value / 25.4, 2)

def in_to_mm(value):
    if value is None:
        return None
    return round(value * 25.4, 2)

def m_to_km(value):
    if value is None:
        return None
    return round(value / 1000.0, 2)

def km_to_m(value):
    if value is None:
        return None
    return round(value * 1000.0, 2)

def m_to_mi(value):
    if value is None:
        return None
    return round(value / 1609.344, 2)

def mi_to_m(value):
    if value is None:
        return None
    return round(value * 1609.344, 2)


def convert_distance(value, from_unit, to_unit):
    """
    Convert distance between mm, in, m, km, mi using match-case.
    Only this function is exported; helpers remain internal.
    """
    if value is None:
        return None

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit == to_unit:
        return round(value, 2)

    match (from_unit, to_unit):
        case ("mm", "in"):
            return mm_to_in(value)
        case ("in", "mm"):
            return in_to_mm(value)

        case ("m", "km"):
            return m_to_km(value)
        case ("km", "m"):
            return km_to_m(value)

        case ("m", "mi"):
            return m_to_mi(value)
        case ("mi", "m"):
            return mi_to_m(value)

        case _:
            return round(value, 2)
