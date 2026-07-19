# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/nagios/parser.py
 Version: 1.0.0
 Description: Base parser for Nagios-compatible NMS_Tools checks.
"""

import argparse
import platform
import sys
from typing import Optional

from PythonTools.nagios.mode import Flags, FlagNames, detect_mode
from PythonTools.nagios.states import UNKNOWN
from PythonTools.nagios.runtime import format_runtime_info
# -----------------------------------------------------------
# Handle Arugment Errors
# -----------------------------------------------------------
class CheckArgError():
    pass
# ------------------------------------------------------------
# Custom Formatter (same behavior as check_ports)
# ------------------------------------------------------------
class CustomFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter
):
    """
    Combines default formatting with raw description support.
    """

    def _get_help_string(self, action):
        help_text = action.help or ""
        if "%(default)" in help_text:
            return help_text
        if action.default in (None, False):
            return help_text
        return f"{help_text} (default: {action.default})"
# ------------------------------------------------------------
# Error-handling ArgumentParser
# ------------------------------------------------------------
class CheckArgumentParser(argparse.ArgumentParser):
    """
    Nagios-safe error handler:
    - prints error
    - prints help
    - exits with UNKNOWN
    """

    def error(self, message):
        print(f"ERROR: {message}\n")
        self.print_help()
        sys.exit(UNKNOWN)


# ------------------------------------------------------------
# Base Parser for all NMS_Tools checks
# ------------------------------------------------------------
class BaseNagiosParser:
    """
    Provides:
    - shared output flags (verbose/json/quiet)
    - shared logging flags (--log-dir, --log-max-mb)
    - shared version flag
    - consistent help formatting
    - consistent error handling
    - automatic mode detection
    """

    def __init__(self, prog: str, description: str,
                 script_version: Optional[str] = None,
                 suite_version: Optional[str] = None):

        self.script_version = script_version
        self.suite_version = suite_version

        self.parser = CheckArgumentParser(
            prog=prog,
            description=description,
            formatter_class=CustomFormatter,
            add_help=True
        )

        self._add_shared_output_flags()
        self._add_shared_logging_flags()
        self._add_version_flag(prog)

    # --------------------------------------------------------
    # Shared Flags
    # --------------------------------------------------------
    def _add_shared_output_flags(self):
        out = self.parser.add_argument_group("Output Modes")
        out.add_argument("-v", "--verbose", action="store_true",
                         help="Verbose output mode")
        out.add_argument("-j", "--json", action="store_true",
                         help="JSON output mode")
        out.add_argument("-q", "--quiet", action="store_true",
                         help="Quiet mode (exit code only)")
        out.add_argument("--color", action="store_true",
                         help="Colorize the terminal display (json/verbose)")

    def _add_shared_logging_flags(self):
        log = self.parser.add_argument_group("Logging")
        log.add_argument("--log-dir", default=None,
                         help="Directory to store logs (optional)")
        log.add_argument("--log-max-mb", type=int, default=50,
                         help="Maximum log size before rotation")

    def _add_version_flag(self, prog: str):
        if self.script_version:
            suite = f"(Suite {self.suite_version})" if self.suite_version else ""

            python_ver = platform.python_version()
            platform_ver = platform.platform()

            version_text = (
                f"{prog} {self.script_version} {suite}\n"
                f"{format_runtime_info()}"
            )        
            
            self.parser.add_argument(
                "-V", "--version",
                action="version",
                version=version_text,
                help="Show script and suite version"
            )

    # --------------------------------------------------------
    # Extension API
    # --------------------------------------------------------
    def add_argument(self, *args, **kwargs):
        return self.parser.add_argument(*args, **kwargs)

    def add_group(self, name: str):
        return self.parser.add_argument_group(name)

    # --------------------------------------------------------
    # Parse + Mode Detection
    # --------------------------------------------------------
    def parse(self):
        args = self.parser.parse_args()
        flags = Flags.from_args(args)
        mode = detect_mode(flags)
        return args, flags, mode
