# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-03
 File: PythonTools/datetime/parse.py
 Version: 1.0.0
 Description: Module description here
"""
from datetime import datetime

def parse_iso(ts: str) -> datetime:
    return datetime.fromisoformat(ts)
