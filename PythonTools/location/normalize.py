# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-11
 File: PythonTools/location/normalize.py
 Version: 1.0.0
 Description: Module description here
"""
import unicodedata
import re

from .us_states import US_STATES, STATE_NAME_TO_CODE
from .countries import COUNTRIES, COUNTRY_NAME_TO_CODE

def normalize_state(value: str):
    if not value:
        return None
    v = value.strip().lower()
    if v.upper() in US_STATES:
        return v.upper()
    return STATE_NAME_TO_CODE.get(v)

def normalize_country(value: str) -> str:
    if not value:
        return "US"   # default

    v = value.strip().lower()

    # direct code match
    if v.upper() in COUNTRIES:
        return v.upper()

    # name match
    code = COUNTRY_NAME_TO_CODE.get(v)
    if code:
        return code

    # fallback default
    return "US"

def normalize_zip(value: str):
    if not value:
        return None
    v = value.strip()
    return v if v.isdigit() and len(v) in (5, 9) else None

def normalize_city(value: str) -> str:
    """
    Provider-agnostic city normalization.
    - Strips whitespace
    - Normalizes Unicode accents
    - Collapses multiple spaces
    - Removes leading/trailing punctuation
    - Preserves internal punctuation (e.g., "St. John")
    """

    if not value:
        return ""

    # Strip whitespace
    v = value.strip()

    # Normalize Unicode accents (NFKC recommended for geocoding)
    v = unicodedata.normalize("NFKC", v)

    # Collapse multiple spaces
    v = re.sub(r"\s+", " ", v)

    # Remove leading/trailing punctuation but preserve internal punctuation
    v = v.strip(" ,.;:/\\\"'")

    return v
def normalize_city_name(city: str) -> str:
    city = city.strip()
    # Replace "St" or "St." at the beginning with "Saint"
    if city.lower().startswith("st "):
        return "Saint " + city[3:].strip()
    if city.lower().startswith("st. "):
        return "Saint " + city[4:].strip()
    return city

def format_resolved_name(loc):
    city = loc.get("city")
    state = loc.get("state")
    country = loc.get("country")
    zip_code = loc.get("zip")

    if city and state and zip_code:
        return f"{city}, {state} {zip_code}, {country}"
    if city and state:
        return f"{city}, {state}, {country}"
    if city:
        return f"{city}, {country}"
    return f"{loc['latitude']},{loc['longitude']}"
