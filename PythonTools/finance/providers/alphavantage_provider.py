# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-07
 Modified: 2026-07-18
 File: PythonTools/finance/providers/alphavantage_provider.py
 Version: 1.0.0
 Description: Module description here
"""

from .base import BaseProvider
from .registry import ProviderRegistry

from ...market.alpha import fetch_alpha_stock
from ...market.symbols import COMMODITY_MAP

@ProviderRegistry.register
class AlphaVantageProvider(BaseProvider):
    name = "alphavantage"
    requires_key = False
    accepts_key = True
    priority = 30
    asset_types = {"stock", "forex", "commodity"}
    prefers_history = False
    capabilities = {"quote"}
    
    def fetch(self, symbol: str, key: str):
        symbol = symbol.upper()

        # Commodity → use GLOBAL_QUOTE
        if symbol in COMMODITY_MAP:
            alpha_id = COMMODITY_MAP[symbol]["alphavantage"]
            return fetch_alpha_stock(alpha_id, key)

        # Stock / Forex → use GLOBAL_QUOTE
        return fetch_alpha_stock(symbol, key)
