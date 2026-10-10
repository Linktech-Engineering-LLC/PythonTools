# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-10-10
 Modified: 2026-10-10
 File: PythonTools/parsing/substitution.py
 Version: 1.0.0
 Description: Module description here
"""

import os
import re
import yaml

VAR_PATTERN = re.compile(r"\$\{([^}]+)\}")

def substitute_env(value: str) -> str:
    """
    Substitute ${VAR} with environment variable values.
    Supports ${VAR} and ${VAR:-default}.
    """
    def repl(match):
        expr = match.group(1)

        # Handle ${VAR:-default}
        if ":-" in expr:
            var, default = expr.split(":-", 1)
            return os.getenv(var, default)

        # Handle ${VAR:default}
        if ":" in expr:
            var, default = expr.split(":", 1)
            return os.getenv(var, default)

        # Handle ${VAR}
        return os.getenv(expr, "")

    return VAR_PATTERN.sub(repl, value)

def load_yaml_with_substitution(path: str):
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return _apply_substitution(data)

def _apply_substitution(obj):
    if isinstance(obj, dict):
        return {k: _apply_substitution(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_apply_substitution(v) for v in obj]
    elif isinstance(obj, str):
        return substitute_env(obj)
    else:
        return obj
