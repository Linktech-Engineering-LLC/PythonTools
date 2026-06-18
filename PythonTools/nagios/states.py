# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/nagios/states.py
 Version: 1.0.0
 Description: Nagios exit codes and state names.
"""

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

STATE_NAMES = {
    OK: "OK",
    WARNING: "WARNING",
    CRITICAL: "CRITICAL",
    UNKNOWN: "UNKNOWN",
}
