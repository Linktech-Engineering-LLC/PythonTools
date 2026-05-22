# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
 Modified: 2026-05-22
 File: PythonTools/logging/helpers.py
 Version: 1.0.1
 Description: Logging initialization helpers for RunUpdates
"""

import logging
import os
from pathlib import Path

from .factory import LoggerFactory
class ConfigError(Exception):
    pass

def build_log_cfg(paths: dict, run_cfg: dict) -> dict:
    project_name = paths["PROJECT_NAME"]

    # Base log dir: from CLI or default
    log_dir = run_cfg.get("log_dir", paths["LOG_DIR"])

    log_file = Path(log_dir) / f"{project_name}.log"

    # Derive logging-specific settings from run_cfg
    max_mb = run_cfg.get("log_max_mb", 50)
    max_bytes = max_mb * 1_000_000

    return {
        # Logging-only flags (not CLI flags)
        "enabled": True,
        "rotate_logs": True,

        # Derived from CLI
        "path": log_file,
        "max_bytes": max_bytes,
        "max_age_days": run_cfg.get("log_max_age_days", 30),
        "console_enabled": not run_cfg.get("no_console", False),
        "compress_archive": run_cfg.get("compress_archive", False),
        "delete_log": run_cfg.get("delete_log", False),

        # Custom levels
        "custom_levels": {
            "AUDIT": 25,
            "LIFECYCLE": 26,
            "TRACE": 5,
        },

        # Verbosity
        "log_level": "DEBUG" if run_cfg.get("verbose") else "INFO",
    }

def resolve_paths(anchor_file: str | Path) -> dict:
    """
    Resolve deterministic project-local paths for ANY project.
    Caller provides __file__ from its own package.
    """
    anchor = Path(anchor_file).resolve()
    package_dir = anchor.parents[1]      # caller's package root
    install_root = package_dir
    project_name = package_dir.name

    log_dir = install_root / "var" / "log"
    config_dir = install_root / "etc"
    if not config_dir.exists():
        raise ConfigError(f"Config directory does not exist: {config_dir}")
    
    return {
        "ROOT": str(install_root),
        "LOG_DIR": str(log_dir),
        "CONFIG_DIR": str(config_dir),
        "PROJECT_NAME": project_name,
    }


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

def initialize_universal_logging(paths: dict, run_cfg: dict | None = None) -> dict:
    """
    Universal logging initializer using PythonTools helpers.
    Project-agnostic. No RunUpdates dependencies.
    """
    run_cfg = run_cfg or {}

    # Build logging configuration
    log_cfg = build_log_cfg(paths, run_cfg)

    # Create logger factory
    logger_factory = init_logger(log_cfg, paths["PROJECT_NAME"])

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
        "paths": paths,
    }
