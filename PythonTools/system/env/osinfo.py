# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-10-08
 Modified: 2026-10-08
 File: PythonTools/system/env/osinfo.py
 Version: 1.0.0
 Description: Low-level system introspection: OS family, flavor, architecture.
"""

import platform
import sys


# ---------------------------------------------------------------------------
# Architecture
# ---------------------------------------------------------------------------

def get_architecture():
    """Return CPU architecture (e.g., x86_64, arm64)."""
    return platform.machine()


# ---------------------------------------------------------------------------
# Linux flavor detection
# ---------------------------------------------------------------------------

def get_linux_flavor():
    """
    Parse /etc/os-release for Linux distribution metadata.
    Returns dict or None.
    """
    try:
        data = {}
        with open("/etc/os-release") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    data[k] = v.strip('"')
        return {
            "id": data.get("ID"),
            "id_like": data.get("ID_LIKE"),
            "version": data.get("VERSION_ID"),
            "name": data.get("NAME"),
        }
    except FileNotFoundError:
        return None


# ---------------------------------------------------------------------------
# macOS version
# ---------------------------------------------------------------------------

def get_macos_version():
    """Return macOS version string (e.g., '14.1.2')."""
    return platform.mac_ver()[0]


# ---------------------------------------------------------------------------
# Unix (non-Linux) flavor detection
# ---------------------------------------------------------------------------

def get_unix_flavor():
    """
    Detect non-Linux Unix variants based on sys.platform.
    Returns string or None.
    """
    plat = sys.platform
    if plat.startswith("sunos"):
        return "sunos"
    if plat.startswith("aix"):
        return "aix"
    if plat.startswith("hp-ux"):
        return "hpux"
    if plat.startswith("freebsd"):
        return "freebsd"
    if plat.startswith("openbsd"):
        return "openbsd"
    if plat.startswith("netbsd"):
        return "netbsd"
    return None


# ---------------------------------------------------------------------------
# Windows flavor detection
# ---------------------------------------------------------------------------

def get_windows_flavor():
    """Return Windows release, version, and edition."""
    return {
        "release": platform.release(),
        "version": platform.version(),
        "edition": platform.win32_edition(),
    }


# ---------------------------------------------------------------------------
# OS family checks
# ---------------------------------------------------------------------------

def is_linux():
    return sys.platform.startswith("linux")

def is_macos():
    return sys.platform == "darwin"

def is_windows():
    return sys.platform.startswith("win")
