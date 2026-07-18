# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-07-18
 File: PythonTools/market/router.py
 Version: 1.0.0
 Description:
            Central routing engine for all market data requests. Determines the asset type
            (stock, forex, commodity, crypto) and dispatches to the appropriate provider
            (Finnhub, Yahoo, CoinGecko). Handles fallback logic, normalizes
            results into QuoteResult objects, and prepares data for trend and history
            analysis. This module acts as the unified entry point for all market queries.
"""
from ..finance.providers.registry import ProviderRegistry
from . import QuoteResult
from .symbols import normalize_commodity, normalize_forex

ALIASES = {
    "XAU": "GOLD",
    "XAG": "SILVER",
    "WTI": "OIL",
    "BRENT": "OIL",
    "XBT": "BTC",
    "XETH": "ETH",
}

def detect_type(symbol: str) -> str:
    s = symbol.upper().strip()
    s = ALIASES.get(s, s)

    if "/" in s:
        return "forex"

    if s in ("GOLD", "SILVER", "OIL", "NATGAS", "COPPER"):
        return "commodity"

    if s in ("BTC", "ETH", "SOL", "DOGE", "XRP", "ADA", "LTC"):
        return "crypto"

    return "stock"

def extract_history(result):
    raw = result.raw
    provider = result.provider

    match provider:

        case "coingecko":
            return raw.get("market_data", {}) \
                      .get("sparkline_7d", {}) \
                      .get("price", [])

        case "finnhub":
            return raw.get("c", [])

        case "yahoo_crypto" | "yahoo_stock":
            return raw.get("close", [])

        case "yahoo":
            try:
                return raw["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            except Exception:
                return []

        case "alphavantage":
            from PythonTools.market.alpha import fetch_alpha_history
            return fetch_alpha_history(
                raw.get("provider_symbol"),
                raw.get("provider_key")
            )

        case _:
            return []


class MarketObjectEngine:
    def __init__(self, api_keys: dict):
        self.api_keys = api_keys

    def get_quote(self, symbol: str, prefer_history: bool = False) -> QuoteResult:
        asset_type = detect_type(symbol)
        providers = ProviderRegistry.providers

        providers = sorted(
            providers,
            key=lambda p: (
                # 1. History-capable providers first
                not (prefer_history and p.prefers_history),

                # 2. Exclusive crypto providers next
                not (asset_type == "crypto" and len(p.asset_types) == 1 and "crypto" in p.asset_types),

                # 3. Priority last
                p.priority
            )
        )

        # --- 4. Try providers in order, track fallback errors ---
        errors = []

        for provider in providers:
            if asset_type not in provider.asset_types:
                continue

            key = self.api_keys.get(provider.name)
            result = provider.fetch(symbol, key)

            if not result.is_error():
                # Post-processing
                result.history = extract_history(result)
                result.compute_trend()
                return result

            errors.append(f"{provider.name}: {result.error}")

        # --- 5. Final fallback error ---
        return QuoteResult(0, 0, error="; ".join(errors))
