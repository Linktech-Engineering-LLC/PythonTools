# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-12
Modified: 2026-07-12
 File: PythonTools/certs/classify_certs.py
 Version: 1.0.0
 Description: Certificate Classification Modules
"""
from typing import Tuple, Optional

# --------------------------------------
#  Classification/Enforcement/Validation
# --------------------------------------
def classify_tls_version(tls_version: str) -> Tuple[str, str]:
    """
    Returns (state, message) based on TLS version strength.
    """
    if tls_version == "tlsv1.3":
        return ("OK", "TLS 1.3 negotiated")
    if tls_version == "tlsv1.2":
        return ("WARNING", "TLS 1.2 negotiated (consider upgrading)")
    if tls_version in ("tlsv1.1", "tlsv1"):
        return ("CRITICAL", f"Weak TLS version negotiated: {tls_version}")
    return ("UNKNOWN", f"Unknown or unsupported TLS version: {tls_version}")
def classify_cipher(cipher: Optional[str]) -> Tuple[str, str]:
    if cipher is None:
        return ("UNKNOWN", "No cipher negotiated")

    c = cipher.lower()

    # Strong AEAD ciphers
    if "gcm" in c or "chacha20" in c:
        return ("OK", f"Strong cipher negotiated: {cipher}")

    # CBC is acceptable but not ideal
    if "cbc" in c:
        return ("WARNING", f"Weak cipher mode (CBC) negotiated: {cipher}")

    # Known bad ciphers
    if any(x in c for x in ("rc4", "3des", "null", "export")):
        return ("CRITICAL", f"Insecure cipher negotiated: {cipher}")

    # Default fallback
    return ("WARNING", f"Unclassified cipher: {cipher}")
def evaluate_tls(tls_version: str, cipher: Optional[str]):
    v_state, v_msg = classify_tls_version(tls_version)
    c_state, c_msg = classify_cipher(cipher)

    # Highest severity wins
    final_state = max((v_state, c_state), key=lambda s: ["OK","WARNING","CRITICAL","UNKNOWN"].index(s))

    return final_state, [v_msg, c_msg]
def classify_signature_algorithm(sigalg: str):
    """
    Classify certificate signature algorithm strength.

    Returns:
        (state, message)
        state ∈ {"OK", "WARNING", "CRITICAL", "UNKNOWN"}
    """

    if not sigalg:
        return ("UNKNOWN", "Signature algorithm missing or unrecognized")

    algo = sigalg.lower().strip()

    # Strong algorithms
    if algo in ("sha256", "sha384", "sha512"):
        return ("OK", f"Strong signature algorithm: {algo}")

    # RSA-PSS variants (strong)
    if "pss" in algo:
        return ("OK", f"Strong RSA-PSS signature algorithm: {algo}")

    # Weak / deprecated algorithms
    if algo in ("sha1", "sha1withrsa", "sha1withrsaencryption"):
        return ("CRITICAL", f"Weak signature algorithm (SHA‑1): {algo}")

    if algo in ("md5", "md5withrsa", "md5withrsaencryption"):
        return ("CRITICAL", f"Broken signature algorithm (MD5): {algo}")

    # Unknown or unusual algorithms
    return ("WARNING", f"Unrecognized signature algorithm: {algo}")
def classify_key_strength(key_type: str, rsa_bits: int | None, ecc_curve: str | None):
    """
    Classify certificate key strength.

    Returns:
        (state, message)
        state ∈ {"OK", "WARNING", "CRITICAL", "UNKNOWN"}
    """

    # Normalize
    kt = (key_type or "").lower().strip()

    # ------------------------------------------------------------
    # RSA classification
    # ------------------------------------------------------------
    if kt == "rsa":
        if rsa_bits is None:
            return ("UNKNOWN", "RSA key size missing or unrecognized")

        if rsa_bits < 2048:
            return ("CRITICAL", f"Weak RSA key size: {rsa_bits} bits")

        if rsa_bits == 2048:
            return ("OK", "RSA 2048-bit key (minimum recommended strength)")

        if rsa_bits in (3072, 4096):
            return ("OK", f"Strong RSA key: {rsa_bits} bits")

        if rsa_bits > 4096:
            return ("OK", f"Very strong RSA key: {rsa_bits} bits")

        return ("WARNING", f"Unusual RSA key size: {rsa_bits} bits")

    # ------------------------------------------------------------
    # ECDSA classification
    # ------------------------------------------------------------
    if kt == "ecdsa":
        if not ecc_curve:
            return ("UNKNOWN", "ECDSA curve missing or unrecognized")

        curve = ecc_curve.lower().strip()

        if curve in ("secp256r1", "prime256v1"):
            return ("OK", "Strong ECDSA curve: secp256r1")

        if curve == "secp384r1":
            return ("OK", "Strong ECDSA curve: secp384r1")

        # Other curves: not necessarily bad, but uncommon
        return ("WARNING", f"Unrecognized or uncommon ECDSA curve: {curve}")

    # ------------------------------------------------------------
    # EdDSA classification
    # ------------------------------------------------------------
    if kt in ("ed25519", "ed448"):
        return ("OK", f"Strong EdDSA key: {kt}")

    # ------------------------------------------------------------
    # Unknown key type
    # ------------------------------------------------------------
    if not kt:
        return ("UNKNOWN", "Key type missing or unrecognized")

    return ("WARNING", f"Unrecognized key type: {kt}")
def classify_chain_completeness(server_sent: bool, reconstructed: bool, valid: bool, errors: list):
    """
    Classify certificate chain completeness and trustworthiness.

    Returns:
        (state, message)
        state ∈ {"OK", "WARNING", "CRITICAL", "UNKNOWN"}
    """

    # Unknown / missing data
    if valid is None:
        return ("UNKNOWN", "Chain validation state missing or unrecognized")

    # Critical failures
    if not valid:
        return ("CRITICAL", "Certificate chain is invalid")

    if errors:
        return ("CRITICAL", f"Chain validation errors present: {len(errors)} error(s)")

    # Valid chain but server did not send intermediates
    if valid and not server_sent and reconstructed:
        return ("WARNING", "Chain reconstructed via AIA (server did not send intermediates)")

    # Valid chain fully provided by server
    if valid and server_sent:
        return ("OK", "Complete certificate chain provided by server")

    # Valid chain reconstructed but server_sent flag unknown
    if valid and reconstructed:
        return ("WARNING", "Chain reconstructed via AIA")

    # Fallback
    return ("UNKNOWN", "Chain completeness could not be determined")
# -----------------------------
# Populate Warnings/Errors
# -----------------------------
def populate_warnings(meta):
    warnings = []

    # 1. Expiration approaching
    if meta["expiration_days"] <= meta["warning_days"]:
        warnings.append("expiration_warning")

    # 2. Weak RSA key
    if meta["key_type"] == "rsa" and meta["rsa_bits"]:
        if meta["rsa_bits"] < 2048:
            warnings.append("weak_rsa_key")

    # 3. Weak signature algorithm
    if meta["signature_algorithm"] in ("md5", "sha1"):
        warnings.append("weak_signature_algorithm")

    return warnings
def populate_errors(meta):
    errors = []

    # 1. TLS handshake failure
    # If TLS version or cipher is missing, handshake failed.
    if meta.get("tls_version") is None or meta.get("cipher") is None:
        errors.append("tls_handshake_failed")

    # 2. Certificate presence
    # If subject or issuer is missing, no certificate was parsed.
    if meta.get("subject_cn") is None or meta.get("issuer_cn") is None:
        errors.append("no_certificate_present")

    # 3. Chain validation
    # If chain_valid is False, chain is invalid.
    if meta.get("chain_valid") is False:
        errors.append("chain_invalid")

    return errors

