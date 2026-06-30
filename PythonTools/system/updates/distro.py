#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
File: distro.py
Author: Leon McClatchey
Company: Linktech Engineering LLC
Created: 2026-06-30
 Modified: 2026-06-30
Required: Python 3.8+

Description: Description of this module

"""
import re

def detect_distro(lines, output):
    # openSUSE
    for line in lines:
        lower = line.lower()
        if re.match(r"^[vui]\s+\|", lower):
            return "opensuse"
        if "found" in lower and "patch" in lower:
            return "opensuse"
        if "0 patches needed" in lower or "no patches found" in lower:
            return "opensuse"
    if "Available Version" in output and "Current Version" in output:
        return "opensuse"

    # Debian/Ubuntu
    for line in lines:
        if line.startswith("Inst ") or "upgradable from" in line:
            return "debian"

    # RedHat/Fedora
    for line in lines:
        lower = line.lower()
        if "updates available" in lower:
            return "redhat"
        parts = line.split()
        if len(parts) >= 3 and any(char.isdigit() for char in parts[1]):
            return "redhat"

    # Arch
    for line in lines:
        if "->" in line:
            return "arch"

    # Alpine
    for line in lines:
        if "Upgrading" in line and "to" in line:
            return "alpine"

    # Flatpak
    if "Updates:" in output:
        return "flatpak"

    # Snap
    if "will be updated" in output:
        return "snap"

    return None

