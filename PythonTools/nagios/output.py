# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/nagios/output.py
 Version: 1.0.0
 Description: Nagios output formatting helpers.
"""

from PythonTools.nagios.states import STATE_NAMES


def nagios_summary(state: int, message: str, extra: dict | None = None) -> str:
    """
    Build a Nagios-compatible summary line.
    """
    base = f"{STATE_NAMES[state]} - {message}"

    if extra:
        parts = [f"{k}={v}" for k, v in extra.items() if v is not None]
        if parts:
            base += " " + " ".join(parts)

    return base
