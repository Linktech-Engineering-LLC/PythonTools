# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-07
Modified: 2026-07-07
 File: PythonTools/finance/providers/coingecko_provider.py
 Version: 1.0.0
 Description: Module description here
"""


from .base import BaseProvider
from .registry import ProviderRegistry

from PythonTools.market.coingecko import fetch_coingecko_crypto
from PythonTools.market.symbols import normalize_crypto


@ProviderRegistry.register
class CoinGeckoProvider(BaseProvider):
    name = "coingecko"
    requires_key = False
    accepts_key = True
    priority = 20
    asset_types = {"crypto"}
    prefers_history = True
    capabilities = {"history", "trend", "sparkline"}
    
    def fetch(self, symbol: str, key: str):
        symbol = normalize_crypto(symbol, "coingecko")
        return fetch_coingecko_crypto(symbol, key)
