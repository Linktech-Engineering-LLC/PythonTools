# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-09-25
Modified: 2026-09-25
 File: PythonTools/net/ssh/reachability.py
 Version: 1.0.0
 Description: Module description here
"""
import socket

from .port import get_ssh_port_for_host

def is_ssh_reachable(hostname, timeout=0.5):
    port = get_ssh_port_for_host(hostname)

    try:
        with socket.create_connection((hostname, port), timeout=timeout):
            return True
    except OSError:
        return False
