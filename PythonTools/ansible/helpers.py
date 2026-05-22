# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-22
 Modified: 2026-05-22
 File: PythonTools/ansible/helpers.py
 Version: 1.0.0
 Description: Description of this module
"""
from pathlib import Path

def resolve_path(path: str | Path) -> Path:
    """
    Expand ~, resolve relative paths, and return an absolute Path.
    """
    p = Path(path).expanduser().resolve()
    return p

def resolve_with_priority(cli_value: str | None, env_value: str | None, default: str | None = None) -> Path | None:
    """
    Generic 3‑tier resolution:
      1. CLI value
      2. Environment variable
      3. Default (optional)
    """
    if cli_value:
        return resolve_path(cli_value)

    if env_value:
        return resolve_path(env_value)

    if default:
        return resolve_path(default)

    return None
