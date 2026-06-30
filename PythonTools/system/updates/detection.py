#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
File: detection.py
Author: Leon McClatchey
Company: Linktech Engineering LLC
Created: 2026-06-30
 Modified: 2026-06-30
Required: Python 3.8+

Description: Description of this module

"""

def detect_installs(stdout: str) -> int:
    """
    Detects whether updates were applied by scanning stdout.
    Works even when SUSE returns exit code 1 with empty stderr.
    """

    if not stdout:
        return 0

    install_markers = [
        "Installing:",
        "installing",
        "downloading",
        "Retrieving",
        "Preparing",
        "Updating",
        "Upgrade",
        "Upgrading"
    ]

    count = 0
    for line in stdout.splitlines():
        if any(marker in line for marker in install_markers):
            count += 1

    return count

def detect_update_outcome(exit_code: int, stdout: str, stderr: str):
    """
    Unified cross-distro update detection for RunUpdates.
    Handles SUSE's tri-state exit model and Ubuntu/Debian/RHEL's normal model.
    """

    # Normalize empty strings
    stdout = stdout or ""
    stderr = stderr or ""

    # --- CASE 1: Perfect success -------------------------------------------
    if exit_code == 0:
        return {
            "status": "success",
            "updates_applied": detect_installs(stdout),
            "severity": "clean"
        }

    # --- CASE 2: SUSE-style solver warning --------------------------------
    if exit_code == 1:
        # Hard failures ALWAYS produce stderr on SUSE.
        # So if stderr is empty, this is NOT a failure.
        if stderr.strip() == "":
            return {
                "status": "success_with_warnings",
                "updates_applied": detect_installs(stdout),
                "severity": "warning"
            }
        else:
            # stderr present → solver warning with details
            return {
                "status": "warning_with_details",
                "updates_applied": detect_installs(stdout),
                "severity": "warning"
            }

    # --- CASE 3: Hard failure (exit_code > 1) ------------------------------
    # All distros: hard failures ALWAYS produce stderr.
    return {
        "status": "failed",
        "updates_applied": 0,
        "severity": "error",
        "error": stderr.strip()
    }

