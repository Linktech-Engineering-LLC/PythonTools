# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-09-02
Modified: 2026-09-02
 File: PythonTools/test/displays.py
 Version: 1.0.0
 Description: Module description here
"""
import json

from ..color import colorize, Color

def display_results(results, args):
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed

    # JSON mode
    if args.json:
        print(json.dumps([r.__dict__ for r in results], indent=2))
        return

    # Verbose mode
    if args.verbose:
        for r in results:
            if r.passed:
                print(colorize(f"PASS: {r.name} ({r.duration:.4f}s)", Color.GREEN, args.color))
            else:
                print(colorize(f"FAIL: {r.name} ({r.duration:.4f}s) error={r.error}", Color.RED, args.color))

        print(colorize(f"{passed} passed, {failed} failed",
                       Color.GREEN if failed == 0 else Color.RED,
                       args.color))
    else:
        print(colorize(f"{passed} passed, {failed} failed",
                       Color.GREEN if failed == 0 else Color.RED,
                       args.color))

    # 🔹 Always reset terminal color before logger writes to stderr
    print(Color.RESET, end="")

