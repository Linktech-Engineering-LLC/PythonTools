# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
Modified: 2026-09-08
 File: PythonTools/nagios/parser.py
 Version: 1.0.0
 Description: Base parser for Nagios-compatible NMS_Tools checks.
"""

import argparse
import os

from PythonTools.parser import BaseScriptParser
from PythonTools.nagios.mode import Flags, FlagNames, detect_mode
from PythonTools.nagios.states import UNKNOWN
from PythonTools.nagios.runtime import format_runtime_info, build_version_string

# ------------------------------------------------------------
# Base Parser for all NMS_Tools checks
# ------------------------------------------------------------
class BaseNagiosParser(BaseScriptParser):
    def __init__(self, prog, description, script_version=None, suite_version=None):

        # Build Nagios-style version string
        version_string = build_version_string(prog, script_version, suite_version)

        # Initialize the global parser with the custom version string
        super().__init__(prog, description, version_string)

        # Remove irrelevant global groups
        self.remove_group("Config Options")
        self.remove_group("Inventory Options")
        self.remove_group("Vault Options")

        # Remove global JSON/color flags
        self.remove_flag("--json")
        self.remove_flag("--color")

        # Add Nagios-specific flags
        nagios = self.add_group("Nagios Output Options")
        nagios.add_argument("-j", "--json", action="store_true", help="JSON output mode")
        nagios.add_argument("-q", "--quiet", action="store_true", help="Quiet mode")
        nagios.add_argument("--color", action="store_true", help="Colorize output")
        nagios.add_argument("--output", metavar="FILE", help="Write output to FILE")

    def parse(self):
        args = super().parse()
        flags = Flags.from_args(args)
        mode = detect_mode(flags)
        return args, flags, mode

