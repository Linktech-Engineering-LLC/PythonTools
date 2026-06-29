#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
File: exitcodes.py
Author: Leon McClatchey
Company: Linktech Engineering LLC
Created: 2026-06-29
 Modified: 2026-06-29
Required: Python 3.8+

Description: General Class for Exit Codes

"""

class ExitCodeClassifier:
    def __init__(self, cfg: dict):
        self.cfg = cfg

    def classify(self, rc: int) -> str:
        for category, patterns in self.cfg.items():
            if self._matches(rc, patterns):
                return category
        return "unknown"

    def _matches(self, rc: int, patterns: list) -> bool:
        matched = False
        excluded = set()

        for p in patterns:
            if isinstance(p, int):
                if rc == p:
                    matched = True
                continue

            p = str(p).strip()

            if p.startswith("!"):
                excluded.add(int(p[1:]))
                continue

            if p == "*":
                matched = True
                continue

            try:
                if rc == int(p):
                    matched = True
            except ValueError:
                pass

        if rc in excluded:
            return False

        return matched
