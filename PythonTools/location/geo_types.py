# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-11
 File: PythonTools/location/geo_types.py
 Version: 1.0.0
 Description: Module description here
"""

from dataclasses import dataclass

@dataclass
class GeoPoint:
    latitude: float
    longitude: float

@dataclass
class LocationInfo:
    # Always present
    query: str
    provider: str
    point: GeoPoint

    # Optional depending on provider
    city: str | None = None
    state: str | None = None
    country: str | None = None
    zip: str | None = None

    # Optional metadata
    url: str | None = None
