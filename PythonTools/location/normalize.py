# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-03
 File: PythonTools/location/normalize.py
 Version: 1.0.0
 Description: Module description here
"""

from .us_states import US_STATES, STATE_NAME_TO_CODE
from .countries import COUNTRIES, COUNTRY_NAME_TO_CODE

def normalize_state(value: str):
    if not value:
        return None
    v = value.strip().lower()
    if v.upper() in US_STATES:
        return v.upper()
    return STATE_NAME_TO_CODE.get(v)

def normalize_country(value: str):
    if not value:
        return None
    v = value.strip().lower()
    if v.upper() in COUNTRIES:
        return v.upper()
    return COUNTRY_NAME_TO_CODE.get(v)

def normalize_zip(value: str):
    if not value:
        return None
    v = value.strip()
    return v if v.isdigit() and len(v) in (5, 9) else None

def normalize_city_name(city: str) -> str:
    city = city.strip()
    # Replace "St" or "St." at the beginning with "Saint"
    if city.lower().startswith("st "):
        return "Saint " + city[3:].strip()
    if city.lower().startswith("st. "):
        return "Saint " + city[4:].strip()
    return city
