# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-07
 Modified: 2026-07-18
 File: PythonTools/market/symbols.py
 Version: 1.0.0
 Description: Module description here
"""

COMMODITY_MAP = {
    "GOLD": {
        "yahoo": "GC=F",
        "alphavantage": "XAUUSD",
        "finnhub": "OANDA:XAU_USD",
    },
    "SILVER": {
        "yahoo": "SI=F",
        "alphavantage": "XAGUSD",
        "finnhub": "OANDA:XAG_USD",
    },
    "OIL": {
        "yahoo": "CL=F",
        "alphavantage": "WTI",
        "finnhub": "OANDA:OIL_USD",   # or BRENT_USD if you prefer
    },
    "NATGAS": {
        "yahoo": "NG=F",
        "alphavantage": "NATGAS",
        "finnhub": "OANDA:NATGAS_USD",
    },
    "COPPER": {
        "yahoo": "HG=F",
        "alphavantage": "COPPER",
        "finnhub": "OANDA:XCU_USD",
    },
}
CRYPTO_MAP = {
    "BTC": {
        "yahoo": "BTC-USD",
        "coingecko": "bitcoin",
        "finnhub": "BINANCE:BTCUSDT",
    },
    "ETH": {
        "yahoo": "ETH-USD",
        "coingecko": "ethereum",
        "finnhub": "BINANCE:ETHUSDT",
    },
    "SOL": {
        "yahoo": "SOL-USD",
        "coingecko": "solana",
        "finnhub": "BINANCE:SOLUSDT",
    },
    "DOGE": {
        "yahoo": "DOGE-USD",
        "coingecko": "dogecoin",
        "finnhub": "BINANCE:DOGEUSDT",
    },

    # Merged from COINGECKO_MAP
    "LTC": {
        "yahoo": "LTC-USD",
        "coingecko": "litecoin",
        "finnhub": "BINANCE:LTCUSDT",
    },
    "XRP": {
        "yahoo": "XRP-USD",
        "coingecko": "ripple",
        "finnhub": "BINANCE:XRPUSDT",
    },
    "ADA": {
        "yahoo": "ADA-USD",
        "coingecko": "cardano",
        "finnhub": "BINANCE:ADAUSDT",
    },
    "DOT": {
        "yahoo": "DOT-USD",
        "coingecko": "polkadot",
        "finnhub": "BINANCE:DOTUSDT",
    },
}
INDEX_MAP = {
    "^GSPC": {"yahoo": "^GSPC"},
    "^DJI": {"yahoo": "^DJI"},
    "^IXIC": {"yahoo": "^IXIC"},
    "^RUT": {"yahoo": "^RUT"},
    "^VIX": {"yahoo": "^VIX"},
}

def normalize_commodity(symbol: str, provider: str) -> str:
    s = symbol.upper()
    entry = COMMODITY_MAP.get(s)
    if entry:
        return entry.get(provider, s)
    return s


def normalize_crypto(symbol: str) -> str:
    return symbol.upper()

def normalize_forex(symbol: str) -> dict:
    base, quote = symbol.split("/")
    return {
        "yahoo": f"{base}{quote}=X",
        "alphavantage": f"{base}/{quote}",
        "finnhub": f"OANDA:{base}_{quote}",
    }
