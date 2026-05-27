# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
 Modified: 2026-05-27
 File: PythonTools/logging/helpers.py
 Version: 1.0.1
 Description: Logging initialization helpers for RunUpdates
"""

import logging
import os
from pathlib import Path

from .factory import LoggerFactory
from ..utils.common import read_toml
class ConfigError(Exception):
    pass

def build_log_cfg(context: dict) -> dict:
    """
    Build logging configuration using merged CLI + default paths.
    """

    project_name = context["PROJECT_NAME"]

    # Base log dir: from CLI or default
    log_dir = context.get("log_dir", context["LOG_DIR"])
    log_dir = Path(os.path.expanduser(log_dir))

    log_file = log_dir / f"{project_name}.log"

    # Derive logging-specific settings from context
    max_mb = context.get("log_max_mb", 5)
    max_bytes = max_mb * 1024 * 1024

    return {
        # Logging-only flags (not CLI flags)
        "enabled": True,
        "rotate_logs": True,

        # Derived from CLI
        "path": log_file,
        "max_bytes": max_bytes,
        "max_age_days": context.get("log_max_age_days", 30),
        "console_enabled": context.get("verbose", False),
        "compress_archive": context.get("compress_archive", False),
        "delete_log": context.get("delete_log", False),

        # Custom levels
        "custom_levels": {
            "AUDIT": 25,
            "LIFECYCLE": 26,
            "TRACE": 5,
        },

        # Verbosity
        "log_level": "DEBUG" if context.get("verbose") else "INFO",
    }

def resolve_paths(anchor_file: str | Path) -> dict:
    """
    Resolve deterministic project-local paths for ANY project.
    Caller provides __file__ from its own package.

    Detects dev vs installed environment using:
      - presence of schema/ directory
      - presence of pyproject.toml
      - presence of .git/
    """

    anchor = Path(anchor_file).resolve()
    package_dir = anchor.parents[1]      # caller's package root
    install_root = package_dir

    log_dir = install_root / "var" / "log"
    config_dir = install_root / "etc"

    # ------------------------------------------------------------
    # Detect dev environment
    # ------------------------------------------------------------
    pyproject_file = package_dir / "pyproject.toml"
    dev_schema_dir = package_dir / "schema"
    git_dir = package_dir / ".git"

    is_dev = (
        dev_schema_dir.exists()
        or pyproject_file.exists()
        or git_dir.exists()
    )

    # ------------------------------------------------------------
    # Determine project name
    # ------------------------------------------------------------
    if is_dev:
        # Dev mode: use pyproject if available, else folder name
        if pyproject_file.exists():
            try:
                data = read_toml(pyproject_file)
                project_name = data.get("project", {}).get("name", package_dir.name)
            except Exception:
                project_name = package_dir.name
        else:
            project_name = package_dir.name
        environment = "dev"

        # Schema lives in repo
        schema_dir = dev_schema_dir if dev_schema_dir.exists() else package_dir

    else:
        # Installed mode: use executable name
        import sys
        project_name = Path(sys.argv[0]).name
        environment = "installed"

        if not config_dir.exists():
            raise ConfigError(f"Config directory does not exist: {config_dir}")

        schema_dir = config_dir

    summary_base = install_root / "var" / "summaries"
    summary_host_dir = summary_base / "hosts"
    summary_run_dir  = summary_base / "runs"

    # Ensure directories exist
    summary_host_dir.mkdir(parents=True, exist_ok=True)
    summary_run_dir.mkdir(parents=True, exist_ok=True)

    return {
        "ROOT": str(install_root),
        "LOG_DIR": str(log_dir),
        "CONFIG_DIR": str(config_dir),
        "SCHEMA_DIR": str(schema_dir),
        "SUMMARY_HOST_DIR": str(summary_host_dir),
        "SUMMARY_RUN_DIR": str(summary_run_dir),
        "PROJECT_NAME": project_name,
        "ENVIRONMENT": environment,
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
            "LOG_DIR": context["LOG_DIR"],
            "CONFIG_DIR": context["CONFIG_DIR"],
            "SCHEMA_DIR": context["SCHEMA_DIR"],
            "PROJECT_NAME": context["PROJECT_NAME"],
            "ENVIRONMENT": context.get("ENVIRONMENT"),
        },
    }
