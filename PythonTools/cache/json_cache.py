# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-03
 File: PythonTools/cache/json_cache.py
 Version: 1.0.0
 Description: Module description here
"""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path

from .ttl import is_expired

def cache_path(base: Path, key: str) -> Path:
    digest = hashlib.sha256(key.encode()).hexdigest()
    return base / f"{digest}.json"

def load_json_cache(path: Path, ttl: timedelta):
    if not path.exists():
        return None, None

    try:
        with open(path, "r") as f:
            cached = json.load(f)

        ts = datetime.fromisoformat(cached["timestamp"])

        if is_expired(ts, ttl):
            return None, None

        return cached["data"], ts

    except Exception:
        return None, None

def save_json_cache(path: Path, data: dict):
    payload = {
        "timestamp": datetime.now().isoformat(),
        "data": data
    }
    with open(path, "w") as f:
        json.dump(payload, f)
    return True

