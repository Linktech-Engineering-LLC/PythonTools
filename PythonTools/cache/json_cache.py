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

def _deserialize(obj):
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if k in ("sunrise", "sunset") and isinstance(v, str):
                try:
                    out[k] = datetime.fromisoformat(v)
                except:
                    out[k] = v
            else:
                out[k] = _deserialize(v)
        return out

    if isinstance(obj, list):
        return [_deserialize(v) for v in obj]

    return obj

def load_json_cache(path: Path, ttl: timedelta):
    if not path.exists():
        return None, None

    try:
        with open(path, "r") as f:
            cached = json.load(f)

        ts = datetime.fromisoformat(cached["timestamp"])

        if is_expired(ts, ttl):
            return None, None

        return _deserialize(cached["data"]), ts

    except Exception:
        return None, None

def serialize_for_json(obj):
    from datetime import datetime

    if isinstance(obj, datetime):
        return obj.strftime("%Y-%m-%dT%H:%M")

    if isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}

    if isinstance(obj, list):
        return [serialize_for_json(v) for v in obj]

    return obj


def save_json_cache(path: Path, data: dict):
    payload = {
        "timestamp": datetime.now().isoformat(),
        "data": serialize_for_json(data)
    }
    with open(path, "w") as f:
        json.dump(payload, f)
    return True

