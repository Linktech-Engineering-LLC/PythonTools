# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-26
 Modified: 2026-08-26
 File: PythonTools/net/http.py
 Version: 1.0.0
 Description: Net HTTP Tools
"""

import json
import urllib.request

def http_get_json(url: str, timeout: float = 5.0):
    """
    Minimal HTTP GET returning parsed JSON.
    Deterministic, no external dependencies.
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PythonTools"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
            return json.loads(data.decode("utf-8"))
    except Exception:
        return None
