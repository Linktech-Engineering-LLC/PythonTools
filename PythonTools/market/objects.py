# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-08-29
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
import math

from dataclasses import dataclass, field
from typing import Optional, Dict, Any

from .trend import (
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
        # Store raw first, then sanitize it
        self.raw = raw or {}
        self.raw = self._sanitize_raw(self.raw)

        # Build history AFTER raw is sanitized
        closes = self.raw.get("close")
        if history:
            # sanitize provided history
            self.history = [
                clean_number(x) for x in history
                if isinstance(x, (int, float)) and not math.isnan(x)
            ]
        elif isinstance(closes, list):
            # derive history from sanitized raw
            self.history = [
                clean_number(x) for x in closes
                if isinstance(x, (int, float)) and not math.isnan(x)
            ]
        else:
            self.history = []

        # Now apply price fallback AFTER history is ready
        if price is None or (isinstance(price, float) and math.isnan(price)):
            # fallback to last valid close
            if self.history:
                price = self.history[-1]

        self.price = clean_number(price)
        self.pct = clean_number(pct)

        self.provider = provider
        self.timestamp = timestamp
        self.fallback_chain = fallback_chain or []
        self.error = error

        self.provider_key = provider_key
        self.provider_symbol = provider_symbol

        self.trend_result = trend_result or TrendResult()
        self.trend_data = trend_data or {}

    def compute_trend(self):
        """Compute all trend metrics in one place."""
        # Sanitize history: remove None and NaN
        self.history = [
            x for x in self.history
            if isinstance(x, (int, float)) and not math.isnan(x)
        ]
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
        slope = clean_number(slope) or 0.0

        vol = clean_number(compute_volatility(self.history)) or 0.0
        strength = clean_number(compute_trend_strength(self.history)) or 0.0

        reversal = bool(detect_reversal(self.history))

        windows_raw = compute_multi_window_trend(self.history)
        windows = {
            k: (v[0], clean_number(v[1]) or 0.0)
            for k, v in windows_raw.items()
        }

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
    def _sanitize_raw(self, raw: Any) -> Any:
        """Recursively sanitize numeric fields in the raw provider payload."""
        def scrub(value):
            if isinstance(value, (int, float)):
                return clean_number(value)
            if isinstance(value, list):
                out = []
                for v in value:
                    sv = scrub(v)
                    if isinstance(sv, (int, float)) and not math.isnan(sv):
                        out.append(sv)
                return out
            if isinstance(value, dict):
                return {k: scrub(v) for k, v in value.items()}
            return value

        return scrub(raw)

def clean_number(x):
    if isinstance(x, (int, float)) and not math.isnan(x):
        return x
    return None
