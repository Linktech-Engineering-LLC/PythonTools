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
    price: float
    pct: float
    history: Optional[List[float]] = None
    trend: str = "unknown"
    error: Optional[str] = None

    def is_error(self):
        return self.error is not None
