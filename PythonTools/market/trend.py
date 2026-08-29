#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
File: trend.py
Author: Leon McClatchey
Company: Linktech Engineering LLC
Created: 2026-07-01
 Modified: 2026-08-29
Required: Python 3.10+

Description: Description of this module

"""
import statistics
import math
from typing import Sequence

def analyze_trend(history: Sequence[float]) -> dict:
    # Sanitize history: remove NaN and non-numeric values
    history = [x for x in history if isinstance(x, (int, float)) and not math.isnan(x)]

    if not history or len(history) < 2:
        return {
            "trend": "unknown",
            "slope": 0.0,
            "volatility": 0.0,
            "strength": 0.0,
            "reversal": False,
            "sma_5": None,
            "sma_10": None,
            "ema_5": None,
            "ema_10": None,
            "windows": {
                "short": ("unknown", 0.0),
                "medium": ("unknown", 0.0),
                "long": ("unknown", 0.0)
            }
        }

    trend, slope = compute_trend_and_slope(history)
    slope = safe(slope)

    vol = compute_volatility(history)
    strength = safe(compute_trend_strength(history))
    reversal = detect_reversal(history)

    windows_raw = compute_multi_window_trend(history)
    windows = {
        "short": (windows_raw["short"][0], safe(windows_raw["short"][1])),
        "medium": (windows_raw["medium"][0], safe(windows_raw["medium"][1])),
        "long": (windows_raw["long"][0], safe(windows_raw["long"][1]))
    }

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
        "windows": windows
    }

def compute_multi_window_trend(history: Sequence[float]):
    return {
        "short": compute_trend_and_slope(history[-5:]),
        "medium": compute_trend_and_slope(history[-10:]),
        "long": compute_trend_and_slope(history[-20:])
    }

def compute_trend_and_slope(history: Sequence[float]) -> tuple[str, float]:
    if not history or len(history) < 2:
        return ("unknown", 0.0)

    slope = safe(history[-1] - history[0])

    ups = 0
    downs = 0

    for i in range(1, len(history)):
        if history[i] > history[i - 1]:
            ups += 1
        elif history[i] < history[i - 1]:
            downs += 1

    if slope > 0 and ups > downs:
        trend = "up"
    elif slope < 0 and downs > ups:
        trend = "down"
    else:
        trend = "flat"

    return (trend, slope)

def compute_trend_strength(history: Sequence[float]) -> float:
    if len(history) < 2:
        return 0.0

    slope = safe(history[-1] - history[0])
    vol = compute_volatility(history)

    if vol == 0:
        return slope

    return safe(slope / vol)

def compute_volatility(history):
    # Filter out NaN values
    clean = [x for x in history if isinstance(x, (int, float)) and not math.isnan(x)]

    if len(clean) < 2:
        return 0.0

    return statistics.stdev(clean)

def detect_reversal(history: Sequence[float]) -> bool:
    n = len(history)
    if n < 4:
        return False

    mid = n // 2

    first_slope = safe(history[mid] - history[0])
    second_slope = safe(history[-1] - history[mid])

    return (first_slope > 0 and second_slope < 0) or \
           (first_slope < 0 and second_slope > 0)

def ema(history: Sequence[float], window: int) -> float:
    if not history:
        return 0.0

    alpha = 2 / (window + 1)
    ema_val = history[0]

    for price in history[1:]:
        ema_val = alpha * price + (1 - alpha) * ema_val

    return ema_val

def sma(history: Sequence[float], window: int) -> float:
    if len(history) < window:
        return sum(history) / len(history)
    return sum(history[-window:]) / window

def safe(x):
    return x if isinstance(x, (int, float)) and not math.isnan(x) else 0.0

