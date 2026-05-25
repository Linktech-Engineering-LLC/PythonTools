# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-25
 Modified: 2026-05-25
 File: PythonTools/parser/formatters.py
 Version: 1.0.0
 Description: Description of this module
"""



import argparse

class CustomFormatter(
    argparse.RawTextHelpFormatter,
    argparse.ArgumentDefaultsHelpFormatter,
):
    def _get_help_string(self, action):
        help_text = action.help or ""
        if "%(default)" in help_text:
            return help_text
        if action.default in (None, False):
            return help_text
        return f"{help_text} (default: {action.default})"
