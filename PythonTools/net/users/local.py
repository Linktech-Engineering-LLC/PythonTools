# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-09-25
Modified: 2026-09-25
 File: PythonTools/net/users/local.py
 Version: 1.0.0
 Description: Module description here
"""

import getpass
import pwd

def get_valid_users():
    current_user = getpass.getuser()
    users = []

    for entry in pwd.getpwall():
        name = entry.pw_name
        uid = entry.pw_uid
        home = entry.pw_dir
        shell = entry.pw_shell

        # Always include root
        if name == "root":
            users.append(name)
            continue

        # Skip system accounts (UID < 1000)
        if uid < 1000:
            continue

        # Skip accounts without a home directory
        if not home or home == "/":
            continue

        # Skip nologin shells
        if shell.endswith("nologin") or shell.endswith("false"):
            continue

        users.append(name)

    # Ensure current user is first and unique
    users = [current_user] + [u for u in users if u != current_user]

    return users
