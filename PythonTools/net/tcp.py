# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-04
 Modified: 2026-08-04
 File: PythonTools/net/tcp.py
 Version: 1.0.0
 Description: Module description here
"""

import socket

def check_port(host, port, timeout):
    """
    Attempt a single TCP connection to host:port with a strict timeout.

    Returns one of:
        "open"
        "closed"
        "timeout"
        "unreachable"
    """

    try:
        with socket.create_connection((host, port), timeout):
            return "open"

    except socket.timeout:
        return "timeout"

    except ConnectionRefusedError:
        return "closed"

    except OSError:
        # Includes: network unreachable, no route to host, DNS issues, etc.
        return "unreachable"
