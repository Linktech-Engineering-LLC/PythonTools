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
 Description: Module description here
"""


# PythonTools/market/yahoo.py

import requests
from PythonTools.market.objects import QuoteResult

YAHOO_URL = "https://query1.finance.yahoo.com/v8/finance/chart/"

def fetch_yahoo_crypto(symbol: str) -> QuoteResult:
    url = f"{YAHOO_URL}{symbol.upper()}-USD"

    try:
        r = requests.get(url, timeout=10)
    except Exception as e:
        return QuoteResult(0, 0, error=f"Yahoo request failed: {e}")

    # Bail out early on bad HTTP status
    if r.status_code != 200:
        return QuoteResult(0, 0, error=f"Yahoo HTTP {r.status_code}")

    # Try JSON parsing — if it fails, return None/error immediately
    try:
        data = r.json()
    except Exception:
        return QuoteResult(0, 0, error="Yahoo returned invalid JSON")

    # Validate structure
    try:
        result = data["chart"]["result"][0]
        close = result["indicators"]["quote"][0]["close"]
        last = close[-1]
        prev = close[-2]
        pct = ((last - prev) / prev) * 100
        return QuoteResult(last, pct)
    except Exception:
        return QuoteResult(0, 0, error="Yahoo JSON missing expected fields")
