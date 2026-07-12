# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-12
Modified: 2026-07-12
 File: PythonTools/certs/status_helpers.py
 Version: 1.0.0
 Description: Status Helper Modules
"""
from cryptography.x509.oid import ExtensionOID
from typing import Optional
from .status_helpers import TLS_ORDER
# -----------------------------
#  Status Dispatcher + Perfdata
# -----------------------------
def is_aead_cipher(cipher: Optional[str]) -> bool:
    if not cipher:
        return False
    return cipher.startswith("TLS_") and ("GCM" in cipher or "CHACHA20" in cipher)
def is_cbc_cipher(cipher: Optional[str]) -> bool:
    if not cipher:
        return False
    return "CBC" in cipher
def is_rc4_cipher(cipher: Optional[str]) -> bool:
    if not cipher:
        return False
    return "RC4" in cipher
def is_self_signed(cert):
    return cert.issuer == cert.subject
def get_aia_issuer_urls(cert):
    try:
        aia = cert.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
        urls = []
        for desc in aia.value:
            if desc.access_method.dotted_string == "1.3.6.1.5.5.7.48.2":  # caIssuers
                urls.append(desc.access_location.value)
        return urls
    except Exception:
        return []
def tls_version_rank(version: str):
    return TLS_ORDER.get(version, 0)

