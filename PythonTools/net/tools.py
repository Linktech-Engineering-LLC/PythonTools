# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
Package: PythonTools
Author: Leon McClatchey
Company: Linktech Engineering LLC
Created: 2025-12-31
 Modified: 2026-05-30
File: PythonTools/net_tools.py
Description: Describe the purpose of this file
"""
# System Libraries
import ipaddress
import socket
import subprocess
import shlex
from typing import Optional
from types import SimpleNamespace
# Project Libraries
from ..log_helpers.factory import LoggerFactory

# Function to verify that a host exists
def host_exists(hostname: str):
    try:
        socket.gethostbyname(hostname)
        return True
    except socket.error:
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
