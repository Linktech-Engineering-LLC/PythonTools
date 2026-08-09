# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-09
 File: PythonTools/location/__init__.py
 Version: 1.0.0
 Description: 
--------------------

Shared geographic utilities for PythonTools, NMS_Tools, BotScanner, and
other modules that require location normalization, lookup, or provider
metadata.

Public API:
    US_STATES              – mapping of US state codes → full names
    STATE_NAME_TO_CODE     – mapping of full names → state codes

    COUNTRIES              – mapping of country codes → full names
    COUNTRY_NAME_TO_CODE   – mapping of full names → country codes

    normalize_state()      – normalize state names/codes
    normalize_country()    – normalize country names/codes
    normalize_zip()        – normalize ZIP/postal codes

    GeoPoint               – latitude/longitude pair
    LocationInfo           – structured location record

    PROVIDERS              – registry of geolocation/weather providers
"""

from .us_states import US_STATES, STATE_NAME_TO_CODE
from .countries import COUNTRIES, COUNTRY_NAME_TO_CODE
from .normalize import normalize_state, normalize_country, normalize_zip, normalize_city_name, format_resolved_name
from .geo_types import GeoPoint, LocationInfo
from .providers import PROVIDERS
from .validate import validate_location_input

__all__ = [
    "US_STATES",
    "STATE_NAME_TO_CODE",
    "COUNTRIES",
    "COUNTRY_NAME_TO_CODE",
    "normalize_state",
    "normalize_country",
    "normalize_zip",
    "GeoPoint",
    "LocationInfo",
    "PROVIDERS",
    "normalize_city_name",
    "validate_location_input",
    "format_resolved_name",
]
