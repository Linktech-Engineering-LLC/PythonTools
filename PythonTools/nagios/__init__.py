# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-07-14
 File: PythonTools/nagios/__init__.py
 Version: 1.0.0
 Description: Package library for the nagios module
"""
from PythonTools import __version__

from .states import OK, WARNING, CRITICAL, UNKNOWN, STATE_NAMES
from .mode import Flags, FlagNames, detect_mode
from .output import (
    nagios_summary, 
    early_exit,
    critical_exit,
    nagios_priority,
)
from .banners import (
    start_banner, 
    end_banner, 
    cert_banner, 
    html_banner,
    result_banner,
    log_interface,
)
from .helpers import should_output
from .parser import BaseNagiosParser
from .result import build_result_object
