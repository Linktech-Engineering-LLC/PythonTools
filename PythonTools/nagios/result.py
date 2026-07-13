# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-13
 Modified: 2026-07-13
 File: PythonTools/nagios/result.py
 Version: 1.0.0
 Description: Helpers that determines Nagios results
"""

from .output import nagios_priority

def build_result_object(capture, backend_info, checks, failures):
    # Determine final Nagios status
    final_status = max(
        (checks["backend"]["status"],
         checks["status"]["status"],
         checks["content_type"]["status"],
         checks["html"]["status"]),
        key=nagios_priority
    )

    # Determine final message
    final_message = (
        checks["backend"]["message"]
        or checks["html"]["message"]
        or checks["content_type"]["message"]
        or checks["status"]["message"]
        or "OK"
    )

    return {
        "capture": capture,

        # MUST contain status + message (PythonTools banner requirement)
        "backend": {
            "detected": backend_info["detected"],
            "candidates": backend_info["candidates"],
            "confidence": backend_info["confidence"],
            "reason": backend_info["reason"],
            "status": checks["backend"]["status"],
            "message": checks["backend"]["message"],
        },

        "status_check": {
            "status": checks["status"]["status"],
            "message": checks["status"]["message"],
        },

        "content_type_check": {
            "status": checks["content_type"]["status"],
            "message": checks["content_type"]["message"],
        },

        "html_check": {
            "status": checks["html"]["status"],
            "message": checks["html"]["message"],
        },

        # Unified enforcement model (matches check_cert)
        "failures": failures,

        "overall": {
            "status": final_status,
            "message": final_message,
        }
    }
