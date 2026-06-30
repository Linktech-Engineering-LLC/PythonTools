#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
File: repo_health.py
Author: Leon McClatchey
Company: Linktech Engineering LLC
Created: 2026-06-30
 Modified: 2026-06-30
Required: Python 3.8+

Description: Description of this module

"""
def detect_repo_health(stderr: str) -> bool:
    patterns = (
        "Failed to download metadata",
        "Cannot download repomd.xml",
        "All mirrors were tried",
        "Status code: 404",
        "repodata/repomd.xml",
        "No such file or directory: repodata",
        "Error: repomd.xml",
        "Cannot prepare internal mirrorlist",
        "No URLs in mirrorlist",
        "There are no enabled repositories",
    )
    lowered = stderr.lower()
    return any(p.lower() in lowered for p in patterns)

