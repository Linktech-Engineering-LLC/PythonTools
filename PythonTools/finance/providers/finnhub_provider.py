# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-07
 Modified: 2026-07-07
 File: PythonTools/finance/providers/finnhub_provider.py
 Version: 1.0.0
 Description: Module description here
"""
from .base import BaseProvider
from .registry import ProviderRegistry

from PythonTools.market.finnhub import fetch_finnhub_crypto
from PythonTools.market.objects import QuoteResult
from PythonTools.market.symbols import normalize_crypto, normalize_commodity

@ProviderRegistry.register
class FinnhubProvider(BaseProvider):
    name = "finnhub"
    requires_key = False
    accepts_key = True
    priority = 30
    asset_types = {"crypto"}
    prefers_history = True
    capabilities = {"history", "candles"}

    def fetch(self, symbol: str, key: str):
        # Provider-specific normalization
        symbol = normalize_crypto(symbol, "finnhub")
        symbol = normalize_commodity(symbol, "finnhub")

        raw = fetch_finnhub_crypto(symbol, key)

        # Error from fetcher
        if "error" in raw:
            return QuoteResult(
                price=0,
                pct=0,
                provider="finnhub",
                error=raw["error"],
                provider_key=key,
                provider_symbol=symbol
            )

        closes = raw.get("c", [])
        price = closes[-1] if closes else 0
        timestamp = raw.get("t", [None])[-1]

        return QuoteResult(
            price=price,
            pct=0,
            provider="finnhub",
            timestamp=timestamp,
            raw=raw,
            history=closes,
            provider_key=key,
            provider_symbol=symbol
        )

