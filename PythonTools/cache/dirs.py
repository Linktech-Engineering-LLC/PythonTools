# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-03
 File: PythonTools/cache/dirs.py
 Version: 1.0.0
 Description: Module description here
"""

import os
import pwd
from pathlib import Path

def get_cache_dir():
    # 1. Respect XDG_CACHE_HOME if set
    xdg = os.environ.get("XDG_CACHE_HOME")
    if xdg:
        return Path(xdg) / "nms_tools"

    # 2. Detect Nagios user
    try:
        user = pwd.getpwuid(os.geteuid()).pw_name
    except Exception:
        user = None

    if user in ("nagios", "nrpe"):
        return Path("/var/tmp/nms_tools")

    # 3. Normal user fallback
    return Path.home() / ".cache" / "nms_tools"

def ensure_subdir(name: str) -> Path:
    base = get_cache_dir()
    path = base / name
    path.mkdir(parents=True, exist_ok=True)
    return path

