# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-03
 File: PythonTools/utils/dict.py
 Version: 1.0.0
 Description: Module description here
"""

def strip_none(d):
    return {k: v for k, v in d.items() if v is not None}

