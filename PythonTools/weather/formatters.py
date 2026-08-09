# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-09
 File: PythonTools/weather/formatters.py
 Version: 1.0.0
 Description: Presentation formatters
"""

def fmt_temp(data, key, units):
    v = data.get(f"{key}_{'f' if units == 'imperial' else 'c'}")
    return f"{v}°{'F' if units == 'imperial' else 'C'}" if v is not None else "—"

def fmt_wind(data, key, units):
    if units == "imperial":
        v = data.get(key + "_mph") or data.get(key + "_mph_max")
        return f"{v} mph" if v is not None else "—"
    else:
        v = data.get(key + "_kph") or data.get(key + "_kph_max")
        return f"{v} kph" if v is not None else "—"

def fmt_precip(data, key, units):
    if units == "imperial":
        v = data.get(key + "_in")
        return f"{v} in" if v is not None else "—"
    else:
        v = data.get(key + "_mm")
        return f"{v} mm" if v is not None else "—"

def fmt_clouds(v):
    return f"{v}%" if v is not None else "—"
