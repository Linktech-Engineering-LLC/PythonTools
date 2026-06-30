#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
File: normalize.py
Author: Leon McClatchey
Company: Linktech Engineering LLC
Created: 2026-06-30
 Modified: 2026-06-30
Required: Python 3.8+

Description: Description of this module

"""
def normalize_systemd_result(result):
    def _get(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    return {
        "exit_code": _get(result, "exit_code", 1),
        "stdout": _get(result, "stdout", ""),
        "stderr": _get(result, "stderr", ""),
        "unit": _get(result, "unit", None),
        "systemd_state": _get(result, "state", "unknown"),
        "success": _get(result, "success", None),
        "start_time": _get(result, "start_time", None),
        "end_time": _get(result, "end_time", None),
        "duration": _get(result, "duration", None),
        "status": "unknown",
    }

