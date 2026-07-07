# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-07
Modified: 2026-07-07
 File: PythonTools/finance/providers/base.py
 Version: 1.0.0
 Description: Module description here
"""
class BaseProvider:
    """
    Minimal base class for market providers.

    Providers must define:
        - name: str
        - requires_key: bool
        - accepts_key: bool
        - fetch(symbol: str, key: str) -> QuoteResult
    """

    name: str = ""
    requires_key: bool = False
    accepts_key: bool = False
    prefers_history: bool = False
    capabilities: set[str] = set()

    def fetch(self, symbol: str, key: str):
        raise NotImplementedError("Provider must implement fetch()")

