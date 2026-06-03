# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-05-25
 Modified: 2026-05-30
 File: PythonTools/parser/errors.py
 Version: 1.0.0
 Description: Description of this module
"""



import sys
import argparse

class CheckArgError(Exception):
    pass
class CheckArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # Allow missing subcommand so ScriptParser can set a default
        if "the following arguments are required: command" in message:
            raise argparse.ArgumentError(None, message)

        # Otherwise behave normally
        super().error(message)

