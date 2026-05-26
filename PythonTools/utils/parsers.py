# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-23
 Modified: 2026-05-26
 File: PythonTools/utils/parsers.py
 Version: 1.0.0
 Description: Description of this module
"""

# PythonTools/utils/parsers.py

import re
from typing import Dict, List, Any, Optional


class Parser:
    """
    Generic multi-distro parsing engine.
    Used for check/update/clean summaries across all distros.
    """

    PARSING_RULES: Dict[str, Dict[str, str]] = {

        # Debian-family
        "debian.check": {
            "summary": r"(\d+)\s+packages can be upgraded",
            "up_to_date": r"All packages are up to date",
        },

        "debian.update": {
            "upgraded": r"^\s{2}(\S+)\s*$",
        },

        # RedHat-family
        "redhat.update": {
            "upgraded": r"^\s+(\S+)\.\S+\s+\S+$",
        },

        # openSUSE
        "opensuse.update": {
            "upgraded": r"^\s+(\S+)\s+\|\s+\S+\s+\|\s+\S+\s+\|\s+\S+$",
        },
    }

    @staticmethod
    def parse_output(output: str, rules: Dict[str, str]) -> Dict[str, Any]:
        result: Dict[str, List[str]] = {}
        if not output or not rules:
            return result

        for key, pattern in rules.items():
            matches = re.findall(pattern, output, re.MULTILINE)
            if matches:
                result[key] = matches

        return result

    @classmethod
    def parse(cls, distro: str, step: str, output: str) -> Optional[Dict[str, Any]]:
        key = f"{distro}.{step}"
        rules = cls.PARSING_RULES.get(key)
        if not rules:
            return None

        parsed = cls.parse_output(output, rules)
        return parsed or None
