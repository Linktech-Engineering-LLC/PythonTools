# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
Package: PythonTools
Author: Leon McClatchey
Company: Linktech Engineering LLC
Created: 2025-12-31
 Modified: 2026-07-16
File: PythonTools/net/tools.py
Description: Describe the purpose of this file
"""
# System Libraries
import os
import errno
import ipaddress
import psutil
import re
import socket
import subprocess
import shlex
from typing import Optional
from types import SimpleNamespace
# Project Libraries

VIRTUAL_PREFIXES = (
    "vnet", "virbr", "docker", "br-", "tap", "tun", "veth"
)

def apply_iface_selection(interfaces, ifaces_arg) -> tuple:
    """
    Selects interfaces based on --ifaces.
    Supports:
      • comma-delimited lists
      • regex patterns
      • literal matches
    If --ifaces is None → return all interfaces, no unmatched.

    Returns:
        (selected_dict, unmatched_list)
    """

    # No selection → return everything
    if not ifaces_arg:
        return interfaces, []

    selected = {}
    patterns = [p.strip() for p in ifaces_arg.split(",") if p.strip()]
    matched_patterns = set()

    for name, iface in interfaces.items():
        lname = name.lower()

        for p in patterns:
            # Literal match
            if lname == p.lower():
                selected[name] = iface
                matched_patterns.add(p)
                break

            # Substring match
            if p.lower() in lname:
                selected[name] = iface
                matched_patterns.add(p)
                break

            # Regex match
            try:
                if re.search(p, name, re.IGNORECASE):
                    selected[name] = iface
                    matched_patterns.add(p)
                    break
            except re.error:
                # Invalid regex → ignore and fall back to substring only
                pass

    unmatched = [p for p in patterns if p not in matched_patterns]
    return selected, unmatched
def decode_mac(raw):
    """
    Convert raw SNMP MAC strings (unicode escapes, bytes, hex, or ASCII)
    into human-readable MAC addresses. If the value cannot be interpreted
    as exactly 6 bytes, return it unchanged.
    """

    # Case 1: Already colon-formatted
    if isinstance(raw, str) and ":" in raw:
        return raw.lower()

    # Case 2: Dash-formatted ASCII (00-11-22-33-44-55)
    if isinstance(raw, str) and "-" in raw:
        parts = raw.split("-")
        if len(parts) == 6 and all(len(p) == 2 for p in parts):
            return ":".join(p.lower() for p in parts)
        return raw

    # Case 3: Hex string like "0x001122334455"
    if isinstance(raw, str) and raw.startswith("0x"):
        hexstr = raw[2:]
        if len(hexstr) == 12:
            return ":".join(hexstr[i:i+2] for i in range(0, 12, 2)).lower()
        return raw

    # Case 4: Raw bytes
    if isinstance(raw, (bytes, bytearray)):
        if len(raw) == 6:
            return ":".join(f"{b:02x}" for b in raw)
        return raw

    # Case 5: Unicode escape string (SNMP OCTET STRING)
    if isinstance(raw, str):
        try:
            b = raw.encode("latin-1")
            if len(b) == 6:
                return ":".join(f"{byte:02x}" for byte in b)
            return raw
        except Exception:
            return raw

    return raw
def evaluate_status(interfaces, status_target, unmatched=None) -> dict:
    """
    Evaluates the selected interfaces based on the --status target.
    Injects unmatched --ifaces patterns as CRITICAL failures.
    Returns a dict:
        {
            "state": "OK" | "WARNING" | "CRITICAL",
            "failures": [iface names],
            "results": { iface: { "ok": bool, "value": X } }
        }
    """

    if not status_target:
        status_target = "oper-status"

    results = {}
    failures = []

    for name, iface in interfaces.items():

        if status_target == "oper-status":
            ok = iface.get("oper_up", False)
            value = "up" if ok else "down"

        elif status_target == "admin-status":
            ok = iface.get("admin_up", False)
            value = "up" if ok else "down"

        elif status_target == "linkspeed":
            speed = iface.get("speed")
            ok = speed not in (None, 0)
            value = speed

        elif status_target == "duplex":
            if iface.get("name").startswith("br"):
                ok = True
                value = "n/a"
            else:
                ok = iface.get("duplex") == "full"
                value = iface.get("duplex")

        elif status_target == "mtu":
            mtu = iface.get("mtu")
            ok = mtu is not None and mtu > 0
            value = mtu

        elif status_target == "alias":
            ok = not is_alias(name)
            value = "alias" if not ok else "normal"

        else:
            ok = True
            value = None

        results[name] = {
            "ok": ok,
            "value": value
        }

        if not ok:
            failures.append(name)

    # Inject unmatched --ifaces patterns as CRITICAL failures
    if unmatched:
        for name in unmatched:
            results[name] = {"ok": False, "value": "not found"}
            failures.append(name)

    # Determine overall state
    if failures:
        state = "CRITICAL"
    else:
        state = "OK"

    return {
        "state": state,
        "failures": failures,
        "results": results
    }
# Function to verify that a host exists
def host_exists(hostname: str):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.error:
        return False
def is_alias(name):
    return ":" in name
# Function to determine if an address is external
def is_external_ip(ip: str, exc: list[str], verbose: bool = False) -> bool:
    try:
        addr = ipaddress.ip_address(ip)
        if verbose:
            print(f"[CHECK] IP: {addr}")
        # reject internal addresses
        if addr.is_private or addr.is_loopback or addr.is_link_local:
            if verbose:
                print(f"[SKIP] {addr} is internal (private/loopback/link-local)")
            return False
        # Check against excluded subnets
        for subnet in exc:
            try:
                net = ipaddress.ip_network(subnet, strict=False)
                if addr in net:
                    if verbose:
                        print(f"[SKIP] {addr} is in excluded subnet {net}")
                    return False
            except ValueError:
                if verbose:
                    print(f"[WARN] Invalid subnet: {subnet}")
                continue
        return True
    except ValueError:
        if verbose:
            print(f"[ERROR] Invalid IP: {ip}")
        return False
# Function to determine if the host is an address or a string
def is_ip_address(host: str):
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False
# Function to determine if subnet is a valid subnet
def is_valid_subnet(subnet_str: str) -> bool:
    try:
        if "/" not in subnet_str:
            return False
        ipaddress.ip_network(subnet_str, strict=False)
        return True
    except ValueError:
        return False
# Function to determine if the host is the localhost
def isLocalHost(host: str):
    return (
        True
        if host.lower() == "localhost" or host.lower() == socket.gethostname().lower()
        else False
    )
def is_local(name, iface):
    # Loopback interface
    if name == "lo":
        return True

    # Loopback aliases (rare but possible)
    if name.startswith("lo:"):
        return True

    # IPv4 loopback addresses
    for ip in iface.get("ipv4", []):
        if ip["address"].startswith("127."):
            return True

    return False
def is_virtual(name):
    return name.startswith(VIRTUAL_PREFIXES)
# Runs a command on the local machine
def local_command(cmd: str, raise_on_error: bool = False, logger=None):
    try:
        if logger:
            logger.command_start(cmd)

        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)

        if logger:
            logger.command_end(cmd, proc.returncode)

        if proc.returncode != 0:
            if logger:
                logger.command_error("local_command", RuntimeError(proc.stderr.strip()))
            if raise_on_error:
                raise RuntimeError(proc.stderr.strip())

        return proc.stdout.strip(), proc.returncode, proc.stderr.strip()

    except Exception as error:
        if logger:
            logger.command_error("local_command", error)
        if raise_on_error:
            raise RuntimeError(str(error))
        return "", 1, str(error)
# Function to determine if a pid is running/valid
def pid_is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except OSError as e:
        if e.errno == errno.ESRCH:
            return False   # No such process
        if e.errno == errno.EPERM:
            return True    # Process exists, but no permission
        raise
    else:
        return True
def run_with_error_handling(cmd: str, sudo_password: Optional[str], raise_on_error: bool = True, **kwargs):
    """
    Wrapper around sudo_run that always passes raise_on_error explicitly.
    Ensures audit-friendly error handling across all modules.
    """
    return sudo_run(cmd, sudo_password=sudo_password, raise_on_error=raise_on_error, **kwargs)
# Sudo Command Function
def sudo_run(
    cmd: str,
    sudo_password: Optional[str],
    raise_on_error: bool = False,
    logger=None
):
    # Always define these so Pylance is satisfied
    raw_cmd: str = ""
    args: list[str] = []
    cmd_list: list[str] = []
    result_obj: Optional[SimpleNamespace] = None

    # Root mode (no sudo)
    if sudo_password is None:
        out, code, err = local_command(cmd, logger=logger)
        return SimpleNamespace(
            msg=out,
            code=code,
            err=err,
            stdout=out,
            stderr=err,
            returncode=code,
            as_tuple=(out, code, err)
        )

    # Normalize command into raw_cmd + args
    if isinstance(cmd, str):
        raw_cmd = cmd
        if any(op in cmd for op in ["&&", "||", "|", ";", ">", "<"]):
            args = ["sh", "-c", cmd]
        else:
            args = shlex.split(cmd)

    elif isinstance(cmd, list):
        raw_cmd = " ".join(cmd)
        args = cmd

    else:
        raise TypeError("cmd must be str or list")

    # Build sudo command list
    cmd_list = ["sudo", "-S"] + args

    try:
        if logger:
            logger.command_start(f"sudo_run raw: {raw_cmd}, sudo_run args: {args}")

        result = subprocess.run(
            cmd_list,
            capture_output=True,
            text=True,
            input=f"{sudo_password}\n",
            check=True
        )

        result_obj = SimpleNamespace(
            msg=result.stdout,
            code=result.returncode,
            err=result.stderr,
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode,
            as_tuple=(result.stdout, result.returncode, result.stderr)
        )

    except subprocess.CalledProcessError as e:
        result_obj = SimpleNamespace(
            msg=e.stdout,
            code=e.returncode,
            err=e.stderr,
            stdout=e.stdout,
            stderr=e.stderr,
            returncode=e.returncode,
            as_tuple=(e.stdout, e.returncode, e.stderr)
        )

    finally:
        if logger and result_obj is not None:
            logger.command_end("sudo_run finished", result_obj.code)

    return result_obj
def validate_host_basic(host: str):
    """
    Deterministic hostname validation used by all NMS_Tools plugins.

    Rules:
      • If the user supplies an IP → treat it as authoritative (no reverse DNS).
      • If the user supplies the system hostname → resolve it once.
      • Otherwise → attempt forward resolution only.
      • Never perform reverse lookups.
      • Never replace an IP with a hostname.
      • All failures return UNKNOWN-level errors (caller decides exit).

    Returns:
        {
            "ok": bool,
            "ip": str or None,
            "error": str or None
        }
    """

    host = host.strip()

    # ------------------------------------------------------------
    # 1. IP address case (authoritative)
    # ------------------------------------------------------------
    try:
        ip_obj = ipaddress.ip_address(host)
        return {
            "ok": True,
            "ip": str(ip_obj),   # return IP exactly as supplied
            "error": None
        }
    except ValueError:
        pass  # Not an IP, continue

    # ------------------------------------------------------------
    # 2. Local hostname case (special deterministic rule)
    # ------------------------------------------------------------
    system_hostname = socket.gethostname()

    if host.lower() == system_hostname.lower():
        try:
            resolved = socket.gethostbyname(system_hostname)
            return {
                "ok": True,
                "ip": resolved,
                "error": None
            }
        except Exception:
            return {
                "ok": False,
                "ip": None,
                "error": (
                    f"Hostname '{host}' matches local hostname but "
                    f"cannot be resolved by the system resolver"
                )
            }

    # ------------------------------------------------------------
    # 3. Normal hostname → forward resolution only
    # ------------------------------------------------------------
    try:
        resolved = socket.gethostbyname(host)
        return {
            "ok": True,
            "ip": resolved,
            "error": None
        }
    except Exception:
        return {
            "ok": False,
            "ip": None,
            "error": f"Hostname resolution failed for '{host}'"
        }
def validate_host_local(host: str):
    """
    Determines whether the supplied host is:
      • invalid (UNKNOWN)
      • local (local mode)
      • remote (SNMP mode)

    Returns:
        {
            "ok": bool,
            "local": bool,
            "ip": str or None,
            "error": str or None
        }
    """

    # Step 1: Basic validation (shared logic)
    rc = validate_host_basic(host)
    if not rc["ok"]:
        return {
            "ok": False,
            "local": False,
            "ip": None,
            "error": rc["error"]
        }

    target_ip = rc["ip"]

    # Step 2: Enumerate local interface IPs
    local_ips = set()
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family in (socket.AF_INET, socket.AF_INET6):
                local_ips.add(addr.address)
    # Step 3: Compare
    if target_ip in local_ips:
        return {
            "ok": True,
            "local": True,
            "ip": target_ip,
            "error": None
        }

    # Not local → remote SNMP mode
    return {
        "ok": True,
        "local": False,
        "ip": target_ip,
        "error": None
    }
