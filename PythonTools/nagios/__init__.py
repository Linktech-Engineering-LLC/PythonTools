# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-07-16
 File: PythonTools/nagios/__init__.py
 Version: 1.0.0
 Description: Package library for the nagios module
"""
from PythonTools import __version__

from .states import (
    STATE_NAMES, 
    OK,
    WARNING,
    CRITICAL,
    UNKNOWN,
)
from .mode import (
    Flags,
    FlagNames,
    MODE_MAP,
)
from .output import (
    early_exit,
    ok_exit,
    unknown_exit,
    warning_exit,
    critical_exit,
    nagios_priority,
    nagios_summary,
)
from .banners import (
    SAFE_START_KEYS,
    start_banner,
    end_banner,
    cert_banner,
    html_banner,
    result_banner,
    _fmt,
    log_interface,
)
from .helpers import should_output
from .parser import BaseNagiosParser, CheckArgError
from .result import build_result_object
from .runtime import (
    get_runtime_info,
    format_runtime_info,
)
