# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-07-18
 File: PythonTools/market/finnhub.py
 Version: 1.0.0
 Description:
            Implements Finnhub support for cryptocurrency OHLCV candle data. Attempts to
            retrieve recent historical candles using the crypto/candle endpoint and
            gracefully handles free‑tier limitations. When successful, returns full OHLCV
            arrays and timestamps through QuoteResult.raw, enabling trend and history
            analysis for supported symbols.
"""
# PythonTools/market/finnhub.py

import requests
import time

def fetch_finnhub_crypto(symbol: str,
                         api_key: str,
                         resolution: str = "D",
                         count: int = 1):

    url = "https://finnhub.io/api/v1/crypto/candle"

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

        # Free-tier rejection
        if r.text.startswith("<!DOCTYPE html>"):
            return {"error": "Finnhub: HTML response (likely no access)"}

        data = r.json()

        if data.get("s") != "ok":
            return {"error": f"Finnhub error: {data.get('s')}"}

        closes = data.get("c", [])
        if not closes:
            return {"error": "Finnhub: no candle data"}

        return data

    except Exception as e:
        return {"error": f"Finnhub exception: {e}"}
def fetch_finnhub_commodity(symbol: str,
                            api_key: str,
                            resolution: str = "D",
                            count: int = 1):

    url = "https://finnhub.io/api/v1/forex/candle"

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

        if r.text.startswith("<!DOCTYPE html>"):
            return {"error": "Finnhub: HTML response (likely no access)"}

        data = r.json()

        if data.get("s") != "ok":
            return {"error": f"Finnhub error: {data.get('s')}"}

        closes = data.get("c", [])
        if not closes:
            return {"error": "Finnhub: no candle data"}

        return data

    except Exception as e:
        return {"error": f"Finnhub exception: {e}"}

def fetch_finnhub_stock(symbol: str,
                        api_key: str,
                        resolution: str = "D",
                        count: int = 1):

    url = "https://finnhub.io/api/v1/stock/candle"

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

        # Free-tier rejection
        if r.text.startswith("<!DOCTYPE html>"):
            return {"error": "Finnhub: HTML response (likely no access)"}

        data = r.json()

        if data.get("s") != "ok":
            return {"error": f"Finnhub error: {data.get('s')}"}

        closes = data.get("c", [])
        if not closes:
            return {"error": "Finnhub: no candle data"}

        return data

    except Exception as e:
        return {"error": f"Finnhub exception: {e}"}
