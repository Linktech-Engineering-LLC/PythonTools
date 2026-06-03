# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-25
 Modified: 2026-05-30
 File: PythonTools/parser/inventory.py
 Version: 1.0.0
 Description: Description of this module
"""

from pathlib import Path
import os
import yaml

from PythonTools.parser.BaseScriptParser import BaseScriptParser
from PythonTools.parser.errors import CheckArgError


class InventoryBaseParser(BaseScriptParser):
    """
    Base class for tools that use an inventory file.
    Provides:
      - --inventory
      - file existence validation
      - YAML loading
    Does NOT define any schema (RunUpdates, BotScanner, etc.)
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self._add_inventory_args()

    # --------------------------------------------------------
    # Inventory Option
    # --------------------------------------------------------
    def _add_inventory_args(self):
        inv = self.parser.add_argument_group("Inventory Options")

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
    # Parse + Load Inventory
    # --------------------------------------------------------
    def parse(self):
        args = super().parse()

        if args.inventory:
            self.inventory_path = Path(args.inventory).expanduser()
            self._validate_inventory_path()
            self.inventory_data = self._load_inventory_yaml()
        else:
            self.inventory_path = None
            self.inventory_data = None

        return args

    # --------------------------------------------------------
    # Schema Validation Hook
    # --------------------------------------------------------
    def _validate(self):
        """
        Child classes override this to validate their schema.
        """
        super()._validate()
