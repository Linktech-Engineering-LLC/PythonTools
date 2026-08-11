# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-10
Modified: 2026-08-10
 File: PythonTools/weather/providers/builders.py
 Version: 1.0.0
 Description: Module description here
"""

import requests
import urllib

from ..registry import WEATHER_PROVIDERS

def build_nws_url(lat: float, lon: float, mode: str) -> str:
    base = WEATHER_PROVIDERS["nws"]["base"]

    # Step 1: resolve gridpoint metadata
    point_url = f"{base}/points/{lat},{lon}"
    point_data = requests.get(point_url, timeout=5).json()
    props = point_data["properties"]

    match mode:
        case "current" | "hourly":
            return props["forecastHourly"]

        case "weekly":
            return props["forecast"]

        case "observation":
            # Return the station list URL
            return props["observationStations"]

        case _:
            raise ValueError(f"Unsupported mode for NWS: {mode}")
def build_open_meteo_url(lat: float, lon: float, mode: str) -> str:
    base = WEATHER_PROVIDERS["open-meteo"]["base"]

    match mode:
        case "current":
            params = {
                "latitude": lat,
                "longitude": lon,
                "current_weather": "true",
                "hourly": ",".join([
                    "temperature_2m",
                    "apparent_temperature",
                    "dewpoint_2m",
                    "relativehumidity_2m",
                    "pressure_msl",
                    "visibility",
                    "precipitation",
                    "precipitation_probability",
                    "cloudcover",
                    "windspeed_10m",
                    "windgusts_10m",
                    "weathercode",
                ]),
                "daily": "sunrise,sunset",
                "timezone": "auto",
            }

        case "hourly":
            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": ",".join([
                    "temperature_2m",
                    "apparent_temperature",
                    "dewpoint_2m",
                    "relativehumidity_2m",
                    "pressure_msl",
                    "visibility",
                    "precipitation",
                    "precipitation_probability",
                    "cloudcover",
                    "windspeed_10m",
                    "windgusts_10m",
                    "weathercode",
                ]),
                "daily": ",".join(["sunrise,sunset",]),   # ⭐ FIXED
                "timezone": "auto",
            }

        case "weekly":
            params = {
                "latitude": lat,
                "longitude": lon,
                "daily": ",".join([
                    "weathercode",
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "precipitation_probability_max",
                    "windspeed_10m_max",
                    "sunrise",
                    "sunset",
                ]),
                "timezone": "auto",
            }

        case _:
            raise ValueError(f"Unsupported mode for Open-Meteo: {mode}")

    return f"{base}?{urllib.parse.urlencode(params)}"
