# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-21
 Modified: 2026-05-21
 File: PythonTools/ansible/loader.py
 Version: 1.0.0
 Description: 
    This module:
    - Loads a schema (YAML)
    - Loads an inventory (YAML)
    - Validates structure recursively
    - Applies defaults
    - Applies inheritance
    - Produces a normalized inventory tree
"""
from __future__ import annotations

import yaml

from pathlib import Path
from typing import Any, Dict, List, Optional


class SchemaError(Exception):
    pass
class InventoryError(Exception):
    pass
class GenericInventoryLoader:
    """
    Loads and validates an inventory YAML file using a declarative schema.
    Applies inheritance and default values defined in the schema.
    """

    def __init__(self, inventory_path: str | Path, schema_path: str | Path):
        self.inventory_path = Path(inventory_path)
        self.schema_path = Path(schema_path)

        self.schema = self._load_yaml(self.schema_path)
        self.inventory = self._load_yaml(self.inventory_path)

    # ------------------------------------------------------------
    # YAML loader
    # ------------------------------------------------------------
    def _load_yaml(self, path: Path) -> dict:
        if not path.exists():
            raise InventoryError(f"File not found: {path}")

        try:
            return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception as exc:
            raise InventoryError(f"Invalid YAML syntax in: {path}") from exc

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------
    def load(self) -> dict:
        """
        Validate, apply inheritance, apply defaults, and return normalized inventory.
        """
        root_schema = self.schema.get("root")
        if not root_schema:
            raise SchemaError("Schema missing required 'root' definition")

        validated = self._validate_node(self.inventory, root_schema, path="root")
        normalized = self._apply_inheritance(validated, root_schema)
        return normalized

    # ------------------------------------------------------------
    # Recursive validation
    # ------------------------------------------------------------
    def _validate_node(self, node, schema, path):
        """
        Recursively validate a node against the schema.
        """
        expected_type = schema.get("type")
        required = schema.get("required", False)

        # Required check
        if node is None:
            if required:
                raise InventoryError(f"Missing required node at: {path}")
            return None

        # Type check
        if expected_type == "dict" and not isinstance(node, dict):
            raise InventoryError(f"Expected dict at {path}, got {type(node).__name__}")

        if expected_type == "list" and not isinstance(node, list):
            raise InventoryError(f"Expected list at {path}, got {type(node).__name__}")

        if expected_type == "str" and not isinstance(node, str):
            raise InventoryError(f"Expected str at {path}, got {type(node).__name__}")

        if expected_type == "bool" and not isinstance(node, bool):
            raise InventoryError(f"Expected bool at {path}, got {type(node).__name__}")

        # If no children defined, return node as-is
        children = schema.get("children")
        if not children:
            return node

        # Validate children
        validated = {}

        for key, value in node.items():
            matched_schema = None

            # Exact key match
            if key in children:
                matched_schema = children[key]

            # Wildcard match
            elif "*" in children:
                matched_schema = children["*"]

            if not matched_schema:
                raise InventoryError(f"Unexpected key '{key}' at {path}")

            validated[key] = self._validate_node(
                value,
                matched_schema,
                path=f"{path}.{key}"
            )

        return validated

    # ------------------------------------------------------------
    # Inheritance + defaults
    # ------------------------------------------------------------
    def _apply_inheritance(self, node, schema, parent=None):
        """
        Recursively apply inheritance and defaults.
        """
        if not isinstance(node, dict):
            return node

        inherit = schema.get("inherit", False)
        defaults = schema.get("defaults", {})

        # Start with defaults
        merged = dict(defaults)

        # Inherit from parent if allowed
        if inherit and isinstance(parent, dict):
            for k, v in parent.items():
                if k not in merged:
                    merged[k] = v

        # Merge actual node values
        for key, value in node.items():
            child_schema = schema.get("children", {}).get(key) or schema.get("children", {}).get("*")

            if child_schema:
                merged[key] = self._apply_inheritance(value, child_schema, merged)
            else:
                merged[key] = value

        return merged
    # ------------------------------------------------------------
    # Normalization Layer
    # ------------------------------------------------------------
    def normalize(self) -> List[Dict[str, Any]]:
        """
        Convert the inherited inventory tree into a flattened list of host objects.
        """
        tree = self.load()
        output = []

        for family_name, family_node in tree.items():
            if not isinstance(family_node, dict):
                continue

            family_vars = family_node.get("vars", {})
            family_port = family_vars.get("port")

            # Iterate distros
            for distro_name, distro_node in family_node.items():
                if distro_name == "vars":
                    continue
                if not isinstance(distro_node, dict):
                    continue

                distro_vars = distro_node.get("vars", {})
                distro_port = distro_vars.get("port")

                # Extract package commands
                raw_cmds = distro_node.get("packages", {}) or {}
                exit_codes = raw_cmds.get("exit_codes", {})
                commands = {k: v for k, v in raw_cmds.items() if k != "exit_codes"}

                # Hosts block
                hosts_block = distro_node.get("hosts", {}) or {}

                for host_name, host_data in hosts_block.items():
                    if not isinstance(host_data, dict):
                        continue

                    # Skip disabled hosts
                    if not host_data.get("enabled", True):
                        continue

                    # Required: address
                    address = host_data.get("address")
                    if not address:
                        raise InventoryError(
                            f"Host '{host_name}' under {family_name}/{distro_name} is missing 'address'."
                        )

                    # Port inheritance: host → distro → family → default
                    host_port = (
                        host_data.get("port")
                        or distro_port
                        or family_port
                        or 22
                    )

                    # Merge commands: distro-level first, host-level overrides
                    merged_cmds = {}
                    merged_cmds.update(commands)
                    merged_cmds.update(host_data.get("packages", {}) or {})

                    # Build final host object
                    host_obj = {
                        "name": host_name,
                        "family": family_name,
                        "distro": distro_name,
                        "enabled": host_data.get("enabled", True),
                        "address": address,
                        "port": host_port,
                        "commands": merged_cmds,
                        "exit_codes": exit_codes,
                        "vm_host": host_data.get("vm_host"),
                    }

                    output.append(host_obj)

        return output
