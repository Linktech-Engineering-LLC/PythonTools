# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/market/coingecko.py
 Version: 1.0.0
 Description:
            Implements the CoinGecko provider for cryptocurrency market data. This module
            maps common ticker symbols to CoinGecko asset IDs and retrieves full market
            metadata using the /coins/{id} endpoint. Returned data includes current price,
            percent changes, sparkline history, market statistics, and extended metadata
            such as categories, community metrics, developer activity, and descriptive
            content. Results are normalized into QuoteResult objects.
"""

import requests
from PythonTools.market.objects import QuoteResult

COINGECKO_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "DOGE": "dogecoin",
    "LTC": "litecoin",
    "XRP": "ripple",
    "ADA": "cardano",
    "SOL": "solana",
    "DOT": "polkadot",
}


def fetch_coingecko_crypto(symbol: str, key: str) -> QuoteResult:
    cg_id = COINGECKO_MAP.get(symbol.upper())
    if not cg_id:
        return QuoteResult(0, 0, error="CoinGecko: unknown symbol")

    url = (
        f"https://api.coingecko.com/api/v3/coins/{cg_id}"
        "?localization=false"
        "&tickers=false"
        "&market_data=true"
        "&community_data=false"
        "&developer_data=false"
        "&sparkline=true"
    )
    headers = {"x-cg-pro-api-key": key} if key else {}

    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
    except Exception as exc:
        return QuoteResult(0, 0, error=f"CoinGecko request failed: {exc}")

    if "error" in data:
        return QuoteResult(0, 0, error=f"CoinGecko error: {data['error']}")

    market = data.get("market_data", {})
    if not market:
        return QuoteResult(0, 0, error="CoinGecko: no market data")

    price = market.get("current_price", {}).get("usd")
    pct = market.get("price_change_percentage_24h", 0) / 100.0
    timestamp = data.get("last_updated")

    if price is None:
        return QuoteResult(0, 0, error="Coingecko: missing price")

    return QuoteResult(
        price=price,
        pct=pct,
        provider="coingecko",
        timestamp=timestamp,
        raw=data
    )
