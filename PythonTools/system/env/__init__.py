# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-10-08
 Modified: 2026-10-08
 File: PythonTools/system/env/__init__.py
 Version: 1.0.0
 Description: Module description here
"""

from .modes import (
    is_dev_mode, is_frozen, 
    get_os_details, get_os_family, get_environment
)
from .osinfo import (
    get_architecture, get_linux_flavor,
    get_macos_version, get_unix_flavor,
    get_windows_flavor, is_linux, is_macos,
    is_windows
)
from .userinfo import get_current_user

__all__ = [
    "get_environment",
]