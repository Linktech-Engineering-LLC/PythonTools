# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-09
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
import urllib.error


# ---------------------------------------------------------------------------
# Fetch NWS Alerts
# ---------------------------------------------------------------------------

def fetch_alerts_nws(lat, lon, timeout=10):
    """
    Fetch active NWS alerts for a given lat/lon.

    Returns raw JSON (dict) or empty list on error.
    """

    url = f"https://api.weather.gov/alerts/active?point={lat},{lon}"

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

    raw = fetch_alerts_nws(lat, lon, timeout)
    normalized = normalize_alerts(raw)
    data["alerts"] = normalized
    return data

