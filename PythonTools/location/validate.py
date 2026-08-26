# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-26
 File: PythonTools/location/validate.py
 Version: 1.0.0
 Description: Module description here
"""
import re

from .normalize import US_STATES

def validate_location_input(location: str, country: str = "US", lat=None, lon=None):
    """
    Validates location input for check_weather and weather-demo.

    Accepted formats:
      - Explicit lat/lon via CLI (--lat --lon)
      - Lat,Lon in the location string
      - US ZIP (5-digit or ZIP+4)
      - US City, ST or City, StateName
      - Non-US postal codes (alphanumeric)
      - Non-US city names (with or without region)
    """

    # -------------------------
    # 0. If CLI lat/lon provided, skip validation
    # -------------------------
    if lat is not None and lon is not None:
        return True

    loc = (location or "").strip()
    ctry = (country or "US").strip().upper()

    # -------------------------
    # 1. Lat/Lon inside location string
    # -------------------------
    LAT_LON_PATTERN = r"^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$"
    if re.fullmatch(LAT_LON_PATTERN, loc):
        return True

    # -------------------------
    # 2. US-specific validation
    # -------------------------
    if ctry == "US":

        # ZIP or ZIP+4
        ZIP_PATTERN = r"^\d{5}(-\d{4})?$"
        if re.fullmatch(ZIP_PATTERN, loc):
            return True

        # City, ST or City, StateName
        if "," in loc:
            parts = [p.strip() for p in loc.split(",")]
            if len(parts) == 2:
                city, state = parts
                state_upper = state.upper()
                state_lower = state.lower()

                # 2-letter code
                if state_upper in US_STATES:
                    return True

                # full state name
                STATE_NAME_TO_CODE = {v.lower(): k for k, v in US_STATES.items()}
                if state_lower in STATE_NAME_TO_CODE:
                    return True

                raise ValueError(
                    f"Invalid U.S. state '{state}'. Expected 2-letter code or full name."
                )

        raise ValueError(
            "Invalid U.S. location. Expected ZIP, 'City, ST', or 'lat,lon'."
        )

    # -------------------------
    # 3. Non-US validation
    # -------------------------
    # Postal codes: alphanumeric, no comma
    if "," not in loc:
        if re.fullmatch(r"[A-Za-z0-9 ]+", loc):
            return True

    # City or City, Region
    if "," in loc:
        parts = [p.strip() for p in loc.split(",")]
        if len(parts) in (1, 2):
            return True

    # -------------------------
    # 4. Reject everything else
    # -------------------------
    raise ValueError(
        f"Invalid location format for country '{country}'. "
        "Expected postal code, city, or lat/lon."
    )
