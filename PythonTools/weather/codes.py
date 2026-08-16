# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-09
 Modified: 2026-08-16
 File: PythonTools/weather/codes.py
 Version: 1.0.0
 Description: Weather Code Mapping utilities
"""

from typing import Any

WEATHER_CODES = {
    0: {
        "canonical": "Clear sky",
        "contexts": [
            "Clear sky", "Clear", "Sunny", "Mostly Sunny"
        ],
        "day_icon": "wi-day-sunny.svg",
        "night_icon": "wi-night-clear.svg",
    },

    1: {
        "canonical": "Mainly clear",
        "contexts": [
            "Mainly clear", "Mostly Clear"
        ],
        "day_icon": "wi-day-sunny.svg",
        "night_icon": "wi-night-clear.svg",
    },

    2: {
        "canonical": "Partly cloudy",
        "contexts": [
            "Partly Cloudy", "Partly Sunny"
        ],
        "day_icon": "wi-day-cloudy.svg",
        "night_icon": "wi-night-alt-partly-cloudy.svg",
    },

    3: {
        "canonical": "Overcast",
        "contexts": [
            "Overcast",
            "Cloudy",
            "Mostly Cloudy",
            "Cloudy and breezy",
            "Cloudy and windy",
            "Increasing clouds",
            "Decreasing clouds",
            "Cloudy then clearing",
            "Cloudy then becoming partly cloudy",
        ],
        "day_icon": "wi-cloudy.svg",
        "night_icon": "wi-night-cloudy.svg",
    },

    45: {
        "canonical": "Fog",
        "contexts": [
            "Fog", "Patchy Fog", "Depositing rime fog"
        ],
        "day_icon": "wi-day-fog.svg",
        "night_icon": "wi-night-fog.svg",
    },

    48: {
        "canonical": "Depositing rime fog",
        "contexts": [
            "Depositing rime fog"
        ],
        "day_icon": "wi-day-fog.svg",
        "night_icon": "wi-night-fog.svg",
    },

    51: {
        "canonical": "Light drizzle",
        "contexts": [
            "Light drizzle"
        ],
        "day_icon": "wi-day-sprinkle.svg",
        "night_icon": "wi-night-alt-sprinkle.svg",
    },

    53: {
        "canonical": "Moderate drizzle",
        "contexts": [
            "Moderate drizzle"
        ],
        "day_icon": "wi-day-sprinkle.svg",
        "night_icon": "wi-night-alt-sprinkle.svg",
    },

    55: {
        "canonical": "Dense drizzle",
        "contexts": [
            "Dense drizzle"
        ],
        "day_icon": "wi-day-rain-mix.svg",
        "night_icon": "wi-night-alt-rain-mix.svg",
    },

    56: {
        "canonical": "Freezing drizzle",
        "contexts": [
            "Freezing drizzle"
        ],
        "day_icon": "wi-day-sleet.svg",
        "night_icon": "wi-night-alt-sleet.svg",
    },

    57: {
        "canonical": "Dense freezing drizzle",
        "contexts": [
            "Freezing drizzle (dense)"
        ],
        "day_icon": "wi-day-sleet.svg",
        "night_icon": "wi-night-alt-sleet.svg",
    },

    61: {
        "canonical": "Slight rain",
        "contexts": [
            "Slight rain", "Rain", "Rain Showers", "Showers"
        ],
        "day_icon": "wi-day-rain.svg",
        "night_icon": "wi-night-alt-rain.svg",
    },

    63: {
        "canonical": "Moderate rain",
        "contexts": [
            "Moderate rain"
        ],
        "day_icon": "wi-day-rain.svg",
        "night_icon": "wi-night-alt-rain.svg",
    },

    65: {
        "canonical": "Heavy rain",
        "contexts": [
            "Heavy rain"
        ],
        "day_icon": "wi-day-rain-wind.svg",
        "night_icon": "wi-night-alt-rain-wind.svg",
    },

    66: {
        "canonical": "Freezing rain",
        "contexts": [
            "Freezing rain"
        ],
        "day_icon": "wi-day-sleet.svg",
        "night_icon": "wi-night-alt-sleet.svg",
    },

    67: {
        "canonical": "Heavy freezing rain",
        "contexts": [
            "Freezing rain (heavy)"
        ],
        "day_icon": "wi-day-sleet-storm.svg",
        "night_icon": "wi-night-alt-sleet-storm.svg",
    },

    71: {
        "canonical": "Slight snow",
        "contexts": [
            "Slight snow", "Snow", "Snow grains"
        ],
        "day_icon": "wi-day-snow.svg",
        "night_icon": "wi-night-alt-snow.svg",
    },

    73: {
        "canonical": "Moderate snow",
        "contexts": [
            "Moderate snow"
        ],
        "day_icon": "wi-day-snow.svg",
        "night_icon": "wi-night-alt-snow.svg",
    },

    75: {
        "canonical": "Heavy snow",
        "contexts": [
            "Heavy snow"
        ],
        "day_icon": "wi-day-snow-wind.svg",
        "night_icon": "wi-night-alt-snow-wind.svg",
    },

    80: {
        "canonical": "Rain showers",
        "contexts": [
            "Rain showers", "Showers"
        ],
        "day_icon": "wi-day-showers.svg",
        "night_icon": "wi-night-alt-showers.svg",
    },

    81: {
        "canonical": "Moderate rain showers",
        "contexts": [
            "Rain showers (moderate)"
        ],
        "day_icon": "wi-day-showers.svg",
        "night_icon": "wi-night-alt-showers.svg",
    },

    82: {
        "canonical": "Violent rain showers",
        "contexts": [
            "Rain showers (violent)"
        ],
        "day_icon": "wi-day-storm-showers.svg",
        "night_icon": "wi-night-alt-storm-showers.svg",
    },

    85: {
        "canonical": "Slight snow showers",
        "contexts": [
            "Snow showers"
        ],
        "day_icon": "wi-day-snow.svg",
        "night_icon": "wi-night-alt-snow.svg",
    },

    86: {
        "canonical": "Heavy snow showers",
        "contexts": [
            "Snow showers (heavy)"
        ],
        "day_icon": "wi-day-snow-wind.svg",
        "night_icon": "wi-night-alt-snow-wind.svg",
    },

    95: {
        "canonical": "Thunderstorm",
        "contexts": [
            "Thunderstorm", "Thunderstorms", 
        ],
        "day_icon": "wi-day-thunderstorm.svg",
        "night_icon": "wi-night-alt-thunderstorm.svg",
    },

    96: {
        "canonical": "Thunderstorm with hail",
        "contexts": [
            "Thunderstorm with hail"
        ],
        "day_icon": "wi-day-hail.svg",
        "night_icon": "wi-night-alt-hail.svg",
    },

    99: {
        "canonical": "Thunderstorm with heavy hail",
        "contexts": [
            "Thunderstorm with heavy hail"
        ],
        "day_icon": "wi-day-hail.svg",
        "night_icon": "wi-night-alt-hail.svg",
    },
}
VALID_WMO_CODES = set(WEATHER_CODES.keys())
def validate_weather_code(code: Any) -> bool:
    """Return True if code is a valid WMO weather code."""
    return isinstance(code, int) and code in VALID_WMO_CODES
def nws_text_to_wmo(text: str | None) -> int | None:
    if not text:
        return None

    norm = normalize_nws_text(text)  # e.g., "Slight Chance Showers And Thunderstorms"

    best_code = None

    for code, info in WEATHER_CODES.items():
        for ctx in info["contexts"]:
            # substring match, case-insensitive
            if ctx.lower() in norm.lower():
                # choose the highest-impact code
                if best_code is None or code > best_code:
                    best_code = code

    return best_code
def normalize_nws_text(text: str | None) -> str:
    if not text:
        return ""

    # Lowercase
    t = text.lower()

    # Remove punctuation
    for ch in ",.;:-":
        t = t.replace(ch, "")

    # Collapse multiple spaces
    t = " ".join(t.split())

    # Title-case to match WEATHER_CODES contexts
    return t.title()
def map_context(code: int | None) -> str:
    """Return human-readable context for a WMO weather code."""
    if code is None or code not in WEATHER_CODES:
        return "Unknown"
    return WEATHER_CODES[code]["canonical"]
def map_icon(code: int | None, is_day: bool) -> str:
    """Return the correct icon filename for a WMO weather code."""
    if code is None or code not in WEATHER_CODES:
        return "wi-na.svg"
    key = "day_icon" if is_day else "night_icon"
    return WEATHER_CODES[code][key]
