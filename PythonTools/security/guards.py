# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-09-24
Modified: 2026-09-24
 File: PythonTools/security/guards.py
 Version: 1.0.0
 Description: Module description here
"""
import os

def assert_not_root():
    if os.geteuid() == 0:
        raise RuntimeError("RunUpdates must not be executed as root")
def assert_sudo_available(sudo_password):
    if sudo_password is None:
        raise RuntimeError("No sudo password available for non-root execution")
