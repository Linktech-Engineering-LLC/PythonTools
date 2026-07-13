# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-13
 Modified: 2026-07-13
 File: PythonTools/http/enforce.py
 Version: 1.0.0
 Description: HTTP Enforcement helpers
"""

from ..nagios.states import (
    CRITICAL,
    OK,
    WARNING,
    UNKNOWN,
)

def enforce_status_rules(capture):
    """
    Enforce HTTP status code rules.
    Returns (status_code, message) in Nagios format.
    """

    code = capture.get("status")

    # If no HTTP status exists (TLS failure, connection failure, etc.)
    if code is None:
        return (CRITICAL, "No HTTP status (TLS or connection failure)")

    # 1. Explicit OK range (200–299)
    if 200 <= code <= 299:
        return (OK, None)

    # 2. Redirects (300–399)
    if 300 <= code <= 399:
        return (WARNING, f"Redirect ({code})")

    # 3. Client errors (400–499)
    if 400 <= code <= 499:
        return (CRITICAL, f"Client error ({code})")

    # 4. Server errors (500–599)
    if 500 <= code <= 599:
        return (CRITICAL, f"Server error ({code})")

    # 5. Anything else is UNKNOWN
    return (UNKNOWN, f"Unexpected HTTP status ({code})")
def enforce_content_type_rules(capture):
    if capture.get("tls_error"):
        return (3, "No Content-Type (TLS failure)")
    """
    Enforce Content-Type rules.
    Currently minimal: only checks that Content-Type exists.
    Returns (status_code, message) in Nagios format.
    """

    headers = capture.get("headers", {})
    ctype = headers.get("content-type")

    # No Content-Type header at all → UNKNOWN
    if not ctype:
        return (UNKNOWN, "Missing Content-Type header")

    # Otherwise OK
    return (OK, None)
def enforce_html_rules(capture):
    # TLS failure means no HTML is possible
    if capture.get("tls_error"):
        return (3, "No HTML body (TLS failure)")
    """
    Enforce HTML content rules.
    Currently minimal: only checks that HTML body exists.
    Returns (status_code, message) in Nagios format.
    """

    body = capture.get("body")

    # If body is None → UNKNOWN (unexpected)
    if body is None:
        return (UNKNOWN, "Missing HTML body")

    # If body is empty → WARNING (page exists but has no content)
    if body.strip() == "":
        return (WARNING, "Empty HTML body")

    # Otherwise OK
    return (OK, None)

