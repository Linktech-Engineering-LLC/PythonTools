# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-03
 File: PythonTools/location/validate.py
 Version: 1.0.0
 Description: Module description here
"""
import re

from .normalize import normalize_city_name, US_STATES

def validate_location_input(location: str, country: str):
    """
    Validates location input in a globally safe, deterministic way.

    Rules:
      - US ZIP codes must be numeric (5-digit or ZIP+4).
      - Non-US postal codes may be alphanumeric.
      - US city lookups require a state (City, ST).
      - Non-US city lookups may omit region.
    """

    loc = location.strip()
    ctry = (country or "").strip().upper()

    # -------------------------
    # 1. Detect US ZIP codes
    # -------------------------
    if ctry == "US":
        # Valid US ZIP (5-digit) or ZIP+4
        if re.fullmatch(r"\d{5}(-\d{4})?", loc):
            return True  # valid US ZIP
        # Otherwise treat as city/state and validate below

    # -------------------------
    # 2. Detect non-US postal codes
    # -------------------------
    # Postal codes outside the US are usually a single token with no commas.
    if ctry != "US" and "," not in loc:
        # Accept any alphanumeric postal code
        # (e.g., "K1A 0B1", "SW1A 1AA", "1012 WX")
        return True

    # -------------------------
    # 3. City/state parsing
    # -------------------------
    parts = [p.strip() for p in loc.split(",")]

    # US-specific rule: city-only is invalid
    if ctry == "US":
        if len(parts) == 1:
            raise ValueError(
                "U.S. city lookups require a state abbreviation "
                "(e.g., 'Wichita, KS')."
            )

        if len(parts) == 2:
            city = parts[0].strip()
            state = parts[1].strip()

            # Normalize city (St → Saint)
            city = normalize_city_name(city)

            # Normalize state
            state_upper = state.upper()
            state_lower = state.lower()

            # 1. Check if it's a valid 2-letter code (case-insensitive)
            if state_upper in US_STATES:
                return True # valid

            # 2. Check if it's a full state name
            STATE_NAME_TO_CODE = {v.lower(): k for k, v in US_STATES.items()}
            if state_lower in STATE_NAME_TO_CODE:
                return True # valid

            raise ValueError(
                f"Invalid U.S. state '{state}'. Expected a 2-letter code "
                "or full state name (e.g., 'KS' or 'Kansas')."
            )

        raise ValueError(
            "Invalid U.S. location format. Expected 'City, ST' or a ZIP code."
        )

    # -------------------------
    # 4. Non-US city lookups
    # -------------------------
    # Allow city-only or city+region
    return True
