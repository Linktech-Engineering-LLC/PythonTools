# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-25
Modified: 2026-09-22
 File: PythonTools/parser/BaseScriptParser.py
 Version: 1.0.0
 Description: Description of this module
"""
import os

from PythonTools.parser.formatters import CustomFormatter
from PythonTools.parser.errors import CheckArgumentParser

class BaseScriptParser:
    """
    Universal base parser for all CLI-driven tools.
    Provides:
      - core switches
      - logging switches
      - vault switches
      - shared validation hook
    """

    def __init__(self, prog, description, version_string):
        self.global_parent = CheckArgumentParser(
            add_help=False,
            formatter_class=CustomFormatter
        )

        self.version_string = version_string
        self._dynamic_groups = {}
        self._dynamic_subcommands = {}

        self._add_core_args()
        self._add_logging_args()
        self._add_vault_args()
        self._add_cfg_args()
        self._add_debug_args()
        self._add_inventory_args()

        self.parser = CheckArgumentParser(
            prog=prog,
            description=description,
            usage=f"{prog} [options] {{version}}",
            formatter_class=CustomFormatter,
            add_help=True,
            parents=[self.global_parent],   # <-- THIS IS THE FIX
        )
        # Subcommand root
        self.subparsers = self.parser.add_subparsers(dest="command")
        # JSON Output Options
        self.global_parent.add_argument(
            "--json", 
            action="store_true",
            help="Output results in JSON format (pretty-printed when TTY)"
        )

        self.global_parent.add_argument(
            "--color",
            action="store_true",
            help="Force colorized output (auto-enabled when TTY)"
        )

        self._add_version_subcommand()

    def _add_version_subcommand(self):
        ver = self.subparsers.add_parser(
            "version",
            parents=[self.global_parent],
            add_help=False,
            help="Show version information"
        )
        ver.set_defaults(func=self._handle_version)
        self.version_parser = ver
    def _handle_version(self, args):
        print(self.version_string)
        os._exit(0)
    # --------------------------------------------------------
    # Core Options
    # --------------------------------------------------------
    def _add_core_args(self):
        core = self.global_parent.add_argument_group("Core Options")

        core.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose output"
        )
        core.add_argument(
            "--quiet",
            action="store_true",
            help="Suppress all non-error output"
        )
        core.add_argument(
            "--dry-run",
            dest="dry_run",
            action="store_true",
            help="Simulate actions without applying changes"
        )
        core.add_argument(
            "--fail-fast",
            dest="fail_fast",
            action="store_true",
            help="Stop on first error"
        )
        core.add_argument(
            "--continue-on-error",
            dest="continue_on_error",
            action="store_true",
            help="Continue processing even if errors"
        )
        #core.add_argument(
        #    "-V", "--version",
        #    action="version",
        #    version=self.version_string
        #)

    # --------------------------------------------------------
    # Logging Options
    # --------------------------------------------------------
    def _add_logging_args(self):
        log = self.global_parent.add_argument_group("Logging Options")

        log.add_argument(
            "--log-dir",
            dest="log_dir",
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
        log.add_argument(
            "--log-level",
            choices=["debug","info","warning","error"],
            default="info",
            help="Logging verbosity"
        )
        log.add_argument(
            "--no-log",
            action="store_true",
            help="Disable logging entirely"
        )

    # --------------------------------------------------------
    # Config Options
    # --------------------------------------------------------
    def _add_cfg_args(self):
        cfg = self.global_parent.add_argument_group("Config Options")
        self._dynamic_groups["Config Options"] = cfg
    
        cfg.add_argument(
            "--config-dir",
            help="Override config directory",
        ) 
    # --------------------------------------------------------
    # Debug Options
    # --------------------------------------------------------
    def _add_debug_args(self):
        debug = self.global_parent.add_argument_group("Debug Options")
        debug.add_argument(
            "--debug",
            action="store_true",
            help="Enable debug logging"
        )
        debug.add_argument(
            "--trace",
            action="store_true",
            help="Trace pipeline steps and internal flow"
        )
        debug.add_argument(
            "--profile",
            action="store_true",
            help="Measure execution timing for major stages"
        )
        debug.add_argument(
            "--dump-svg",
            action="store_true",
            help="Dump raw SVG before recoloring"
        )
        debug.add_argument(
            "--dump-final",
            action="store_true",
            help="Dump final processed output"
        )
        debug.add_argument(
            "--dump-meta",
            action="store_true",
            help="Dump metadata JSON for debugging"
        )
        debug.add_argument(
            "--trace-flags",
            action="store_true",
            help="Show flag resolution and parser behavior"
        )
    # --------------------------------------------------------
    # Inventory Option
    # --------------------------------------------------------
    def _add_inventory_args(self):
        inv = self.global_parent.add_argument_group("Inventory Options")
        self._dynamic_groups["Inventory Options"] = inv
        
        inv.add_argument(
            "-i", "--inventory",
            required=False,
            help="Path to inventory YAML file"
        )

        inv.add_argument(
            "--schema-dir",
            help="Override schema directory",
        )
    
    # --------------------------------------------------------
    # Vault Options
    # --------------------------------------------------------
    def _add_vault_args(self):
        vault = self.global_parent.add_argument_group("Vault Options")
        self._dynamic_groups["Vault Options"] = vault

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
    # -------------------------------------------------------
    # Dynamic Command/Group Processing
    # -------------------------------------------------------
    def add_group(self, title: str):
        """
        Add a new argument group to the global parent parser.
        Returns the group so the caller can add arguments to it.
        """
        grp = self.parser.add_argument_group(title)
        self._dynamic_groups[title] = grp
        return grp
    def add_subcommand(self, name: str, help: str | None):
        """
        Add a new subcommand to the parser.
        Returns the subparser so the caller can add arguments to it.
        """
        sub = self.subparsers.add_parser(
            name,
            parents=[self.global_parent],
            add_help=True,
            help=help
        )
        self._dynamic_subcommands[name] = sub   
        return sub
    def remove_group(self, title: str):
        parser = self.parser  # the parser that prints help

        # Find the actual group object by title
        grp = None
        for g in parser._action_groups:
            if g.title == title:
                grp = g
                break

        if grp is None:
            return False

        # Remove the group object
        try:
            parser._action_groups.remove(grp)
        except ValueError:
            pass

        # Remove actions belonging to this group
        for action in list(grp._group_actions):
            # Remove from actions list
            try:
                parser._actions.remove(action)
            except ValueError:
                pass

            # Remove option strings
            for opt in list(action.option_strings):
                parser._option_string_actions.pop(opt, None)

        return True
    def add_flag(self, *flags, **kwargs):
        """
        Add a standalone flag directly to the global parent parser.
        Example:
            parser.add_flag("--src", help="Source folder")
        """
        action = self.parser.add_argument(*flags, **kwargs)
        return action
    def remove_flag(self, flag: str):
        # Find the action first
        action = self.global_parent._option_string_actions.get(flag)
        if not action:
            return

        # Remove from actions list
        self.global_parent._actions = [
            a for a in self.global_parent._actions
            if a is not action
        ]

        # Remove all option strings for that action
        for opt in list(action.option_strings):
            self.global_parent._option_string_actions.pop(opt, None)
    def remove_command_positional(self):
        parser = self.parser  # the active parser

        for action in list(parser._actions):
            # Positional arguments have no option_strings
            if action.option_strings == [] and action.dest == "command":
                parser._actions.remove(action)
                return True

        return False
    
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
