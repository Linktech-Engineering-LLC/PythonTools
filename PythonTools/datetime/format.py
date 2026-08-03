# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-03
 File: PythonTools/datetime/format.py
 Version: 1.0.0
 Description: Module description here
"""

from datetime import datetime

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
