# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-16
 Modified: 2026-07-16
 File: PythonTools/net/normalize.py
 Version: 1.0.0
 Description: Module description here
"""
import psutil

SPEED_UNITS = {
    "G": 1000,
    "M": 1,
}

def normalize_interfaces(raw, source):
    normalized = {}

    for name, iface in raw.items():
        mac = iface.get("mac")

        # Normalize MAC (SNMP hex → colon format)
        if not mac:
            mac = "00:00:00:00:00:00"

        # Normalize admin/oper
        admin_up = iface.get("admin_up", True)
        oper_up = iface.get("oper_up", False)

        # Normalize flags
        flags = []
        if admin_up:
            flags.append("UP")
        if oper_up:
            flags.append("RUNNING")

        normalized[name] = {
            "name": name,
            "mac": mac,
            "ipv4": iface.get("ipv4", []),
            "ipv6": iface.get("ipv6", []),
            "mtu": iface.get("mtu"),
            "speed": normalize_speed(iface.get("speed")),
            "duplex": normalize_duplex(iface.get("duplex")),
            "admin_up": admin_up,
            "oper_up": oper_up,
            "counters": normalize_counters(iface.get("counters",{})),
            "flags": flags,
            "ifType": iface.get("ifType")
        }

    return normalized
def normalize_counters(raw):
    """
    Normalize interface counters from either local or SNMP collectors.
    Ensures all fields exist, are integers, and follow the canonical schema.
    """

    def to_int(value):
        try:
            return int(value)
        except Exception:
            return 0

    return {
        "in_octets":     to_int(raw.get("in_octets")),
        "out_octets":    to_int(raw.get("out_octets")),
        "in_ucast":      to_int(raw.get("in_ucast")),
        "out_ucast":     to_int(raw.get("out_ucast")),
        "in_multicast":  to_int(raw.get("in_multicast")),
        "out_multicast": to_int(raw.get("out_multicast")),
        "in_broadcast":  to_int(raw.get("in_broadcast")),
        "out_broadcast": to_int(raw.get("out_broadcast")),
        "in_discards":   to_int(raw.get("in_discards")),
        "out_discards":  to_int(raw.get("out_discards")),
        "in_errors":     to_int(raw.get("in_errors")),
        "out_errors":    to_int(raw.get("out_errors"))
    }
def normalize_speed(value):
    """
    Normalize speed to Mbps.
    SNMP reports bits per second.
    psutil reports Mbps.
    """
    try:
        v = int(value)
        if v in (0, None, 4294967295, 4294):
            return None
        if v > 100000:  # SNMP bps threshold
            return v // 1_000_000
        return v
    except Exception:
        return None
def normalize_duplex(value):
    """
    Normalize duplex to 'full', 'half', or 'unknown'.
    SNMP EtherLike-MIB uses integers.
    psutil uses constants.
    """
    if value in (None, "unknown"):
        return "unknown"

    # psutil constants
    if value == psutil.NIC_DUPLEX_FULL:
        return "full"
    if value == psutil.NIC_DUPLEX_HALF:
        return "half"

    # SNMP EtherLike-MIB
    try:
        v = int(value)
        if v == 3:
            return "full"
        if v == 2:
            return "half"
    except Exception:
        pass

    return "unknown"
def fmt_speed(speed):
    if speed is None:
        return "-"
    for suffix, factor in SPEED_UNITS.items():
        if speed >= factor:
            return f"{speed // factor}{suffix}"
    return str(speed)
def fmt_flags(flags):
    return ",".join(flags) if flags else "-"
def parse_speed(s):
    s = s.strip().upper()
    for suffix, factor in SPEED_UNITS.items():
        if s.endswith(suffix):
            return int(s[:-1]) * factor
    return int(s)
