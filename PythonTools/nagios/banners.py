# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/nagios/banners.py
 Version: 1.0.0
 Description: Standardized start/end banners for logging.
"""


def start_banner(name: str, meta: dict) -> str:
    return f"[START] check={name} meta={meta}"


def end_banner(name: str, state: str) -> str:
    return f"[END] check={name} state={state}"
