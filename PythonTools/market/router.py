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
 Description:
            Central routing engine for all market data requests. Determines the asset type
            (stock, forex, commodity, crypto) and dispatches to the appropriate provider
            (Finnhub, Yahoo, CoinGecko). Handles fallback logic, normalizes
            results into QuoteResult objects, and prepares data for trend and history
            analysis. This module acts as the unified entry point for all market queries.
"""
from PythonTools.market.coingecko import fetch_coingecko_crypto
from PythonTools.market.finnhub import fetch_finnhub_crypto
from PythonTools.market.yahoo import fetch_yahoo_crypto, fetch_yahoo_stock
from PythonTools.market.objects import QuoteResult
from PythonTools.market.trend import extract_history, compute_trend_and_slope


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
    def __init__(self, api_keys: dict):
        self.finnhub_key = api_keys.get("finnhub", "")
        self.coingecko_key = api_keys.get("coingecko", "")

    def get_quote(self, symbol: str) -> QuoteResult:
        t = detect_type(symbol)

        result = None

        if t in ("stock", "forex", "commodity"):
            result = fetch_yahoo_stock(symbol)

        elif t == "crypto":
            # CoinGecko first
            r = fetch_coingecko_crypto(symbol, self.coingecko_key)
            if not r.is_error():
                result = r
            else:
                # Yahoo fallback
                r = fetch_yahoo_crypto(symbol)
                if not r.is_error():
                    result = r
                else:
                    # Finnhub fallback
                    result = fetch_finnhub_crypto(symbol, self.finnhub_key)

        else:
            return QuoteResult(0, 0, error="Unknown symbol type")

        # --- POST PROCESSING (applied once) ---
        result.history = extract_history(result)

        return result
