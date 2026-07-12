# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-12
Modified: 2026-07-12
 File: PythonTools/certs/models.py
 Version: 1.0.0
 Description: Date Class Definitions
 
"""
from typing import TypedDict, Optional, Union, List

TLS_VERSIONS = ["TLSv1", "TLSv1.1", "TLSv1.2", "TLSv1.3"]
TLS_ORDER = {
    "TLSv1": 1,
    "TLSv1.1": 2,
    "TLSv1.2": 3,
    "TLSv1.3": 4,
}
# -----------------------------
# Enforcement Results Class
# ----------------------------
class EnforcementResults(TypedDict):
    # Policy rules
    min_tls: Optional[bool]
    require_tls: Optional[bool]
    require_cipher: Optional[bool]
    forbid_cipher: Optional[bool]
    require_aead: Optional[bool]
    forbid_cbc: Optional[bool]
    forbid_rc4: Optional[bool]
    enforce_san: Optional[bool]
    issuer: Optional[bool]
    sigalg: Optional[bool]
    min_rsa: Optional[bool]
    require_curve: Optional[bool]
    require_wildcard: Optional[bool]
    forbid_wildcard: Optional[bool]
    require_ocsp: Optional[bool]
    forbid_ocsp: Optional[bool]
    ocsp_status: Optional[bool]

    # Monitoring rules
    self_signed: Optional[bool]
    chain_valid: Optional[bool]
    hostname_match: Optional[bool]
    san_present: Optional[bool]
    expiration: Optional[Union[bool, str]]  # "warning" allowed
    ocsp: Optional[bool]

    # Shared
    errors: List[str]

