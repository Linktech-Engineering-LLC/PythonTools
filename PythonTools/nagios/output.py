# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-07-13
 File: PythonTools/nagios/output.py
 Version: 1.0.0
 Description: Nagios output formatting helpers.
"""
import os
from .states import (
    STATE_NAMES,
    OK,
    WARNING,
    CRITICAL,
    UNKNOWN,
)

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

def early_exit(meta, logger, message, code):
    """
    Unified early-exit handler for all NMS_Tools.
    - Quiet mode suppresses stdout
    - Nagios mode prints Nagios summary
    - LoggerFactory handles log output if available
    """
    mode = meta.get("mode", "normal")

    # STDOUT
    if mode == "nagios":
        print(nagios_summary(code, message))
    elif mode != "quiet":
        print(message)

    # Logging
    if logger:
        logger.error(f"[ERROR] {message}")

    os._exit(code)
def ok_exit(message):
    print(f"OK - {message}")
    os._exit(OK)
def warning_exit(message):
    print(f"WARNING - {message}")
    os._exit(WARNING)
def critical_exit(message):
    print(f"CRITICAL - {message}")
    os._exit(CRITICAL)
def unknown_exit(message):
    print(f"UNKNOWN - {message}")
    os._exit(UNKNOWN)
def nagios_priority(code):
    # Higher number = higher severity
    if code == 2:  # CRITICAL
        return 4
    if code == 1:  # WARNING
        return 3
    if code == 3:  # UNKNOWN
        return 2
    if code == 0:  # OK
        return 1
    return 0
