# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/finance/api_keys.py
 Version: 1.0.0
 Description: 
            Unified API key loader for market data providers.
            Search order:
            1. Environment variable:   {TARGET.upper()}_API_KEY
            2. Config file:            ~/.nms-tools/{target.lower()}.conf
            3. Vault (future)
"""

import os
from pathlib import Path
from typing import Optional


CONFIG_DIR = Path.home() / ".nms-tools"


def _load_from_env(target: str) -> Optional[str]:
    """
    Looks for environment variable: {TARGET.upper()}_API_KEY
    """
    env_name = f"{target.upper()}_API_KEY"
    return os.environ.get(env_name)


def _load_from_conf(target: str) -> Optional[str]:
    """
    Reads ~/.nms-tools/{target}.conf in KEY=VALUE format.
    """
    filename = f"{target.lower()}.conf"
    path = Path(os.path.expanduser(CONFIG_DIR / filename))

    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    _, value = line.split("=", 1)
                    return value.strip()
    except Exception:
        return None

    return None


def _load_from_vault(target: str) -> Optional[str]:
    """
    Placeholder for future vault integration.
    """
    return None


def get_api_key(target: str) -> str:
    """
    Unified API key loader.
    Search order:
      1. Environment variable
      2. ~/.nms-tools/{target}.conf
      3. Vault (future)
    """
    # 1. Environment variable
    key = _load_from_env(target)
    if key:
        return key

    # 2. Config file
    key = _load_from_conf(target)
    if key:
        return key

    # 3. Vault (future)
    key = _load_from_vault(target)
    if key:
        return key

    raise RuntimeError(
        f"Missing API key for '{target}'. "
        f"Expected environment variable {target.upper()}_API_KEY "
        f"or ~/.nms-tools/{target.lower()}.conf"
    )
