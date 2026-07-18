# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-07
 Modified: 2026-07-18
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
from ...market.symbols import CRYPTO_MAP,COMMODITY_MAP,INDEX_MAP

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
        symbol = symbol.upper()

        # Crypto
        if symbol in CRYPTO_MAP:
            yahoo_symbol = CRYPTO_MAP[symbol]["yahoo"]
            return fetch_yahoo_crypto(yahoo_symbol)

        # Commodity (Yahoo futures)
        elif symbol in COMMODITY_MAP:
            yahoo_symbol = COMMODITY_MAP[symbol]["yahoo"]
            return fetch_yahoo_stock(yahoo_symbol)

        # Index
        elif symbol in INDEX_MAP:
            yahoo_symbol = INDEX_MAP[symbol]["yahoo"]
            return fetch_yahoo_stock(yahoo_symbol)

        # Stock / ETF / Currency / anything else Yahoo supports
        return fetch_yahoo_stock(symbol)
