# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/market/objects.py
 Version: 1.0.0
 Description:
            Defines the core QuoteResult data structure used throughout the market
            engine. QuoteResult acts as a unified container for all provider responses,
            including price, percent change, provider metadata, timestamps, raw payloads,
            historical arrays, trend slope, and fallback routing information. This module
            provides a consistent interface for downstream consumers regardless of which
            market data provider was used.

"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from PythonTools.market.trend import (
    compute_trend_and_slope, 
    compute_volatility, 
    compute_trend_strength,
    detect_reversal,
    compute_multi_window_trend,
    sma,
    ema
)

@dataclass
class TrendResult:
    trend: Optional[str] = None          # "up", "down", "flat", "unknown"
    slope: Optional[float] = None        # numeric slope
    volatility: Optional[float] = None   # std dev
    strength: Optional[float] = None     # slope / volatility
    reversal: Optional[bool] = None      # True/False
    windows: Optional[Dict[str, Any]] = None  # short/medium/long window trends

    def to_json(self) -> dict:
        """Return only fields that are not None."""
        out = {}
        if self.trend is not None:
            out["trend"] = self.trend
        if self.slope is not None:
            out["slope"] = self.slope
        if self.volatility is not None:
            out["volatility"] = self.volatility
        if self.strength is not None:
            out["strength"] = self.strength
        if self.reversal is not None:
            out["reversal"] = self.reversal
        if self.windows is not None:
            out["windows"] = self.windows
        return out

@dataclass
class QuoteResult:
    def __init__(
        self,
        price,
        pct,
        provider=None,
        timestamp=None,
        raw=None,
        history=None,
        fallback_chain=None,
        error=None,
        provider_key=None,
        provider_symbol=None,
        trend_result=None,
        trend_data=None
    ):
        self.price = price
        self.pct = pct
        self.provider = provider
        self.timestamp = timestamp
        self.raw = raw or {}
        self.history = history or []
        self.fallback_chain = fallback_chain or []
        self.error = error

        self.provider_key = provider_key
        self.provider_symbol = provider_symbol

        # TrendResult dataclass
        self.trend_result = trend_result or TrendResult()

        # Full trend analysis dict
        self.trend_data = trend_data or {}

    def compute_trend(self):
        """Compute all trend metrics in one place."""
        if not self.history or len(self.history) < 2:
            self.trend_result = TrendResult(
                trend="unknown",
                slope=0.0,
                volatility=0.0,
                strength=0.0,
                reversal=False,
                windows={}
            )
            self.trend_data = {}
            return

        # Use your existing functions
        trend, slope = compute_trend_and_slope(self.history)
        vol = compute_volatility(self.history)
        strength = compute_trend_strength(self.history)
        reversal = detect_reversal(self.history)
        windows = compute_multi_window_trend(self.history)

        # Fill TrendResult dataclass
        self.trend_result = TrendResult(
            trend=trend,
            slope=slope,
            volatility=vol,
            strength=strength,
            reversal=reversal,
            windows=windows
        )

        # Fill trend_data dict (JSON-friendly)
        self.trend_data = {
            "trend": trend,
            "slope": slope,
            "volatility": vol,
            "strength": strength,
            "reversal": reversal,
            "sma_5": sma(self.history, 5),
            "sma_10": sma(self.history, 10),
            "ema_5": ema(self.history, 5),
            "ema_10": ema(self.history, 10),
            "windows": windows
        }

    def is_error(self):
        return self.error is not None
