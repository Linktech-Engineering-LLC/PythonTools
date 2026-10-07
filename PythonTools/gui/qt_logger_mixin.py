# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-10-07
 Modified: 2026-10-07
 File: PythonTools/gui/qt_logger_mixin.py
 Version: 1.0.0
 Description: Module description here
"""


import inspect

from PySide6.QtCore import Signal

from .logger_mixin import LoggerMixin

class QtLoggerMixin(LoggerMixin):
    def _wrap_methods_for_logging(self):
        for name in dir(self):
            if name.startswith("_"):
                continue

            attr = getattr(self, name)
            if attr is None:
                continue

            # Skip Qt signals
            if hasattr(attr, "connect") and hasattr(attr, "emit"):
                continue

            # Skip Qt event handlers
            if name.endswith("Event"):
                continue

            # Skip Qt internals
            module = getattr(attr, "__module__", None)
            if module and module.startswith("PySide6"):
                continue

            # Only wrap methods defined on this class
            owner = getattr(type(self), name, None)
            if owner is None:
                continue

            if inspect.isfunction(owner) or inspect.ismethod(owner):
                setattr(self, name, self._log_wrapper(attr))
