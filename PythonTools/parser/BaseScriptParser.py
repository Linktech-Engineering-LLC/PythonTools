# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-25
 Modified: 2026-05-27
 File: PythonTools/parser/BaseScriptParser.py
 Version: 1.0.0
 Description: Description of this module
"""



import argparse
import sys
from PythonTools.parser.formatters import CustomFormatter
from PythonTools.parser.errors import CheckArgumentParser, CheckArgError


class BaseScriptParser:
    """
    Universal base parser for all CLI-driven tools.
    Provides:
      - core switches
      - logging switches
      - vault switches
      - shared validation hook
    """

    def __init__(self, prog, description, version_string, default_log_dir=None, default_config_dir=None):
        self.parser = CheckArgumentParser(
            prog=prog,
            description=description,
            formatter_class=CustomFormatter,
            add_help=True,
        )

        self.version_string = version_string
        self.default_log_dir = default_log_dir
        self.default_config_dir = default_config_dir

        self._add_core_args()
        self._add_logging_args()
        self._add_vault_args()
        self._add_cfg_args()

    # --------------------------------------------------------
    # Core Options
    # --------------------------------------------------------
    def _add_core_args(self):
        core = self.parser.add_argument_group("Core Options")

        core.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose output"
        )

        core.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            help="Simulate actions without applying changes"
        )

        core.add_argument(
            "-V", "--version",
            action="version",
            version=self.version_string
        )

    # --------------------------------------------------------
    # Logging Options
    # --------------------------------------------------------
    def _add_logging_args(self):
        log = self.parser.add_argument_group("Logging Options")

        log.add_argument(
            "--log-dir",
            dest="log_dir",
            default=self.default_log_dir,
            help="Folder containing the log file"
        )

        log.add_argument(
            "--log-max-mb",
            dest="log_max_mb",
            type=int,
            default=5,
            help="Maximum size of logs in MB before rotation"
        )

        log.add_argument(
            "--compress-archive",
            dest="compress_archive",
            action="store_false",
            help="Compress rotated log"
        )

        log.add_argument(
            "--delete-log",
            dest="delete_log",
            action="store_false",
            help="Remove rotated log"
        )

        log.add_argument(
            "--archive-mode",
            choices=["tgz", "zip"],
            default="zip",
            help="Archive format for rotated logs"
        )

        log.add_argument(
            "--backup-count",
            type=int,
            default=7,
            help="Number of rotated archives to keep"
        )

    # --------------------------------------------------------
    # Config Options
    # --------------------------------------------------------
    def _add_cfg_args(self):
        cfg = self.parser.add_argument_group("Config Options")
    
        cfg.add_argument(
            "--config-dir",
            default=self.default_config_dir,
            help="Override config directory",
        )        
    
    # --------------------------------------------------------
    # Vault Options
    # --------------------------------------------------------
    def _add_vault_args(self):
        vault = self.parser.add_argument_group("Vault Options")

        vault.add_argument(
            "--vault-path",
            dest="vault_path",
            required=False,
            help="Path to vault file containing credentials"
        )

        vault.add_argument(
            "--vault-password-file",
            dest="vault_password_file",
            required=False,
            help="Path to file containing vault password"
        )

    # --------------------------------------------------------
    # Parse + Validate
    # --------------------------------------------------------
    def parse(self):
        self.args = self.parser.parse_args()
        return self.args

    # --------------------------------------------------------
    # Validation Hook
    # --------------------------------------------------------
    def _validate(self):
        """
        Base validation hook.
        Child classes extend this.
        """
        pass
