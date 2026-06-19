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

class ApiKeyError(Exception):
    pass
def resolve_api_key(provider: str,
                    cli_keys: dict,
                    vault: Optional[dict],
                    config: Optional[dict]) -> Optional[str]:

    # 1. Vault (optional)
    if vault:
        try:
            node = vault.get(provider, {})
            key = node.get("apikey")
            if isinstance(key, str) and key.strip():
                return key.strip()
        except Exception:
            pass

    # 2. Config file (optional)
    if config:
        try:
            node = config.get("apikeys", {})
            key = node.get(provider, {})
            if isinstance(key, str) and key.strip():
                return key.strip()
        except Exception:
            pass

    # 3. CLI override
    if provider in cli_keys and cli_keys[provider]:
        return cli_keys[provider]

    # 4. Environment variable
    env_name = f"CT_{provider.upper()}_APIKEY"
    key = os.getenv(env_name)
    if key:
        return key

    # 5. Fail cleanly
    return None
def resolve_apikey_file(apikey_file: Optional[str], script_name: str) -> Optional[str]:
    if not apikey_file:
        return None

    # Normalize input path
    path = Path(os.path.expandvars(os.path.expanduser(apikey_file))).resolve()

    # Compute script base name (no ext, lowercase)
    script_base = Path(script_name).stem.lower()

    # If it's a directory → append script_base.yml
    if path.is_dir():
        return str(path / f"{script_base}.yml")

    # If it's a file → use it directly
    return str(path)
