# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-12
Modified: 2026-07-12
 File: PythonTools/certs/validate_certs.py
 Version: 1.0.0
 Description: Certificate Validation Modules
"""
from typing import List, Tuple
from cryptography import x509

def hostname_matches(host: str, cn: str, san: List[str]) -> bool:
    host = host.lower()

    # SAN takes precedence
    for entry in san:
        if entry.lower() == host:
            return True

        # wildcard match
        if entry.startswith("*.") and host.endswith(entry[1:].lower()):
            return True

    # fallback to CN
    return cn.lower() == host
def validate_chain(cert: x509.Certificate, chain: List[x509.Certificate]) -> Tuple[bool, List[str]]:
    """
    Validates certificate chain structure.
    Returns (chain_ok, warnings).
    """
    warnings = []

    # Case 1: Self-signed certificate
    if cert.issuer == cert.subject:
        warnings.append("self_signed")
        return (False, warnings)

    # Case 2: No intermediates provided
    if not chain:
        warnings.append("missing_intermediate")
        return (False, warnings)

    # Case 3: Check ordering and issuer/subject linkage
    full_chain = [cert] + chain
    for i in range(len(full_chain) - 1):
        child = full_chain[i]
        parent = full_chain[i + 1]

        if child.issuer != parent.subject:
            warnings.append("issuer_mismatch")

    # Case 4: If chain is out of order
    # (simple heuristic: if issuer of leaf matches neither subject of first intermediate nor leaf itself)
    if cert.issuer != chain[0].subject:
        warnings.append("chain_out_of_order")

    chain_ok = len(warnings) == 0
    return (chain_ok, warnings)
