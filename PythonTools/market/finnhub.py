# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/market/finnhub.py
 Version: 1.0.0
 Description: Module description here
"""
# PythonTools/market/finnhub.py

import requests

from PythonTools.finance.api_keys import get_api_key
from PythonTools.market.objects import QuoteResult

FINNHUB_URL = "https://finnhub.io/api/v1/crypto/candle"

def fetch_finnhub_crypto(symbol: str) -> QuoteResult:
    key = get_api_key("finnhub")
    if not key:
        return QuoteResult(0, 0, error="Missing Finnhub API key")

    # Finnhub uses BINANCE:<symbol>USDT
    pair = f"BINANCE:{symbol.upper()}USDT"

    params = {
        "symbol": pair,
        "resolution": "D",
        "count": 2,
        "token": key
    }

    r = requests.get(FINNHUB_URL, params=params, timeout=10)
    data = r.json()

    if data.get("s") != "ok":
        return QuoteResult(0, 0, error=f"Finnhub error: {data.get('s')}")

    try:
        close_prev = data["c"][0]
        close_now = data["c"][1]
        pct = (close_now - close_prev) / close_prev if close_prev else 0
    except Exception:
        return QuoteResult(0, 0, error="Malformed Finnhub response")

    return QuoteResult(close_now, pct)
