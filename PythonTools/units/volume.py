# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-08
 Modified: 2026-08-08
 File: PythonTools/units/volume.py
 Version: 1.0.0
 Description: Volumne Conversion Utilities
"""
# ============================================================
# Volume Conversion Utilities
# ============================================================

def ml_to_l(value):
    if value is None:
        return None
    return round(value / 1000.0, 3)

def l_to_ml(value):
    if value is None:
        return None
    return round(value * 1000.0, 2)

def ml_to_floz(value):
    if value is None:
        return None
    return round(value / 29.5735, 3)

def floz_to_ml(value):
    if value is None:
        return None
    return round(value * 29.5735, 2)

def l_to_gal(value):
    if value is None:
        return None
    return round(value / 3.78541, 3)

def gal_to_l(value):
    if value is None:
        return None
    return round(value * 3.78541, 2)


def convert_volume(value, from_unit, to_unit):
    """
    Convert volume between ml, l, floz, gal using match-case.
    Only this function is exported; helpers remain internal.
    """
    if value is None:
        return None

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit == to_unit:
        return round(value, 3)

    match (from_unit, to_unit):
        case ("ml", "l"):
            return ml_to_l(value)
        case ("l", "ml"):
            return l_to_ml(value)

        case ("ml", "floz"):
            return ml_to_floz(value)
        case ("floz", "ml"):
            return floz_to_ml(value)

        case ("l", "gal"):
            return l_to_gal(value)
        case ("gal", "l"):
            return gal_to_l(value)

        case _:
            return round(value, 3)
