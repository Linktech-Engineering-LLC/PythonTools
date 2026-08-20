# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-20
 File: PythonTools/weather/alerts.py
 Version: 1.0.0
 Description: Weather Alerts Module
"""
"""
PythonTools.weather.alerts
--------------------------

NWS alert fetching, normalization, and categorization.

This module is provider-specific (NWS only), but the output schema
is provider-agnostic and matches the unified weather JSON schema.

All functions are deterministic and freeze-safe.
"""

import json
import urllib.request
import time

from .providers.builders import build_nws_alerts_url

# ---------------------------------------------------------------------------
# Alert Cache
# ---------------------------------------------------------------------------


_ALERT_CACHE = {
    "timestamp": 0,
    "lat": None,
    "lon": None,
    "data": None
}

ALERT_CACHE_TTL = 60   # seconds

# ---------------------------------------------------------------------------
# Fetch NWS Alerts
# ---------------------------------------------------------------------------

def fetch_nws_alerts(lat, lon, timeout=10):
    """
    Fetch active NWS alerts for a given lat/lon.

    Returns raw JSON (dict) or empty list on error.
    """

    url = build_nws_alerts_url(lat, lon)

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "NMS_Tools/Weather"}
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("features", [])
    except Exception:
        return []

def fetch_cached_alerts(lat, lon, timeout=10):
    """
    Fetch alerts with caching.
    Cache is keyed by lat/lon and expires after ALERT_CACHE_TTL seconds.
    """

    now = time.time()

    # Cache hit: same location and not expired
    if (_ALERT_CACHE["lat"] == lat and
        _ALERT_CACHE["lon"] == lon and
        (now - _ALERT_CACHE["timestamp"]) < ALERT_CACHE_TTL):

        return _ALERT_CACHE["data"]

    # Cache miss: fetch fresh alerts
    raw = fetch_nws_alerts(lat, lon, timeout)
    normalized = normalize_alerts(raw)

    # Update cache
    _ALERT_CACHE["timestamp"] = now
    _ALERT_CACHE["lat"] = lat
    _ALERT_CACHE["lon"] = lon
    _ALERT_CACHE["data"] = normalized

    return normalized

# ---------------------------------------------------------------------------
# Categorization Rules
# ---------------------------------------------------------------------------

def categorize_alert(event_name):
    """
    Map NWS event names to unified categories.

    Categories:
        fire, heat, cold, wind, winter, flood,
        convective, air_quality, uv, other
    """

    if not event_name:
        return "other"

    name = event_name.lower()

    # Fire
    if "fire" in name:
        return "fire"

    # Heat
    if "heat" in name or "excessive heat" in name:
        return "heat"

    # Cold
    if "freeze" in name or "frost" in name or "cold" in name or "wind chill" in name:
        return "cold"

    # Wind
    if "wind" in name and "high wind" in name:
        return "wind"

    # Winter
    if any(x in name for x in ["snow", "blizzard", "winter", "ice", "sleet"]):
        return "winter"

    # Flood
    if "flood" in name or "flash flood" in name:
        return "flood"

    # Convective (thunderstorms, tornadoes)
    if any(x in name for x in ["thunderstorm", "tornado", "severe storm"]):
        return "convective"

    # Air Quality
    if "air quality" in name or "ozone" in name:
        return "air_quality"

    # UV
    if "uv" in name:
        return "uv"

    return "other"


# ---------------------------------------------------------------------------
# Normalize NWS Alerts
# ---------------------------------------------------------------------------

def normalize_alerts(raw_alerts):
    """
    Normalize NWS alert features into unified schema.

    Input: raw list of NWS alert features
    Output:
        {
            "count": int,
            "active": [
                {
                    "event": str,
                    "category": str,
                    "severity": str,
                    "certainty": str,
                    "urgency": str,
                    "headline": str,
                    "description": str,
                    "instruction": str,
                    "effective": str,
                    "expires": str,
                    "area": [str],
                    "sender": str
                }
            ]
        }
    """

    normalized = []

    for feature in raw_alerts:
        props = feature.get("properties", {})

        event = props.get("event")
        category = categorize_alert(event)

        normalized.append({
            "event": event,
            "category": category,
            "severity": props.get("severity"),
            "certainty": props.get("certainty"),
            "urgency": props.get("urgency"),
            "headline": props.get("headline"),
            "description": props.get("description"),
            "instruction": props.get("instruction"),
            "effective": props.get("effective"),
            "expires": props.get("expires"),
            "area": props.get("affectedZones", []),
            "sender": props.get("senderName"),
            "icon": alert_icon(category),
            "context": alert_context(category, props.get("severity"), event),
            "color": alert_color(props.get("severity"))
        })

    return {
        "count": len(normalized),
        "active": normalized
    }


# ---------------------------------------------------------------------------
# Unified Alert Enrichment
# ---------------------------------------------------------------------------

def add_alerts(provider, lat, lon, data, timeout=10):
    """
    Add alerts to the unified weather data.

    provider: "nws" or "open-meteo"
    data: dict being enriched

    For Open-Meteo: alerts = empty
    For NWS: alerts = normalized NWS alerts
    """

    if provider != "nws":
        data["alerts"] = {
            "count": 0,
            "active": []
        }
        return data

    raw = fetch_nws_alerts(lat, lon, timeout)
    normalized = normalize_alerts(raw)
    data["alerts"] = normalized
    return data

# ---------------------------------------------------------------------------
# Alert Icon Mapping
# ---------------------------------------------------------------------------

def alert_icon(category):
    """
    Map unified alert categories to icon filenames.

    Categories:
        convective, flood, winter, fire, wind,
        heat, cold, air_quality, uv, other
    """

    match category:
        case "convective":
            # Tornado / Severe Thunderstorm
            return "wi-thunderstorm.svg"

        case "flood":
            # Flood / Flash Flood
            return "wi-flood.svg"

        case "winter":
            # Blizzard / Winter Storm / Ice Storm
            return "wi-snow-wind.svg"

        case "fire":
            # Red Flag Warning
            return "wi-fire.svg"

        case "wind":
            # High Wind Warning / Wind Advisory
            return "wi-strong-wind.svg"

        case "heat":
            # Excessive Heat Warning / Heat Advisory
            return "wi-hot.svg"

        case "cold":
            # Freeze Warning / Frost Advisory / Wind Chill
            return "wi-thermometer-exterior.svg"

        case "air_quality":
            # Air Quality Alert
            return "wi-smoke.svg"

        case "uv":
            # UV Alert
            return "wi-day-sunny.svg"

        case _:
            # Fallback
            return "wi-alert.svg"
# ---------------------------------------------------------------------------
# Alert Context Mapping
# ---------------------------------------------------------------------------

def alert_context(category, severity, event):
    """
    Produce a short human-readable context string for an alert.

    Inputs:
        category: unified category (convective, flood, winter, etc.)
        severity: NWS severity (Extreme, Severe, Moderate, Minor)
        event: raw NWS event name

    Output:
        A short descriptive context string.
    """

    # Normalize severity
    sev = (severity or "").lower()

    # Severity prefix
    if sev == "extreme":
        prefix = "Extreme"
    elif sev == "severe":
        prefix = "Severe"
    elif sev == "moderate":
        prefix = "Moderate"
    elif sev == "minor":
        prefix = "Minor"
    else:
        prefix = ""

    # Category-based context
    match category:
        case "convective":
            # Tornado / Severe Thunderstorm
            base = "Convective weather alert"
        case "flood":
            base = "Flooding alert"
        case "winter":
            base = "Winter weather alert"
        case "fire":
            base = "Fire weather alert"
        case "wind":
            base = "High wind alert"
        case "heat":
            base = "Heat alert"
        case "cold":
            base = "Cold weather alert"
        case "air_quality":
            base = "Air quality alert"
        case "uv":
            base = "UV exposure alert"
        case _:
            base = "Weather alert"

    # If we have a severity prefix, prepend it
    if prefix:
        return f"{prefix} {base.lower()}"

    # Otherwise return base
    return base
# ---------------------------------------------------------------------------
# Severity Color Mapping
# ---------------------------------------------------------------------------

def alert_color(severity):
    """
    Map NWS severity levels to color codes.

    Severity levels (NWS):
        Extreme, Severe, Moderate, Minor, Unknown

    Output:
        Hex color string suitable for UI use.
    """

    if not severity:
        return "#888888"   # neutral gray

    sev = severity.lower()

    match sev:
        case "extreme":
            return "#d32f2f"   # deep red
        case "severe":
            return "#f57c00"   # orange
        case "moderate":
            return "#fbc02d"   # yellow
        case "minor":
            return "#1976d2"   # blue
        case _:
            return "#888888"   # fallback gray
