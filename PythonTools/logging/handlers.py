# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-14
 Modified: 2026-05-26
 File: PythonTools/logging/handlers.py
 Version: 1.0.0
 Description: Description of this module
"""

# system imports
import os
import logging
import time
import tarfile
import zipfile
import glob
from logging.handlers import RotatingFileHandler


def get_project_logger():
    """
    Determine the project name from the module path and return its logger.
    Example:
        RunUpdates.logging.handlers -> RunUpdates.Logger
    """
    pkg = __package__  # e.g., "RunUpdates.logging"
    if pkg:
        project = pkg.split(".")[0]  # "RunUpdates"
    else:
        project = "DefaultProject"

    return logging.getLogger(f"{project}.Logger")


class ArchiveRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename: str, mode: str = "zip", *args, **kwargs):
        super().__init__(filename, *args, **kwargs)
        self.archive_mode = mode

    def doRollover(self):
        super().doRollover()

        rotated_file = f"{self.baseFilename}.1"
        if not os.path.exists(rotated_file):
            return

        # Date-only stamp
        date_stamp = time.strftime("%Y%m%d")
        base_dir = os.path.dirname(self.baseFilename)
        project_name = os.path.splitext(os.path.basename(self.baseFilename))[0]

        if self.archive_mode == "zip":
            archive_name = os.path.join(base_dir, f"{project_name}_{date_stamp}.zip")
            with zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(rotated_file, arcname=os.path.basename(rotated_file))

        elif self.archive_mode == "tgz":
            archive_name = os.path.join(base_dir, f"{project_name}_{date_stamp}.tgz")
            with tarfile.open(archive_name, "w:gz") as tar:
                tar.add(rotated_file, arcname=os.path.basename(rotated_file))

        else:
            archive_name = rotated_file

        os.remove(rotated_file)

        # Enforce backup count on matching archives
        ext = "zip" if self.archive_mode == "zip" else "tgz"
        pattern = os.path.join(base_dir, f"{project_name}_*.{ext}")
        archives = sorted(glob.glob(pattern), key=os.path.getmtime)

        if len(archives) > self.backupCount:
            for old_archive in archives[: -self.backupCount]:
                os.remove(old_archive)

        self.stream = self._open()
