# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-09-24
Modified: 2026-09-24
 File: PythonTools/net/__init__.py
 Version: 1.0.0
 Description: Module description here
"""

from .collectors import (
    gather_local_interfaces,
    gather_snmp_interfaces,
    snmp_walk,
)
from .http import http_get_json
from .normalize import (
    normalize_counters,
    normalize_duplex,
    normalize_interfaces,
    normalize_speed,
    fmt_flags,
    fmt_speed,
    parse_speed,
    SPEED_UNITS,
)
from .tools import (
    apply_iface_selection,
    decode_mac,
    evaluate_status,
    host_exists,
    is_alias,
    is_external_ip,
    is_ip_address,
    is_valid_subnet,
    isLocalHost,
    is_local,
    is_virtual,
    local_command,
    pid_is_running,
    run_with_error_handling,
    sudo_run,
    validate_host_basic,
    validate_host_local,
    VIRTUAL_PREFIXES,
)
from .nagios import build_perfdata
from .pidguard import PidGuard
from .tcp import check_port

__all__ = [
    "PidGuard",
    "sudo_run"
]