# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-13
 Modified: 2026-07-13
 File: PythonTools/html/models.py
 Version: 1.0.0
 Description: html class structures
"""
BACKEND_SIGNATURES = {
    "tomcat": {
        "headers": [
            "apache-coyote",
            "tomcat",
            "coyote"
        ],
        "html": [
            "apache tomcat",
            "org.apache.catalina",
            "tomcat manager"
        ],
        "ports": [8080]  # weak heuristic
    },

    "apache": {
        "headers": ["apache"],
        "html": ["apache server at"],
        "ports": [80, 8080]
    },

    "nginx": {
        "headers": ["nginx"],
        "html": ["nginx"],
        "ports": [80]
    },

    "iis": {
        "headers": ["microsoft-iis"],
        "html": ["iis", "microsoft"],
        "ports": [80, 443]
    },

    "jetty": {
        "headers": ["jetty"],
        "html": ["powered by jetty"],
        "ports": [8080]
    },

    "express": {
        "headers": ["express"],
        "html": [],
        "ports": []
    },

    "gunicorn": {
        "headers": ["gunicorn"],
        "html": [],
        "ports": []
    }
}
# -----------------------------
# Custom Error Classes
# -----------------------------
class HttpFetchError(Exception):
    pass

