# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-09-25
Modified: 2026-09-25
 File: PythonTools/net/ssh/config.py
 Version: 1.0.0
 Description: Module description here
"""
import os
import glob
import fnmatch
import socket

def parse_ssh_config_for_port(path, hostname):
    port = None
    active = False

    try:
        with open(path) as f:
            for line in f:
                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if line.lower().startswith("host "):
                    patterns = line.split()[1:]
                    active = any(fnmatch.fnmatch(hostname, p) for p in patterns)
                    continue

                if active and line.lower().startswith("port "):
                    try:
                        return int(line.split()[1])
                    except ValueError:
                        pass

    except FileNotFoundError:
        pass

    return None


def get_ssh_port_for_host(hostname):
    # 1. User config (~/.ssh/config)
    user_config = os.path.expanduser("~/.ssh/config")
    if os.path.exists(user_config):
        port = parse_ssh_config_for_port(user_config, hostname)
        if port:
            return port

    # 2. System-wide configs (multiple possible locations)
    system_paths = [
        "/etc/ssh/ssh_config",
        "/etc/ssh_config",
    ]

    # Include modular configs
    system_paths.extend(glob.glob("/etc/ssh/ssh_config.d/*.conf"))

    for path in system_paths:
        if os.path.exists(path):
            port = parse_ssh_config_for_port(path, hostname)
            if port:
                return port

    # 3. Default
    return 22

