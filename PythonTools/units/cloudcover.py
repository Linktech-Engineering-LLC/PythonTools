# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-08
 Modified: 2026-08-08
 File: PythonTools/units/cloudcover.py
 Version: 1.0.0
 Description: Cloud Cover Conversion Utilities
"""
# ============================================================
# Cloud Cover Conversion Utilities
# ============================================================
# percent ↔ oktas (0–8)

def percent_to_oktas(value):
    if value is None:
        return None
    # 100% → 8 oktas
    return round(value / 12.5)

def oktas_to_percent(value):
    if value is None:
        return None
    return round(value * 12.5, 1)


def convert_cloudcover(value, from_unit, to_unit):
    """
    Convert cloud cover between percent and oktas.
    Only this function is exported; helpers remain internal.
    """
    if value is None:
        return None

    from_unit = from_unit.lower()
    to_unit = to_unit.lower()

    if from_unit == to_unit:
        return round(value, 1)

    match (from_unit, to_unit):
        case ("percent", "oktas"):
            return percent_to_oktas(value)
        case ("oktas", "percent"):
            return oktas_to_percent(value)
        case _:
            return round(value, 1)

