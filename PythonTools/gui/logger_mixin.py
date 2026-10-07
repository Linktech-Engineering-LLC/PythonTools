# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-10-07
 Modified: 2026-10-07
 File: PythonTools/gui/logger_mixin.py
 Version: 1.0.0
 Description: Module description here
"""

import logging
import inspect

class LoggerMixin:
    def _init_logger(self, logctx, subsystem_name, projectname):
        self.logctx = logctx
        self.logfactory = None

        if logctx:
            self.logfactory = logctx.get("factory")

        if self.logfactory:
            self.logger = self.logfactory.get_logger(subsystem_name)
        else:
            self.logger = logging.getLogger(f"{projectname}.{subsystem_name}")
            self.logger.addHandler(logging.NullHandler())

    def finalize_logging_wrappers(self):
        if self.logctx and self.logctx.get("level") == "DEBUG":
            self._wrap_methods_for_logging()

    def _wrap_methods_for_logging(self):
        for name in dir(self):
            if name.startswith("_"):
                continue

            attr = getattr(self, name)
            if attr is None:
                continue

            # Only wrap methods defined on this class
            owner = getattr(type(self), name, None)
            if owner is None:
                continue

            if inspect.isfunction(owner) or inspect.ismethod(owner):
                setattr(self, name, self._log_wrapper(attr))

    def _log_wrapper(self, func):
        def wrapper(*args, **kwargs):
            self.logger.debug(f"{func.__name__} called.")
            return func(*args, **kwargs)
        return wrapper
