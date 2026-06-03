# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
 Modified: 2026-05-31
 File: PythonTools/logging/helpers.py
 Version: 1.0.1
 Description: Logging initialization helpers for RunUpdates
"""

import logging
import os
from pathlib import Path
from dataclasses import dataclass

from PythonTools.log_helpers.factory import LoggerFactory
from PythonTools.utils.common import read_toml
class ConfigError(Exception):
    pass
class InventoryError(Exception):
    pass

def build_log_cfg(context: dict) -> dict:
    """
    Build logging configuration using merged CLI + default paths.
    """

    project_name = context["PROJECT_NAME"]
    # Base log dir: from CLI or default
    log_dir = context["paths"].LOG_DIR
    project_name = context["PROJECT_NAME"]
    
    log_dir = Path(os.path.expanduser(log_dir))
    log_file = log_dir / f"{project_name}.log"
    args = context["args"]
    # Derive logging-specific settings from context
    max_mb = getattr(args, "log_max_mb", 5)
    max_bytes = max_mb * 1024 * 1024

    return {
        # Logging-only flags (not CLI flags)
        "enabled": True,
        "rotate_logs": True,

        # Derived from CLI
        "path": log_file,
        "max_bytes": max_bytes,
        "max_age_days": getattr(args, "log_max_age_days", 30),
        "console_enabled": getattr(args, "verbose", False),
        "compress_archive": getattr(args,"compress_archive", False),
        "delete_log": getattr(args, "delete_log", False),

        # Custom levels
        "custom_levels": {
            "AUDIT": 25,
            "LIFECYCLE": 26,
            "TRACE": 5,
        },

        # Verbosity
        "log_level": "DEBUG" if getattr(args, "verbose", False) else "INFO",
    }

@dataclass
class Paths:
    BASE_DIR: Path
    LOG_DIR: Path
    SUMMARY_RUN_DIR: Path
    SUMMARY_HOST_DIR: Path

def resolve_paths(module_file: str) -> Paths:
    base = Path(module_file).resolve().parent

    return Paths(
        BASE_DIR=base,
        LOG_DIR=base / "var" / "log",
        SUMMARY_RUN_DIR=base / "var" / "log" / "summaries" / "runs",
        SUMMARY_HOST_DIR=base / "var" / "log" / "summaries" / "hosts",
    )

def init_logger(log_cfg: dict, project_name: str):
    """
    Initialize logging using caller-provided configuration.
    PythonTools should NOT determine paths or project names.
    """
    return LoggerFactory(
        log_cfg=log_cfg,
        project_name=project_name
    )

def register_custom_levels(log_cfg: dict):
    """
    Register custom logging levels and attach helper methods to logging.Logger.

    Expected format:
        log_cfg["custom_levels"] = {
            "AUDIT": 25,
            "LIFECYCLE": 26,
            "TRACE": 5,
        }
    """

    custom_levels = log_cfg.get("custom_levels", {})
    if not custom_levels:
        return

    # Factory for creating bound logger methods
    def make_log_method(level_value: int, method_name: str):
        def log_method(self, message, *args, **kwargs):
            if self.isEnabledFor(level_value):
                self._log(level_value, message, args, **kwargs)
        log_method.__name__ = method_name.lower()
        return log_method

    for name, value in custom_levels.items():
        upper = name.upper()

        # Register level name with Python logging
        logging.addLevelName(value, upper)

        # Expose constant: logging.AUDIT = 25
        setattr(logging, upper, value)

        # Attach logger.audit(), logger.lifecycle(), etc.
        method = make_log_method(value, upper)
        setattr(logging.Logger, upper.lower(), method)

def initialize_universal_logging(context: dict) -> dict:
    """
    Universal logging initializer using PythonTools helpers.
    Project-agnostic. No RunUpdates dependencies.
    """

    # Build logging configuration from merged context
    log_cfg = build_log_cfg(context)

    # Create logger factory
    logger_factory = init_logger(log_cfg, context["PROJECT_NAME"])

    # Register custom levels (AUDIT, LIFECYCLE, TRACE)
    register_custom_levels(log_cfg)

    # Create a logger for this script
    logger = logger_factory.get_logger("universal")

    # Optional: lightweight startup messages
    logger.lifecycle("UNIVERSAL_LOGGER_INIT", "Logger initialized successfully")

    return {
        "factory": logger_factory,
        "logger": logger,
        "config": log_cfg,
        "paths": {
            "LOG_DIR": context["paths"].LOG_DIR,
            "PROJECT_NAME": context["PROJECT_NAME"],
            "ENVIRONMENT": context.get("ENVIRONMENT"),
        },
    }
