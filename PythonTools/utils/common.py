# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
Modified: 2026-04-15
 File: PythonTools/utils/common.py
 Version: 1.0.0
 Description: Description of this module
        Generic, reusable utility functions for the PythonTools package.
        This module MUST remain project‑agnostic and contain no logic
        specific to RunUpdates, TimerDeck, BotScanner, or any other project.
"""

import sys
import os
import json
import yaml
import tomllib
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# ------------------------------------------------------------
# Generic timestamp helper
# ------------------------------------------------------------

def current_timestamp() -> str:
    """Return a timezone-aware timestamp in ISO format."""
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S %Z%z")

def json_output(data, force_color=False):
    is_tty = sys.stdout.isatty()

    # Pretty JSON for TTY, compact for pipes
    if is_tty:
        text = json.dumps(data, indent=2)
    else:
        text = json.dumps(data, separators=(",", ":"))

    # Optional colorization
    if (force_color):
        try:
            from pygments import highlight
            from pygments.lexers import JsonLexer
            from pygments.formatters import TerminalFormatter
            return highlight(text, JsonLexer(), TerminalFormatter())
        except ImportError:
            return text

    return text

# ------------------------------------------------------------
# Generic size parser
# ------------------------------------------------------------

def parse_size(size_str: str) -> int:
    """
    Convert strings like '10KB', '5MB', '2GB' into integer byte counts.
    """
    size_str = size_str.upper()
    if size_str.endswith("KB"):
        return int(size_str[:-2]) * 1024
    if size_str.endswith("MB"):
        return int(size_str[:-2]) * 1024 * 1024
    if size_str.endswith("GB"):
        return int(size_str[:-2]) * 1024 * 1024 * 1024
    return int(size_str)


# ------------------------------------------------------------
# Generic TOML reader
# ------------------------------------------------------------

def read_toml(path: str | Path) -> dict:
    """Load a TOML file and return its contents as a dict."""
    with open(Path(path), "rb") as f:
        return tomllib.load(f)


# ------------------------------------------------------------
# Generic YAML / JSON loaders
# ------------------------------------------------------------

def load_yaml(path: str | Path) -> dict:
    with open(Path(path), "r") as f:
        return yaml.safe_load(f)


def load_json(path: str | Path) -> dict:
    with open(Path(path), "r") as f:
        return json.load(f)


# ------------------------------------------------------------
# Generic path resolver
# ------------------------------------------------------------

def resolve_path(path: str | Path) -> Path:
    """Expand ~ and return an absolute resolved Path."""
    return Path(path).expanduser().resolve()

def normalize_path(p: Optional[str]) -> Optional[str]:
    if not p:
        return None
    return str(Path(os.path.expandvars(os.path.expanduser(p))))


# ------------------------------------------------------------
# String <-> dictionary helpers
# ------------------------------------------------------------

def string_to_dictionary(value: str) -> dict:
    """
    Parse a config string like:
        'manager.name=firewalld,manager.timeout=1h,kernel.debug=true'
    into a nested dictionary.
    """
    if not value:
        return {}

    result = {}
    parts = []
    buf = []
    depth = 0

    # Split only on top-level commas
    for ch in value:
        if ch in "{[":
            depth += 1
            buf.append(ch)
        elif ch in "}]":
            depth -= 1
            buf.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(buf).strip())
            buf = []
        else:
            buf.append(ch)

    if buf:
        parts.append("".join(buf).strip())

    def coerce(val: str):
        if val == "None":
            return None
        if val.lower() in ("true", "false"):
            return val.lower() == "true"
        try:
            if "." in val:
                return float(val)
            return int(val)
        except ValueError:
            return val

    for part in parts:
        if "=" not in part:
            continue
        key, raw_val = part.split("=", 1)
        val = coerce(raw_val.strip())

        # Support dotted keys for nested dicts
        keys = key.strip().split(".")
        d = result
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        d[keys[-1]] = val

    return result


def dict_to_string(d: dict) -> str:
    """Convert a dictionary into a simple key=value,key2=value2 string."""
    return ",".join(f"{k}={v}" for k, v in d.items())


# ------------------------------------------------------------
# Boolean coercion
# ------------------------------------------------------------

def coerce_bool(val: str) -> bool:
    """Convert common truthy strings into a boolean."""
    return str(val).lower() in ("1", "true", "yes", "on")


def classify_exit_code(
    step: str,
    exit_code: int,
    rules: Dict[str, Any],
    host_name: str | None = None,
) -> str:
    """
    Generic exit-code classifier used by RunUpdates and SystemdRunner.
    rules = {
        "success": [...],
        "up_to_date": [...],
        "updates_available": [...],
        "error": ["*"]
    }
    """
    # Wildcard error rule
    if "error" in rules and "*" in rules["error"]:
        for category, values in rules.items():
            if category == "error":
                continue
            if exit_code in values:
                return category

        raise RuntimeError(
            f"Host '{host_name}' step '{step}' failed with exit code {exit_code}"
        )

    # Strict matching
    for category, values in rules.items():
        if exit_code in values:
            return category

    # Fallback: exit code 0 → success
    if exit_code == 0:
        return "success"

    raise RuntimeError(
        f"Host '{host_name}' step '{step}' failed with exit code {exit_code}"
    )
def normalize_list(values):
    """
    Normalize a list of strings (or comma-separated strings) into a
    clean, lowercase, deduplicated list while preserving order.
    """
    if not values:
        return []

    out = []
    for item in values:
        for part in str(item).split(","):
            name = part.strip().lower()
            if name:
                out.append(name)

    return list(dict.fromkeys(out))
