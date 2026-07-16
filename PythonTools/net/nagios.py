# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-16
 Modified: 2026-07-16
 File: PythonTools/net/nagios.py
 Version: 1.0.0
 Description: Module description here
"""

def build_perfdata(interfaces, metric):
    """
    Build perfdata for a single selected metric.
    Returns a string like:
        'in_octets=12345c br0_in_octets=12345c eth0_in_octets=67890c'
    """
    parts = []

    for name, iface in interfaces.items():
        value = iface["counters"].get(metric)
        if value is None:
            continue

        # perfdata label: iface_metric
        label = f"{name}_{metric}"

        # perfdata value: <value>c (counter)
        parts.append(f"{label}={value}c")

    return " ".join(parts)

