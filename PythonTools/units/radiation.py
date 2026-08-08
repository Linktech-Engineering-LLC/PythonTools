# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-08
 Modified: 2026-08-08
 File: PythonTools/units/radiation.py
 Version: 1.0.0
 Description: Radiation Conversion Utilities
"""
# ============================================================
# Radiation Conversion Utilities
# ============================================================
# W/m² ↔ kWh/m²/day ↔ MJ/m²

# 1 W/m² sustained for 24h = 0.024 kWh/m²/day
# 1 W/m² sustained for 24h = 0.0864 MJ/m²

def wm2_to_kwhm2day(value):
    if value is None:
        return None
    return round(value * 0.024, 3)

def kwhm2day_to_wm2(value):
    if value is None:
        return None
    return round(value / 0.024, 2)

def wm2_to_mjm2(value):
    if value is None:
        return None
    return round(value * 0.0864, 3)

def mjm2_to_wm2(value):
    if value is None:
        return None
    return round(value / 0.0864, 2)


def convert_radiation(value, from_unit, to_unit):
    """
    Convert radiation between W/m², kWh/m²/day, MJ/m².
    Only this function is exported; helpers remain internal.
    """
    if value is None:
        return None

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit == to_unit:
        return round(value, 3)

    match (from_unit, to_unit):
        case ("wm2", "kwhm2day"):
            return wm2_to_kwhm2day(value)
        case ("kwhm2day", "wm2"):
            return kwhm2day_to_wm2(value)

        case ("wm2", "mjm2"):
            return wm2_to_mjm2(value)
        case ("mjm2", "wm2"):
            return mjm2_to_wm2(value)

        case _:
            return round(value, 3)

