# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-07
 Modified: 2026-07-07
 File: PythonTools/market/symbols.py
 Version: 1.0.0
 Description: Module description here
"""
COMMODITY_MAP = {
    "GOLD": {
        "yahoo": "GC=F",
        "alphavantage": "XAUUSD",
        "finnhub": "XAUUSD",
    },
    "SILVER": {
        "yahoo": "SI=F",
        "alphavantage": "XAGUSD",
        "finnhub": "XAGUSD",
    },
    "OIL": {
        "yahoo": "CL=F",
        "alphavantage": "WTI",
        "finnhub": "CL",
    },
    "NATGAS": {
        "yahoo": "NG=F",
        "alphavantage": "NATGAS",
        "finnhub": "NG",
    },
    "COPPER": {
        "yahoo": "HG=F",
        "alphavantage": "COPPER",
        "finnhub": "HG",
    },
}

def normalize_commodity(symbol: str, provider: str) -> str:
    s = symbol.upper()
    entry = COMMODITY_MAP.get(s)
    if entry:
        return entry.get(provider, s)
    return s

CRYPTO_MAP = {
    "BTC": {"yahoo": "BTC-USD", "coingecko": "bitcoin", "finnhub": "BINANCE:BTCUSDT"},
    "ETH": {"yahoo": "ETH-USD", "coingecko": "ethereum", "finnhub": "BINANCE:ETHUSDT"},
    "SOL": {"yahoo": "SOL-USD", "coingecko": "solana", "finnhub": "BINANCE:SOLUSDT"},
    "DOGE": {"yahoo": "DOGE-USD", "coingecko": "dogecoin", "finnhub": "BINANCE:DOGEUSDT"},
}

def normalize_crypto(symbol: str, provider_name: str) -> str:
    entry = CRYPTO_MAP.get(symbol.upper())
    if entry:
        return entry.get(provider_name, symbol.upper())
    return symbol.upper()

def normalize_forex(symbol: str) -> dict:
    base, quote = symbol.split("/")
    return {
        "yahoo": f"{base}{quote}=X",
        "alphavantage": f"{base}/{quote}",
        "finnhub": f"OANDA:{base}_{quote}",
    }
