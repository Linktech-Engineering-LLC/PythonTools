# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-14
 Modified: 2026-07-18
 File: PythonTools/market/__init__.py
 Version: 1.0.0
 Description: Package Library for the market module
"""


from PythonTools import __version__

from .alpha import ALPHA_URL, fetch_alpha_history, fetch_alpha_stock
from .coingecko import fetch_coingecko_crypto
from .finnhub import fetch_finnhub_crypto
from .objects import TrendResult, QuoteResult
from .router import ALIASES, detect_type, extract_history, MarketObjectEngine
from .symbols import (
    COMMODITY_MAP, 
    CRYPTO_MAP,
    INDEX_MAP,
)
from .trend import (
    analyze_trend, 
    compute_multi_window_trend, 
    compute_trend_and_slope,
    compute_trend_strength,
    compute_volatility,
    detect_reversal,
)
from .yahoo import fetch_yahoo_crypto, fetch_yahoo_stock, fetch_yahoo_stock_history