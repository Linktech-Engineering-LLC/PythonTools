# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-08
 Modified: 2026-08-14
 File: PythonTools/units/temperature.py
 Version: 1.0.0
 Description: Temperature Conversion Utilities
"""

def f_to_c(value):
    """Fahrenheit → Celsius"""
    if value is None:
        return None
    return round((value - 32) * 5.0 / 9.0, 2)


def c_to_f(value):
    """Celsius → Fahrenheit"""
    if value is None:
        return None
    return round((value * 9.0 / 5.0) + 32, 2)


def c_to_k(value):
    """Celsius → Kelvin"""
    if value is None:
        return None
    return round(value + 273.15, 2)


def k_to_c(value):
    """Kelvin → Celsius"""
    if value is None:
        return None
    return round(value - 273.15, 2)


def f_to_k(value):
    """Fahrenheit → Kelvin"""
    if value is None:
        return None
    return round((value - 32) * 5.0 / 9.0 + 273.15, 2)


def k_to_f(value):
    """Kelvin → Fahrenheit"""
    if value is None:
        return None
    return round((value - 273.15) * 9.0 / 5.0 + 32, 2)

def convert_temperature(value, from_unit, to_unit):
    if value is None:
        return None

    from_unit = from_unit.upper()
    to_unit = to_unit.upper()

    if from_unit == to_unit:
        return round(value, 2)

    match (from_unit, to_unit):
        case ("F", "C"):
            return f_to_c(value)
        case ("C", "F"):
            return c_to_f(value)
        case ("C", "K"):
            return c_to_k(value)
        case ("K", "C"):
            return k_to_c(value)
        case ("F", "K"):
            return f_to_k(value)
        case ("K", "F"):
            return k_to_f(value)
        case _:
            return round(value, 2)
