# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-16
 Modified: 2026-07-16
 File: PythonTools/net/collectors.py
 Version: 1.0.0
 Description: Module description here
"""
import os
import psutil
import socket
from easysnmp import Session

from .tools import decode_mac
# -----------------------------
# Local Interface Information
# -----------------------------
def gather_local_interfaces(timeout=None):
    """
    Collects local interface information using psutil.
    Returns a deterministic structure suitable for JSON, verbose, and Nagios output.
    """

    interfaces = {}

    # psutil.net_if_addrs() gives addresses
    addrs = psutil.net_if_addrs()

    # psutil.net_if_stats() gives MTU, speed, duplex, flags
    stats = psutil.net_if_stats()

    for iface in sorted(addrs.keys()):

        stats_path = f"/sys/class/net/{iface}/statistics"
        counters = {}
        try:
            counters = {
                "in_octets": int(open(f"{stats_path}/rx_bytes").read()),
                "out_octets": int(open(f"{stats_path}/tx_bytes").read()),
                "in_ucast": int(open(f"{stats_path}/rx_packets").read()),
                "out_ucast": int(open(f"{stats_path}/tx_packets").read()),
                "in_multicast": int(open(f"{stats_path}/multicast").read()),
                "out_multicast": int(open(f"{stats_path}/tx_multicast").read()) if os.path.exists(f"{stats_path}/tx_multicast") else 0,
                "in_broadcast": int(open(f"{stats_path}/broadcast").read()) if os.path.exists(f"{stats_path}/broadcast") else 0,
                "out_broadcast": int(open(f"{stats_path}/tx_broadcast").read()) if os.path.exists(f"{stats_path}/tx_broadcast") else 0,
                "in_discards": int(open(f"{stats_path}/rx_dropped").read()),
                "out_discards": int(open(f"{stats_path}/tx_dropped").read()),
                "in_errors": int(open(f"{stats_path}/rx_errors").read()),
                "out_errors": int(open(f"{stats_path}/tx_errors").read())
            }
        except Exception:
            counters = {}

        iface_info = {
            "name": iface,
            "mac": None,
            "ipv4": [],
            "ipv6": [],
            "mtu": None,
            "speed": None,
            "duplex": None,
            "oper_up": None,
            "running": None,
            "counters": counters,
            "flags": []
        }

        # -----------------------------
        # Address information
        # -----------------------------
        for addr in addrs[iface]:
            if addr.family == socket.AF_INET:
                iface_info["ipv4"].append({
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })
            elif addr.family == socket.AF_INET6:
                iface_info["ipv6"].append({
                    "address": addr.address,
                    "netmask": addr.netmask,
                    "broadcast": addr.broadcast
                })
            elif addr.family in (psutil.AF_LINK, socket.AF_PACKET):
                iface_info["mac"] = addr.address

        # -----------------------------
        # Stats (MTU, speed, duplex, flags)
        # -----------------------------
        if iface in stats:
            st = stats[iface]
            iface_info["mtu"] = st.mtu
            iface_info["speed"] = st.speed  # may be 0 or None
            iface_info["duplex"] = st.duplex  # psutil.NIC_DUPLEX_FULL, etc.
            iface_info["oper_up"] = st.isup

            # psutil doesn't expose flags directly, but we can infer:
            if st.isup:
                iface_info["flags"].append("UP")
            if st.speed not in (0, None):
                iface_info["flags"].append("RUNNING")
        interfaces[iface] = iface_info

    return interfaces
# -----------------------------
# SNMP Interface Information
# -----------------------------
def snmp_walk(host, community, oid, port=161, timeout=3):
    session = Session(
        hostname=host,
        community=community,
        version=2,
        remote_port=port,
        timeout=timeout
    )

    results = session.walk(oid)

    out = {}
    for item in results:
        idx = int(item.oid_index)
        out[idx] = item.value
    return out
def gather_snmp_interfaces(ip, community, port=161, timeout=3):
    ifDescr       = snmp_walk(ip, community, "1.3.6.1.2.1.2.2.1.2", port, timeout)
    ifType        = snmp_walk(ip, community, "1.3.6.1.2.1.2.2.1.3", port, timeout)
    ifMtu         = snmp_walk(ip, community, "1.3.6.1.2.1.2.2.1.4", port, timeout)
    ifSpeed       = snmp_walk(ip, community, "1.3.6.1.2.1.2.2.1.5", port, timeout)
    ifPhysAddress = snmp_walk(ip, community, "1.3.6.1.2.1.2.2.1.6", port, timeout)
    ifAdminStatus = snmp_walk(ip, community, "1.3.6.1.2.1.2.2.1.7", port, timeout)
    ifOperStatus  = snmp_walk(ip, community, "1.3.6.1.2.1.2.2.1.8", port, timeout)
    dot3Duplex    = snmp_walk(ip, community, "1.3.6.1.2.1.10.7.2.1.19", port, timeout)

    interfaces = {}

    for idx in sorted(ifDescr.keys()):
        name = ifDescr[idx]

        iface = {
            "name": name,
            "mac": decode_mac(ifPhysAddress.get(idx)),
            "mtu": int(ifMtu.get(idx, 0)),
            "speed": int(ifSpeed.get(idx, 0)),
            "duplex": dot3Duplex.get(idx),
            "up": (str(ifOperStatus.get(idx)) == "1"),
            "running": (str(ifOperStatus.get(idx)) == "1"),
            "flags": []
        }

        if iface["up"]:
            iface["flags"].append("UP")
        if iface["speed"] > 0:
            iface["flags"].append("RUNNING")

        interfaces[name] = iface

    return interfaces

