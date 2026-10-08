# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-30
 Modified: 2026-10-08
 File: PythonTools/system/env/modes.py
 Version: 1.1.0
 Description: Environment classification: OS family, flavor, user, dev/frozen.
"""

import sys

from PythonTools.system.env.osinfo import (
    is_linux, is_macos, is_windows,
    get_linux_flavor, get_macos_version,
    get_unix_flavor, get_windows_flavor,
    get_architecture
)
from PythonTools.system.env.userinfo import get_current_user


# ---------------------------------------------------------------------------
# Frozen / Dev mode detection
# ---------------------------------------------------------------------------

def is_frozen() -> bool:
    """Return True if running from a PyInstaller/pyoxidizer bundle."""
    return getattr(sys, "frozen", False)


def is_dev_mode() -> bool:
    """Return True if running from source (not frozen)."""
    return not is_frozen()


# ---------------------------------------------------------------------------
# OS family
# ---------------------------------------------------------------------------

def get_os_family():
    """Return 'linux', 'macos', 'windows', or 'unix'."""
    if is_linux():
        return "linux"
    if is_macos():
        return "macos"
    if is_windows():
        return "windows"
    return "unix"


# ---------------------------------------------------------------------------
# OS details
# ---------------------------------------------------------------------------

def get_os_details():
    """Return structured OS metadata: family, flavor/version, architecture."""
    if is_linux():
        return {
            "family": "linux",
            "flavor": get_linux_flavor(),
            "arch": get_architecture(),
        }

    if is_macos():
        return {
            "family": "macos",
            "version": get_macos_version(),
            "arch": get_architecture(),
        }

    if is_windows():
        return {
            "family": "windows",
            "flavor": get_windows_flavor(),
            "arch": get_architecture(),
        }

    # Generic Unix
    return {
        "family": "unix",
        "flavor": get_unix_flavor(),
        "arch": get_architecture(),
    }


# ---------------------------------------------------------------------------
# Unified environment descriptor
# ---------------------------------------------------------------------------

def get_environment():
    """
    Return a unified environment descriptor containing:
    - OS family
    - OS details
    - user identity
    - dev/frozen mode
    """
    return {
        "family": get_os_family(),
        "details": get_os_details(),
        "user": get_current_user(),
        "dev_mode": is_dev_mode(),
        "frozen": is_frozen(),
    }
