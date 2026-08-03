# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-03
 File: PythonTools/location/countries.py
 Version: 1.0.0
 Description: Module description here
"""

COUNTRIES = {
    "US": "United States",
    "CA": "Canada",
    "MX": "Mexico",
    # Expand as needed
}

COUNTRY_NAME_TO_CODE = {v.lower(): k for k, v in COUNTRIES.items()}
