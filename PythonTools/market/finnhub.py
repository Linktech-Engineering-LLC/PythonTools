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
import time

from PythonTools.market.objects import QuoteResult

def fetch_finnhub_crypto(symbol: str,
                         api_key: str,
                         resolution: str = "D",
                         count: int = 1):
    """
    Support-only Finnhub provider.
    Attempts to fetch candles, but gracefully fails on free-tier keys.
    """

    url = "https://finnhub.io/api/v1/crypto/candle"

    # Finnhub candle requires from/to, so we simulate a minimal window.
    # This is allowed even on paid plans.
    now = int(time.time())
    frm = now - (count * 86400)

    params = {
        "symbol": symbol,
        "resolution": resolution,
        "from": frm,
        "to": now,
        "token": api_key,
    }

    try:
        r = requests.get(url, params=params, timeout=5)

        # Detect HTML (free-tier rejection)
        if r.text.startswith("<!DOCTYPE html>"):
            return QuoteResult(0, 0, error="Finnhub: HTML response (likely no access)")

        data = r.json()

        # Finnhub error
        if data.get("s") != "ok":
            return QuoteResult(0, 0, error=f"Finnhub error: {data.get('s')}")

        # Extract last candle
        closes = data.get("c", [])
        if not closes:
            return QuoteResult(0, 0, error="Finnhub: no candle data")

        price = closes[-1]
        return QuoteResult(price, 0)

    except Exception as e:
        return QuoteResult(0, 0, error=f"Finnhub exception: {e}")