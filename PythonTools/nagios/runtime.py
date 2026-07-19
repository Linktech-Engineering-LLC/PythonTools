# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/nagios/runtime.py
 Version: 1.0.0
 Description: 
            Runtime information helpers for Nagios-compatible checks.
            Provides Python version, platform, and architecture details.
"""

import platform
from typing import Dict


def get_runtime_info() -> Dict[str, str]:
    """
    Returns a dictionary describing the runtime environment:
        - python_version: 3.11.3
        - python_build: ('main', 'Apr  2 2024 10:00:00')
        - implementation: CPython
        - platform: Linux-6.8.0-40-generic-x86_64-with-glibc2.39
        - system: Linux
        - release: 6.8.0-40-generic
        - machine: x86_64
        - processor: x86_64
    """
    return {
        "python_version": platform.python_version(),
        "python_build": str(platform.python_build()),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
    }


def format_runtime_info() -> str:
    """
    Returns a multi-line string suitable for --version output.
    Example:
        Python 3.11.3 (CPython)
        Linux-6.8.0-40-generic-x86_64-with-glibc2.39
    """
    info = get_runtime_info()
    return (
        f"Python {info['python_version']} ({info['implementation']})\n"
        f"{info['platform']}"
    )
