# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-16
 File: PythonTools/datetime/format.py
 Version: 1.0.0
 Description: Module description here
"""

from datetime import datetime, timezone

def current_timestamp() -> str:
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S %Z%z")
def format_age(seconds: float) -> str:
    if seconds is None:
        return "unknown"
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h}h {m}m {s}s"
    elif m > 0:
        return f"{m}m {s}s"
    else:
        return f"{s}s"
def normalize_ts(ts: str) -> str:
    return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone(timezone.utc).isoformat()
def normalize_ts_local(ts: str, tzinfo):
    # OM timestamps may be "YYYY-MM-DDTHH:MM" (no offset)
    if len(ts) == 16:
        ts = ts + ":00+00:00"
    elif ts.endswith("Z"):
        ts = ts.replace("Z", "+00:00")

    dt = datetime.fromisoformat(ts)
    return dt.astimezone(tzinfo).strftime("%Y-%m-%dT%H:00")
