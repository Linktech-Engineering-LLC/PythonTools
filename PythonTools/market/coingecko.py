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
from PythonTools.finance.api_keys import get_api_key
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


def fetch_coingecko_crypto(symbol: str) -> QuoteResult:
    try:
        key = get_api_key("coingecko")
    except Exception:
        return QuoteResult(0, 0, error="Missing CoinGecko API key")

    cg_id = COINGECKO_MAP.get(symbol.upper())
    if not cg_id:
        return QuoteResult(0, 0, error="CoinGecko: unknown symbol")


    url = (
        "https://api.coingecko.com/api/v3/simple/price"
        f"?ids={cg_id}&vs_currencies=usd&include_24hr_change=true"
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

    if cg_id not in data:
        return QuoteResult(0, 0, error="CoinGecko returned no data")

    entry = data[cg_id]

    try:
        last = float(entry["usd"])
        pct = float(entry.get("usd_24h_change", 0.0))
    except Exception:
        return QuoteResult(0, 0, error="CoinGecko returned invalid fields")

    return QuoteResult(last, pct)
