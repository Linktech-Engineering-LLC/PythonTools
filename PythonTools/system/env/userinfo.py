# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-10-08
 Modified: 2026-10-08
 File: PythonTools/system/env/userinfo.py
 Version: 1.0.0
 Description: User identity introspection for the current OS user.
"""

import pwd
import getpass


def get_current_user():
    """
    Return a dict describing the current OS user:
    login, uid, gid, home, shell, full name (normalized GECOS).
    """
    login = getpass.getuser()
    pw = pwd.getpwnam(login)

    return {
        "login": login,
        "uid": pw.pw_uid,
        "gid": pw.pw_gid,
        "home": pw.pw_dir,
        "shell": pw.pw_shell,
        "name": pw.pw_gecos.split(",")[0],  # normalized full name
    }
