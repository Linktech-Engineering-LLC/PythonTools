# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-06-17
 File: PythonTools/nagios/mode.py
 Version: 1.0.0
 Description: Flag engine and mode detection for Nagios-compatible tools.
"""

from enum import IntEnum, auto


class FlagNames(IntEnum):
    VERBOSE = auto()
    JSON = auto()
    QUIET = auto()


MODE_MAP = {
    FlagNames.JSON:    "json",
    FlagNames.VERBOSE: "verbose",
    FlagNames.QUIET:   "quiet",
}


class Flags:
    """
    Deterministic bitmask flag engine used by all NMS_Tools checks.
    """

    def __init__(self):
        self._mask = 0

    def set(self, flag: FlagNames, value: bool = True):
        if value:
            self._mask |= (1 << flag.value)
        else:
            self._mask &= ~(1 << flag.value)

    def get(self, flag: FlagNames) -> bool:
        return bool(self._mask & (1 << flag.value))

    def __getitem__(self, flag: FlagNames) -> bool:
        return self.get(flag)

    def __setitem__(self, flag: FlagNames, value: bool):
        self.set(flag, value)

    @classmethod
    def from_args(cls, args):
        f = cls()
        f[FlagNames.VERBOSE] = args.verbose
        f[FlagNames.JSON]    = args.json
        f[FlagNames.QUIET]   = args.quiet
        return f


def detect_mode(flags: Flags) -> str:
    """
    Determine output mode based on active flags.
    If no flags match, default to Nagios mode.
    """
    for flag, mode in MODE_MAP.items():
        if flags[flag]:
            return mode
    return "nagios"
