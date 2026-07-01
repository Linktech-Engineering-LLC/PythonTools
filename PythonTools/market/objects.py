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
        provider_key=None,        # NEW
        provider_symbol=None,      # NEW
        trend_result=None
    ):
        self.price = price
        self.pct = pct
        self.provider = provider
        self.timestamp = timestamp
        self.raw = raw or {}
        self.history = history or []
        self.fallback_chain = fallback_chain or []
        self.error = error

        # NEW FIELDS
        self.provider_key = provider_key
        self.provider_symbol = provider_symbol
        self.trend_result = trend_result or TrendResult()
        
    def is_error(self):
        return self.error is not None
