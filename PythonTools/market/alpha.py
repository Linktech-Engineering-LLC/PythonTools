# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-07-18
 File: PythonTools/market/alpha.py
 Version: 1.0.0
 Description:
            Provides AlphaVantage integration for equities, commodities, and forex quotes.
            Uses the GLOBAL_QUOTE endpoint to retrieve current price, percent change, and
            associated quote metadata. The full AlphaVantage response is preserved and
            returned via QuoteResult.raw for downstream processing. This module serves as
            the primary provider for non‑crypto tickers.
"""

# PythonTools/market/alpha.py

import requests

from ..market.objects import QuoteResult

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

    # NEW: extract timestamp if available
    timestamp = quote.get("07. latest trading day")

    # NEW: preserve full raw metadata
    raw = quote

    # NEW: include provider name
    return QuoteResult(
        price=price,
        pct=pct,
        provider="alphavantage",
        timestamp=timestamp,
        raw=quote,
        provider_key=key,
        provider_symbol=symbol
    )

def fetch_alpha_history(symbol: str, key: str):
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": key,
        "outputsize": "compact"
    }

    try:
        r = requests.get(url, params=params, timeout=10)
        data = r.json()
    except Exception:
        return []

    # Rate limit or error
    if "Note" in data or "Information" in data:
        return []  # gracefully degrade

    series = data.get("Time Series (Daily)")
    if not series:
        return []

    closes = []
    for date in sorted(series.keys()):
        try:
            closes.append(float(series[date]["4. close"]))
        except Exception:
            continue

    return closes
