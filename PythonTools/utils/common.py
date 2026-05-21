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

import json
import yaml
import tomllib
from pathlib import Path
from datetime import datetime


# ------------------------------------------------------------
# Generic timestamp helper
# ------------------------------------------------------------

def current_timestamp() -> str:
    """Return a timezone-aware timestamp in ISO format."""
    return datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M:%S %Z%z")


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
