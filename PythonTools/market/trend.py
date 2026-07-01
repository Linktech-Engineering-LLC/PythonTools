#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
File: trend.py
Author: Leon McClatchey
Company: Linktech Engineering LLC
Created: 2026-07-01
Modified: 2026-07-01
Required: Python 3.10+

Description: Description of this module

"""

from PythonTools.market.alpha import fetch_alpha_history
from PythonTools.market.objects import QuoteResult

def extract_history(result):
    raw = result.raw
    provider = result.provider

    match provider:

        case "coingecko":
            return raw.get("market_data", {}) \
                      .get("sparkline_7d", {}) \
                      .get("price", [])

        case "finnhub":
            # Finnhub candles: raw["c"] = closes
            return raw.get("c", [])

        case "yahoo_crypto" | "yahoo_stock":
            try:
                return raw.get("close", [])
            except Exception:
                return []
            
        case "yahoo":
            # legacy Yahoo (requests/httpx chart API)
            try:
                return raw["chart"]["result"][0]["indicators"]["quote"][0]["close"]
            except Exception:
                return []

        case "alphavantage":
            # your existing AlphaVantage history fetcher
            return fetch_alpha_history(
                raw.get("provider_symbol"),
                raw.get("provider_key")
            )

        case _:
            return []
        
def compute_trend_and_slope(history: list[float]) -> tuple[str, float]:
    if not history or len(history) < 2:
        return ("unknown", 0.0)

    # Slope: magnitude of movement
    slope = history[-1] - history[0]

    # Directional consistency: count ups vs downs
    ups = 0
    downs = 0

    for i in range(1, len(history)):
        if history[i] > history[i - 1]:
            ups += 1
        elif history[i] < history[i - 1]:
            downs += 1

    # Hybrid classification
    if slope > 0 and ups > downs:
        trend = "up"
    elif slope < 0 and downs > ups:
        trend = "down"
    else:
        trend = "flat"

    return (trend, slope)

def compute_volatility(history: list[float]) -> float:
    if len(history) < 2:
        return 0.0

    mean = sum(history) / len(history)
    var = sum((x - mean) ** 2 for x in history) / (len(history) - 1)
    return var ** 0.5

def compute_trend_strength(history: list[float]) -> float:
    if len(history) < 2:
        return 0.0

    slope = history[-1] - history[0]
    vol = compute_volatility(history)

    if vol == 0:
        return slope  # perfectly stable

    return slope / vol

def detect_reversal(history: list[float]) -> bool:
    n = len(history)
    if n < 4:
        return False

    mid = n // 2
    first_slope = history[mid] - history[0]
    second_slope = history[-1] - history[mid]

    return (first_slope > 0 and second_slope < 0) or \
           (first_slope < 0 and second_slope > 0)

def sma(history: list[float], window: int) -> float:
    if len(history) < window:
        return sum(history) / len(history)
    return sum(history[-window:]) / window

def ema(history: list[float], window: int) -> float:
    if not history:
        return 0.0

    alpha = 2 / (window + 1)
    ema_val = history[0]

    for price in history[1:]:
        ema_val = alpha * price + (1 - alpha) * ema_val

    return ema_val

def compute_multi_window_trend(history: list[float]):
    return {
        "short": compute_trend_and_slope(history[-5:]),
        "medium": compute_trend_and_slope(history[-10:]),
        "long": compute_trend_and_slope(history[-20:])
    }

def analyze_trend(history: list[float]) -> dict:
    trend, slope = compute_trend_and_slope(history)
    vol = compute_volatility(history)
    strength = compute_trend_strength(history)
    reversal = detect_reversal(history)

    return {
        "trend": trend,
        "slope": slope,
        "volatility": vol,
        "strength": strength,
        "reversal": reversal,
        "sma_5": sma(history, 5),
        "sma_10": sma(history, 10),
        "ema_5": ema(history, 5),
        "ema_10": ema(history, 10),
        "windows": compute_multi_window_trend(history)
    }
