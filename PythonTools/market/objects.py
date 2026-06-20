# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/market/objects.py
 Version: 1.0.0
 Description: Module description here
"""

# PythonTools/market/objects.py

from dataclasses import dataclass
from typing import List, Optional

@dataclass
class QuoteResult:
    def __init__(
        self,
        price,
        pct,
        provider=None,
        timestamp=None,
        raw=None,
        history=None,
        slope=None,
        fallback_chain=None,
        error=None,
    ):
        self.price = price
        self.pct = pct
        self.provider = provider
        self.timestamp = timestamp
        self.raw = raw or {}
        self.history = history or []
        self.slope = slope
        self.fallback_chain = fallback_chain or []
        self.error = error
        
    def is_error(self):
        return self.error is not None
