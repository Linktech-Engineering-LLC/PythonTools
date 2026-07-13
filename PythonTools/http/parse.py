# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-13
 Modified: 2026-07-13
 File: PythonTools/http/parse.py
 Version: 1.0.0
 Description: HTTP Parsing helpers
"""
from typing import Optional
from urllib.parse import urlparse

from .models import HttpFetchError

def extract_port(final_url: str) -> int:
    parsed = urlparse(final_url)

    # If the URL explicitly contains a port, use it
    if parsed.port is not None:
        return parsed.port

    # Otherwise infer from scheme
    return 443 if parsed.scheme == "https" else 80

def parse_url_or_fail(url: str, original_url: Optional[str]):
    """
    Parses a URL and returns a validated, deterministic structure.

    Returns:
        {
            "host": str,
            "path": str,
            "protocol": str,
            "port": int
        }

    Raises:
        HttpFetchError if hostname is missing or URL is malformed.
    """

    parsed = urlparse(url)

    raw_host = parsed.hostname
    if raw_host is None:
        bad = original_url or url
        raise HttpFetchError(f"Invalid URL: missing hostname in '{bad}'")

    host: str = raw_host
    protocol = parsed.scheme or "http"
    path = parsed.path or "/"
    port = parsed.port or (443 if protocol == "https" else 80)

    return {
        "host": host,
        "path": path,
        "protocol": protocol,
        "port": port
    }

