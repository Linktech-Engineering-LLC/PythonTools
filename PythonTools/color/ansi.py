# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-03
 Modified: 2026-08-03
 File: PythonTools/color/ansi.py
 Version: 1.0.0
 Description: Module description here
"""

class Color:
    RESET = "\x1b[0m"
    RED = "\x1b[31m"
    YELLOW = "\x1b[33m"
    GREEN = "\x1b[32m"
    BLUE = "\x1b[34m"
    CYAN = "\x1b[36m"
    GRAY = "\x1b[90m"


def colorize(text: str, color: str, enabled: bool) -> str:
    if not enabled:
        return text
    return f"{color}{text}{Color.RESET}"

