# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-13
Modified: 2026-07-13
 File: PythonTools/http/backend.py
 Version: 1.0.0
 Description: HTTP backend detection helpers
"""

from .models import BACKEND_SIGNATURES
from .parse import extract_port

def detect_backend(capture):
    # If TLS failed, backend detection is impossible
    if capture.get("tls_error"):
        return {
            "detected": None,
            "candidates": [],
            "confidence": "none",
            "reason": "TLS handshake failed"
        }
    headers = capture["headers"]      # already normalized
    html = capture["body"]
    port = extract_port(capture["final_url"])

    html_lower = html.lower() if html else ""

    candidates = []
    reasons = []

    # ------------------------------------------------------------
    # Header-based detection (strongest)
    # ------------------------------------------------------------
    for backend, sigs in BACKEND_SIGNATURES.items():
        for hsig in sigs["headers"]:
            for header_name, header_value in headers.items():
                if isinstance(header_value, str) and hsig in header_value.lower():
                    candidates.append(backend)
                    reasons.append(f"Header '{header_name}' contains '{hsig}'")

    # ------------------------------------------------------------
    # HTML-based detection (medium)
    # ------------------------------------------------------------
    for backend, sigs in BACKEND_SIGNATURES.items():
        for hsig in sigs["html"]:
            if hsig in html_lower:
                candidates.append(backend)
                reasons.append(f"HTML contains '{hsig}'")

    # ------------------------------------------------------------
    # Port heuristics (weak)
    # ------------------------------------------------------------
    for backend, sigs in BACKEND_SIGNATURES.items():
        if port in sigs["ports"]:
            candidates.append(backend)
            reasons.append(f"Port {port} commonly used by {backend}")

    # Deduplicate
    candidates = list(dict.fromkeys(candidates))

    # Confidence logic unchanged...

    # ------------------------------------------------------------
    # Determine confidence
    # ------------------------------------------------------------
    if not candidates:
        return {
            "detected": None,
            "candidates": [],
            "confidence": "low",
            "reason": "No backend signatures detected"
        }

    # Strongest signal: header match
    for backend in candidates:
        for hsig in BACKEND_SIGNATURES[backend]["headers"]:
            for header_value in headers.values():
                if isinstance(header_value, str) and hsig in header_value.lower():
                    return {
                        "detected": backend,
                        "candidates": candidates,
                        "confidence": "high",
                        "reason": f"Header contains '{hsig}'"
                    }

    # Medium signal: HTML match
    for backend in candidates:
        for hsig in BACKEND_SIGNATURES[backend]["html"]:
            if hsig in html_lower:
                return {
                    "detected": backend,
                    "candidates": candidates,
                    "confidence": "medium",
                    "reason": f"HTML contains '{hsig}'"
                }

    # Weak signal: port only
    return {
        "detected": candidates[0],
        "candidates": candidates,
        "confidence": "low",
        "reason": f"Only port-based heuristic matched ({port})"
    }

