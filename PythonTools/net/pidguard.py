# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-06
 Modified: 2026-06-06
 File: PythonTools/net/pidguard.py
 Version: 1.0.0
 Description: Description of this module
"""
import os
import errno
import atexit
from pathlib import Path

from .tools import pid_is_running


class PidGuard:
    """
    Enforces single-instance execution using a PID file.
    Supports:
      - explicit acquire()/release()
      - context-manager usage
      - optional logging hooks
    """

    def __init__(self, pid_file: Path, logger=None):
        self.pid_file = pid_file
        self.pid_dir = pid_file.parent
        self.logger = logger

    # -----------------------------
    # Context manager support
    # -----------------------------
    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.release()
        return False  # don't suppress exceptions

    # -----------------------------
    # Core logic
    # -----------------------------
    def acquire(self):
        """Ensure only one instance is running."""
        self.pid_dir.mkdir(parents=True, exist_ok=True)

        if self.pid_file.exists():
            try:
                pid = int(self.pid_file.read_text().strip())
            except ValueError:
                pid = None

            if pid and pid_is_running(pid):
                msg = f"Instance already running (PID {pid})"
                if self.logger:
                    self.logger.error(msg)
                raise RuntimeError(msg)

            # stale PID file
            if self.logger:
                self.logger.warning("Stale PID file found; removing")
            self.pid_file.unlink()

        # write our PID
        self.pid_file.write_text(str(os.getpid()))

        if self.logger:
            self.logger.audit("PID_GUARD_ACQUIRED", f"PID {os.getpid()} locked")

        # ensure cleanup on exit
        atexit.register(self.release)

    def release(self):
        """Remove the PID file on exit."""
        try:
            self.pid_file.unlink()
            if self.logger:
                self.logger.audit("PID_GUARD_RELEASED", "PID file removed")
        except FileNotFoundError:
            pass
