# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-10-13
 Modified: 2026-10-13
 File: PythonTools/system/schemas/loader.py
 Version: 1.0.0
 Description: Module description here
"""

import json
from jsonschema import validate, ValidationError
from pathlib import Path

def load_schema(project: str, schema_type: str):
    base = Path(__file__).parent / project.lower()
    schema_path = base / f"{schema_type}.json"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_path}")

    return json.loads(schema_path.read_text())

def validate_config(project: str, schema_type: str, config: dict) -> dict:
    schema = load_schema(project, schema_type)

    try:
        validate(instance=config, schema=schema)
    except ValidationError as e:
        raise ValueError(
            f"{project}.{schema_type} validation failed: {e.message}"
        )

    return config