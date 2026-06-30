#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
File: parsers.py
Author: Leon McClatchey
Company: Linktech Engineering LLC
Created: 2026-06-30
 Modified: 2026-06-30
Required: Python 3.8+

Description: 
            Unified multi-distro parsing engine for update/check/list output.
            This module merges:
            - Regex-based Parser class
            - Distro autodetection
            - Distro-specific parsing helpers
            - Unified check/list parsing logic

            This module is fully project-agnostic and reusable across:
            - RunUpdates
            - NMS_Tools
            - TimerDeck
            - Future automation tools
"""

import re
from typing import Dict, List, Any, Optional


# ======================================================================
# 1. Regex-based parsing engine (existing Parser class)
# ======================================================================

class Parser:
    """
    Generic multi-distro parsing engine.
    Used for check/update/clean summaries across all distros.
    """

    PARSING_RULES: Dict[str, Dict[str, str]] = {

        # Debian-family
        "debian.check": {
            "summary": r"(\d+)\s+packages can be upgraded",
            "up_to_date": r"All packages are up to date",
        },

        "debian.update": {
            "upgraded": r"^\s{2}(\S+)\s*$",
        },

        # RedHat-family
        "redhat.update": {
            "upgraded": r"^\s+(\S+)\.\S+\s+\S+$",
        },

        # openSUSE
        "opensuse.update": {
            "upgraded": r"^\s+(\S+)\s+\|\s+\S+\s+\|\s+\S+\s+\|\s+\S+$",
        },
    }

    @staticmethod
    def parse_output(output: str, rules: Dict[str, str]) -> Dict[str, Any]:
        result: Dict[str, List[str]] = {}
        if not output or not rules:
            return result

        for key, pattern in rules.items():
            matches = re.findall(pattern, output, re.MULTILINE)
            if matches:
                result[key] = matches

        return result

    @classmethod
    def parse(cls, distro: str, step: str, output: str) -> Optional[Dict[str, Any]]:
        key = f"{distro}.{step}"
        rules = cls.PARSING_RULES.get(key)
        if not rules:
            return None

        parsed = cls.parse_output(output, rules)
        return parsed or None


# ======================================================================
# 2. Distro autodetection
# ======================================================================

def detect_distro(lines: List[str], output: str) -> Optional[str]:
    """
    Autodetect distro based on update/check/list output.
    """

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


# ======================================================================
# 3. Distro-specific parsing helpers
# ======================================================================

def parse_opensuse(lines: List[str], output: str) -> bool:
    for line in lines:
        lower = line.lower()

        if "found" in lower and "patch" in lower:
            return True

        if re.match(r"^[vui]\s+\|", lower):
            return True

    for line in lines:
        lower = line.lower()
        if (
            "no patches found" in lower
            or "0 patches needed" in lower
            or "nothing to do" in lower
        ):
            return False

    if "Available Version" in output and "Current Version" in output:
        for line in lines:
            if "|" in line and not line.startswith(("Repository", "Name", "Arch")):
                parts = [p.strip() for p in line.split("|")]
                if len(parts) >= 4 and parts[2] != parts[3]:
                    return True

    return False


def parse_debian(lines: List[str]) -> bool:
    for line in lines:
        if line.startswith("Inst "):
            return True
        if "upgradable from" in line:
            return True
    return False


def parse_redhat(lines: List[str]) -> bool:
    for line in lines:
        lower = line.lower()
        if "updates available" in lower:
            return True

        parts = line.split()
        if len(parts) >= 3 and not line.startswith("Last metadata"):
            if any(char.isdigit() for char in parts[1]):
                return True

    return False


def parse_arch(lines: List[str]) -> bool:
    return any("->" in line for line in lines)


def parse_alpine(lines: List[str]) -> bool:
    return any("Upgrading" in line and "to" in line for line in lines)


def parse_flatpak(output: str) -> bool:
    return "Updates:" in output


def parse_snap(output: str) -> bool:
    return "will be updated" in output


def parse_fallback(lines: List[str]) -> bool:
    for line in lines:
        tokens = line.split()
        if any(token.isdigit() for token in tokens):
            lower = line.lower()
            if any(keyword in lower for keyword in ["update", "upgrade", "upgradable"]):
                return True
    return False


# ======================================================================
# 4. Unified check/list parsing API
# ======================================================================

def parse_check_output(output: str, distro: Optional[str]) -> bool:
    """
    Unified entry point used by RunUpdates and other tools.
    Determines whether updates exist based on merged check/list output.
    """

    if not output:
        return False

    lines = [line.strip() for line in output.splitlines() if line.strip()]

    # Autodetect distro if not provided
    if not distro:
        auto = detect_distro(lines, output)
        if auto:
            distro = auto

    distro = (distro or "").lower()

    match distro:
        case "opensuse":
            return parse_opensuse(lines, output)
        case "debian":
            return parse_debian(lines)
        case "redhat":
            return parse_redhat(lines)
        case "arch":
            return parse_arch(lines)
        case "alpine":
            return parse_alpine(lines)
        case "flatpak":
            return parse_flatpak(output)
        case "snap":
            return parse_snap(output)
        case _:
            return parse_fallback(lines)
