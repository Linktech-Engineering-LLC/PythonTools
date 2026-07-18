# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-07
 Modified: 2026-07-18
 File: PythonTools/finance/providers/finnhub_provider.py
 Version: 1.0.0
 Description: Module description here
"""
from .base import BaseProvider
from .registry import ProviderRegistry

from ...market.finnhub import fetch_finnhub_crypto, fetch_finnhub_commodity, fetch_finnhub_stock
from ...market.objects import QuoteResult
from ...market.symbols import CRYPTO_MAP, COMMODITY_MAP

@ProviderRegistry.register
class FinnhubProvider(BaseProvider):
    name = "finnhub"
    requires_key = False
    accepts_key = True
    priority = 40
    asset_types = {"crypto", "commodity", "stock"}
    prefers_history = True
    capabilities = {"history", "candles"}

    def fetch(self, symbol: str, key: str):
        symbol = symbol.upper()

        # Crypto
        if symbol in CRYPTO_MAP:
            fn_id = CRYPTO_MAP[symbol]["finnhub"]
            raw = fetch_finnhub_crypto(fn_id, key)

        # Commodity
        elif symbol in COMMODITY_MAP:
            fn_id = COMMODITY_MAP[symbol]["finnhub"]
            raw = fetch_finnhub_commodity(fn_id, key)

        # Stock
        else:
            fn_id = symbol  # Finnhub stock symbols are usually identical
            raw = fetch_finnhub_stock(fn_id, key)

        # Error from fetcher
        if "error" in raw:
            return QuoteResult(
                price=0,
                pct=0,
                provider="finnhub",
                error=raw["error"],
                provider_key=key,
                provider_symbol=fn_id
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
            provider_symbol=fn_id
        )
