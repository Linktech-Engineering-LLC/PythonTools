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
 Description: Module description here
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
        "https://api.coingecko.com/api/v3/coins/markets"
        f"?vs_currency=usd&ids={cg_id}"
        "&order=market_cap_desc"
        "&per_page=1&page=1"
        "&sparkline=true"
        "&price_change_percentage=1h,24h,7d,14d,30d,200d,1y"
    )

    headers = {
        "x-cg-demo-api-key": key
    }

    try:
        r = requests.get(url, timeout=10)
    except Exception as e:
        return QuoteResult(0, 0, error=f"CoinGecko request failed: {e}")

    if r.status_code != 200:
        return QuoteResult(0, 0, error=f"CoinGecko HTTP {r.status_code}")

    try:
        data = r.json()
    except Exception:
        return QuoteResult(0, 0, error="CoinGecko returned invalid JSON")

    # /coins/markets ALWAYS returns a list
    if not isinstance(data, list) or not data:
        return QuoteResult(0, 0, error="CoinGecko returned no data")

    entry = data[0]

    # Validate ID match
    if entry.get("id") != cg_id:
        return QuoteResult(0, 0, error="CoinGecko ID mismatch")

    try:
        last = float(entry["current_price"])
        pct = float(entry.get("price_change_percentage_24h", 0.0))
    except Exception:
        return QuoteResult(0, 0, error="CoinGecko returned invalid fields")

    return QuoteResult(
        price=last, 
        pct=pct,
        provider="coingecko",
        timestamp=entry.get("last_updated"),
        raw=entry,
        )
