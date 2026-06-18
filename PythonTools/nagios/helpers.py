# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/nagios/helpers.py
 Version: 1.0.0
 Description: Helper utilities for Nagios-compatible output.
"""


def should_output(mode: str) -> bool:
    """
    Quiet mode suppresses all stdout output.
    """
    return mode not in ("quiet",)
