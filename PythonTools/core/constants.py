# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-13
Modified: 2026-04-17
 File: PythonTools/core/constants.py
 Version: 1.0.0
 Description: Generic, project‑agnostic constants for the PythonTools package.
"""

from pathlib import Path
import platform
import sys

# ------------------------------------------------------------
# PythonTools package metadata (internal only)
# ------------------------------------------------------------

# Root of the PythonTools package (…/PythonTools/PythonTools)
PACKAGE_ROOT = Path(__file__).resolve().parents[1]

# Root of the PythonTools project repository (…/PythonTools)
PROJECT_ROOT = PACKAGE_ROOT.parent

# System information (generic)
PYTHON_VERSION = sys.version.split()[0]
LINUX_VERSION = platform.release()
