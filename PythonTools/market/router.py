# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/market/router.py
 Version: 1.0.0
 Description: Module description here
"""
from PythonTools.market.alpha import fetch_alpha_stock
from PythonTools.market.coingecko import fetch_coingecko_crypto
from PythonTools.market.finnhub import fetch_finnhub_crypto
from PythonTools.market.yahoo import fetch_yahoo_crypto
from PythonTools.market.objects import QuoteResult


def detect_type(symbol: str) -> str:
    s = symbol.upper()

    if "/" in s:
        return "forex"

    if s in ("GOLD", "SILVER", "OIL"):
        return "commodity"

    if s in ("BTC", "ETH", "SOL", "DOGE", "XRP", "ADA", "LTC"):
        return "crypto"

    # Default: stock
    return "stock"


class MarketObjectEngine:
    def get_quote(self, symbol: str) -> QuoteResult:
        t = detect_type(symbol)

        if t in ("stock", "forex", "commodity"):
            return fetch_alpha_stock(symbol)

        if t == "crypto":
            r = fetch_finnhub_crypto(symbol)
            if not r.is_error():
                return r
            r = fetch_yahoo_crypto(symbol)
            if not r.is_error():
                return r
            return fetch_coingecko_crypto(symbol)

        return QuoteResult(0, 0, error="Unknown symbol type")
