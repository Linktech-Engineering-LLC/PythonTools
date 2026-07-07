# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-07
Modified: 2026-07-07
 File: PythonTools/finance/providers/yahoo_provider.py
 Version: 1.0.0
 Description: Module description here
"""

from .base import BaseProvider
from .registry import ProviderRegistry

from PythonTools.market.yahoo import (
    fetch_yahoo_crypto,
    fetch_yahoo_stock,
)
from PythonTools.market.symbols import normalize_crypto, normalize_commodity


@ProviderRegistry.register
class YahooProvider(BaseProvider):
    name = "yahoo"
    requires_key = False
    accepts_key = False
    priority = 10
    asset_types = {"stock", "crypto", "commodity", "index"}
    prefers_history = True
    capabilities = {"history", "trend", "ohlc", "volume"}
    

    def fetch(self, symbol: str, key: str):
        # Crypto normalization
        yahoo_symbol = normalize_crypto(symbol, "yahoo")
        if yahoo_symbol != symbol:
            base = yahoo_symbol.replace("-USD", "")
            return fetch_yahoo_crypto(base)

        # Commodity normalization
        yahoo_symbol = normalize_commodity(symbol, "yahoo")
        if yahoo_symbol != symbol:
            return fetch_yahoo_stock(yahoo_symbol)

        # Stock / ETF / Index
        return fetch_yahoo_stock(symbol)
