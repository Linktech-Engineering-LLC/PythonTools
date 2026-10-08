# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-10-08
 Modified: 2026-10-08
 File: PythonTools/system/env/schema.py
 Version: 1.0.0
 Description: Canonical schema for the environment descriptor returned by
              PythonTools.system.env.get_environment().
"""

ENVIRONMENT_SCHEMA_VERSION = "1.0.0"

ENVIRONMENT_SCHEMA = {
    "family": "string: linux | macos | windows | unix",
    "details": {
        "family": "string",
        "flavor": "dict | None (linux/windows/unix only)",
        "version": "string | None (macOS only)",
        "arch": "string (x86_64, arm64, etc.)",
    },
    "user": {
        "login": "string",
        "uid": "int",
        "gid": "int",
        "home": "string (absolute path)",
        "shell": "string (absolute path)",
        "name": "string (full name, normalized GECOS)",
    },
    "dev_mode": "bool",
    "frozen": "bool",
}
