# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-08-04
 Modified: 2026-08-04
 File: PythonTools/parsing/ports.py
 Version: 1.0.0
 Description: Module description here
"""
import socket

from ..nagios.parser import CheckArgError

def parse_ports(port_string):
    """
    Parse a comma-delimited list of ports or port ranges.
    Rejects host:port, host:service, and service names.
    Returns a sorted, deduped list of integer ports.
    """
    if not port_string:
        return []

    tokens = [t.strip() for t in port_string.split(",") if t.strip()]
    ports = []

    for token in tokens:
        # Reject host:port or host:service
        if ":" in token:
            raise CheckArgError(
                f"Invalid port token '{token}'. Hostnames or service names are not "
                "allowed in --ports; use -H/--host for hosts and -s/--service for services."
            )

        # Reject service names (alphabetic tokens)
        if token.isalpha():
            raise CheckArgError(
                f"Invalid port token '{token}'. Service names belong in --service, not --ports."
            )

        # Handle ranges
        if "-" in token:
            try:
                start, end = token.split("-", 1)
                start = int(start)
                end = int(end)
            except ValueError:
                raise CheckArgError(f"Invalid port range '{token}'.")

            if start < 1 or end < 1 or start > 65535 or end > 65535:
                raise CheckArgError(f"Port range '{token}' is out of valid TCP range.")

            if start > end:
                raise CheckArgError(f"Invalid port range '{token}': start > end.")

            ports.extend(range(start, end + 1))
            continue

        # Handle single numeric ports
        try:
            port = int(token)
        except ValueError:
            raise CheckArgError(f"Invalid port token '{token}'.")

        if port < 1 or port > 65535:
            raise CheckArgError(f"Port '{port}' is out of valid TCP range.")

        ports.append(port)

    return sorted(set(ports))

def resolve_services(service_string):
    """
    Resolve one or more service names into a list of TCP ports.
    Supports comma-delimited service names.
    Rejects numeric ports in --service.
    """
    if not service_string:
        return []

    services = [s.strip() for s in service_string.split(",") if s.strip()]
    resolved_ports = []

    for svc in services:
        # Reject numeric ports in --service
        if svc.isdigit():
            raise CheckArgError(
                f"Invalid service '{svc}'. Numeric ports belong in --ports, not --service."
            )

        ports_for_service = []

        # Primary resolution: socket.getservbyname()
        try:
            port = socket.getservbyname(svc, "tcp")
            ports_for_service.append(port)
        except OSError:
            # Fallback: manual scan of /etc/services
            try:
                with open("/etc/services", "r") as f:
                    for line in f:
                        if line.startswith("#") or not line.strip():
                            continue
                        parts = line.split()
                        if len(parts) >= 2 and parts[0] == svc:
                            port_proto = parts[1]
                            if "/tcp" in port_proto:
                                port_num = int(port_proto.split("/")[0])
                                ports_for_service.append(port_num)
            except FileNotFoundError:
                pass

        if not ports_for_service:
            raise CheckArgError(f"Service '{svc}' not found in /etc/services")

        # No printing here — PythonTools must be side-effect free
        resolved_ports.extend(ports_for_service)

    return sorted(set(resolved_ports))
