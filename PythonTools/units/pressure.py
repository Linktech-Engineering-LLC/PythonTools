# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-08
 Modified: 2026-08-08
 File: PythonTools/units/pressure.py
 Version: 1.0.0
 Description: Pressure Conversion Utilities
"""

# ============================================================
# Pressure Conversion Utilities
# ============================================================

def hpa_to_inhg(value):
    if value is None:
        return None
    return round(value * 0.0295299830714, 3)

def inhg_to_hpa(value):
    if value is None:
        return None
    return round(value / 0.0295299830714, 2)

def hpa_to_mmhg(value):
    if value is None:
        return None
    return round(value * 0.75006156, 2)

def mmhg_to_hpa(value):
    if value is None:
        return None
    return round(value / 0.75006156, 2)

def hpa_to_atm(value):
    if value is None:
        return None
    return round(value / 1013.25, 5)

def atm_to_hpa(value):
    if value is None:
        return None
    return round(value * 1013.25, 2)


def convert_pressure(value, from_unit, to_unit):
    """
    Convert pressure between hPa, inHg, mmHg, atm using match-case.
    Only this function is exported; helpers remain internal.
    """
    if value is None:
        return None

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit == to_unit:
        return round(value, 3)

    match (from_unit, to_unit):
        case ("hpa", "inhg"):
            return hpa_to_inhg(value)
        case ("inhg", "hpa"):
            return inhg_to_hpa(value)

        case ("hpa", "mmhg"):
            return hpa_to_mmhg(value)
        case ("mmhg", "hpa"):
            return mmhg_to_hpa(value)

        case ("hpa", "atm"):
            return hpa_to_atm(value)
        case ("atm", "hpa"):
            return atm_to_hpa(value)

        case _:
            return round(value, 3)
