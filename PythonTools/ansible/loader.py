# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-21
 Modified: 2026-05-22
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


class SchemaError(Exception):
    pass
class InventoryError(Exception):
    pass
class InventoryLoadError(Exception):
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

    @property
    def raw_yaml(self) -> dict:
        """
        Return the raw YAML inventory exactly as loaded from disk,
        before validation, inheritance, or normalization.
        """
        return self.inventory

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
