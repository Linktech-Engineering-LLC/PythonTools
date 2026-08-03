# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-03
 File: PythonTools/cache/ttl.py
 Version: 1.0.0
 Description: Module description here
"""
from datetime import datetime, timedelta

def is_expired(ts: datetime, ttl: timedelta) -> bool:
    return datetime.now() - ts > ttl
