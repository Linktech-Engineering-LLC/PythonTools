# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/market/alpha.py
 Version: 1.0.0
 Description: Module description here
"""

# PythonTools/market/alpha.py

import requests

from PythonTools.market.objects import QuoteResult

ALPHA_URL = "https://www.alphavantage.co/query"

def fetch_alpha_stock(symbol: str, key: str) -> QuoteResult:
    if not key:
        return QuoteResult(0, 0, error="Missing AlphaVantage API key")

    params = {
        "function": "GLOBAL_QUOTE",
        "symbol": symbol,
        "apikey": key
    }

    r = requests.get(ALPHA_URL, params=params, timeout=10)
    data = r.json()

    # Error handling
    for err in ("Note", "Information", "Error Message"):
        if err in data:
            return QuoteResult(0, 0, error=data[err])

    quote = data.get("Global Quote")
    if not quote:
        return QuoteResult(0, 0, error="No Global Quote returned")

    try:
        price = float(quote["05. price"])
        pct = float(quote["10. change percent"].replace("%", "")) / 100.0
    except Exception:
        return QuoteResult(0, 0, error="Malformed AlphaVantage response")

    return QuoteResult(price, pct)
