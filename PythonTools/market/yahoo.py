# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/market/yahoo.py
 Version: 1.0.0
 Description:
            Provides Yahoo Finance fallback support for cryptocurrency tickers. Retrieves
            chart metadata including timestamps and close‑price arrays, enabling basic
            historical extraction when other providers fail. Full Yahoo chart responses
            are preserved in QuoteResult.raw for downstream consumers.
            
            Yahoo Finance fallback providers using yahooquery.
"""

from yahooquery import Ticker
from PythonTools.market.objects import QuoteResult

def fetch_yahoo_crypto(symbol: str) -> QuoteResult:
    yf_symbol = f"{symbol.upper()}-USD"

    try:
        t = Ticker(yf_symbol)
        df = t.history(period="1mo", interval="1d")
    except Exception as exc:
        return QuoteResult(0, 0, error=f"YahooQuery exception: {exc}")

    if df is None or len(df) == 0:
        return QuoteResult(0, 0, error="YahooQuery: no history data")

    try:
        closes = df["close"].tolist()
    except Exception:
        return QuoteResult(0, 0, error="YahooQuery: malformed history")

    if not closes:
        return QuoteResult(0, 0, error="YahooQuery: empty close array")

    price = closes[-1]

    raw_dict = {
        col: [float(v) for v in series.tolist() if v is not None]
        for col, series in df.items()
    }
    raw_dict = dict(raw_dict)

    return QuoteResult(
        price=price,
        pct=0,
        provider="yahoo_crypto",
        timestamp=None,
        raw=raw_dict
    )

def fetch_yahoo_stock(symbol: str) -> QuoteResult:
    try:
        t = Ticker(symbol)
        df = t.history(period="1mo", interval="1d")
    except Exception as exc:
        return QuoteResult(0, 0, error=f"YahooQuery exception: {exc}")

    if df is None or len(df) == 0:
        return QuoteResult(0, 0, error="YahooQuery: no history data")

    try:
        closes = df["close"].tolist()
    except Exception:
        return QuoteResult(0, 0, error="YahooQuery: malformed history")

    if not closes:
        return QuoteResult(0, 0, error="YahooQuery: empty close array")

    price = closes[-1]

    # IMPORTANT: convert DataFrame to dict
    raw_dict = {
        col: [float(v) for v in series.tolist() if v is not None]
        for col, series in df.items()
    }
    raw_dict = dict(raw_dict)

    return QuoteResult(
        price=price,
        pct=0,
        provider="yahoo_stock",
        timestamp=None,
        raw=raw_dict
    )

def fetch_yahoo_stock_history(symbol: str):
    """
    History-only version for trend extraction.
    """
    try:
        t = Ticker(symbol)
        data = t.history(period="1mo", interval="1d")
    except Exception:
        return []

    try:
        closes = data["close"].tolist()
        return [c for c in closes if c is not None]
    except Exception:
        return []
