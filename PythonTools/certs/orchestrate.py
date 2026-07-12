# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-12
Modified: 2026-07-12
 File: PythonTools/certs/orchestrate.py
 Version: 1.0.0
 Description: Cert Orchestration Modules
"""
import ipaddress
import socket
import ssl
from datetime import datetime, timezone
from cryptography import x509
from cryptography.hazmat.backends import default_backend

from .fetch_certs import (
    check_ocsp_reachability,
    fetch_aia_certificate,
    get_subject_cn,
    get_issuer_cn,
    get_san_list,
    get_key_info,
    get_ocsp_urls,
    get_signature_algorithm,
    is_wildcard_cert,
    parse_intermediate_cert,
)
from .classify_certs import (
    classify_chain_completeness,
    classify_key_strength,
    classify_signature_algorithm,
    classify_tls_version,
    classify_cipher,
    evaluate_tls,
    populate_errors,
    populate_warnings
)
from .status_helpers import (
    get_aia_issuer_urls,
    is_aead_cipher,
    is_cbc_cipher,
    is_rc4_cipher,
    is_self_signed
)
from .validate_certs import (
    hostname_matches,
    validate_chain
)
# -----------------------------
# Host Validation & Meta Builders
# -----------------------------
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
def build_certificate_meta(cert, chain, args):
    """
    Build a complete, deterministic metadata dictionary for check_cert.py.
    This function absorbs ALL certificate, chain, OCSP, AIA, and expiration
    processing so that main() becomes clean and minimal.
    """

    # ------------------------------------------------------------
    # 1. Expiration metadata
    # ------------------------------------------------------------
    not_after = cert.not_valid_after_utc
    # Ensure not_after is timezone-aware
    if not_after.tzinfo is None:
        not_after = not_after.replace(tzinfo=timezone.utc)
    expiration_days = (not_after - datetime.now(timezone.utc)).days    
    expiration_date = not_after.strftime("%Y-%m-%d")

    # ------------------------------------------------------------
    # 2. Subject / Issuer
    # ------------------------------------------------------------
    subject_cn = get_subject_cn(cert)
    issuer_cn = get_issuer_cn(cert)

    # ------------------------------------------------------------
    # 3. SAN + hostname matching
    # ------------------------------------------------------------
    san_list = get_san_list(cert)
    hostname_match = hostname_matches(args.host, subject_cn, san_list)

    # ------------------------------------------------------------
    # 4. Key metadata
    # ------------------------------------------------------------
    key_type, key_bits, curve = get_key_info(cert)
    key_state, key_msg = classify_key_strength(key_type, key_bits, curve)

    # ------------------------------------------------------------
    # 5. Signature algorithm + wildcard
    # ------------------------------------------------------------
    sigalg = get_signature_algorithm(cert)
    sigalg_state, sigalg_msg = classify_signature_algorithm(sigalg)
    
    wildcard = is_wildcard_cert(cert)

    # ------------------------------------------------------------
    # 6. TLS session metadata
    # ------------------------------------------------------------
    # These are fetched during socket negotiation
    tls_state, tls_version, cipher, tls_msg = fetch_tls_session_info(
        args.sni or args.host,
        args.port,
        args.timeout,
        args.insecure
    )
    v_state, v_msg = classify_tls_version(tls_version)
    c_state, c_msg = classify_cipher(cipher)
    final_tls_state, tls_messages = evaluate_tls(tls_version, cipher)

    # ------------------------------------------------------------
    # 7. OCSP metadata
    # ------------------------------------------------------------
    ocsp_urls = get_ocsp_urls(cert)
    ocsp_url = ocsp_urls[0] if ocsp_urls else None
    ocsp_status = check_ocsp_reachability(ocsp_url)
    ocsp_reachable = (ocsp_status == "reachable")

    # ------------------------------------------------------------
    # 8. AIA metadata (fetch + parse)
    # ------------------------------------------------------------
    aia_urls = get_aia_issuer_urls(cert)
    aia_chain_raw = []
    aia_chain = []

    for url in aia_urls:
        raw = fetch_aia_certificate(url)

        # Parse raw cert for chain validation
        if isinstance(raw, bytes):
            try:
                cert_obj = x509.load_der_x509_certificate(raw, default_backend())
                aia_chain_raw.append(cert_obj)
            except Exception:
                pass

        # Parse JSON-safe entry for output
        aia_chain.append(parse_intermediate_cert(url, raw))

    # ------------------------------------------------------------
    # 9. Chain validation
    # ------------------------------------------------------------
    chain_ok, chain_warnings = validate_chain(cert, aia_chain_raw)
    chain_state, chain_msg = classify_chain_completeness(
        server_sent=len(chain) > 0,
        reconstructed=chain_ok,
        valid=chain_ok,
        errors=chain_warnings
    )

    # ------------------------------------------------------------
    # 10. Warnings / Errors
    # ------------------------------------------------------------
    # Add thresholds to meta BEFORE calling populate_warnings/errors
    warning_days = args.warning
    critical_days = args.critical    

    # Build a temporary meta dict for warnings/errors
    temp_meta = {
        "expiration_days": expiration_days,
        "warning_days": warning_days,
        "critical_days": critical_days,
        "key_type": key_type,
        "rsa_bits": key_bits,
        "signature_algorithm": sigalg,
        "tls_state": tls_state,
        "tls_version": tls_version,
        "tls_msg": tls_msg,
        "cipher": cipher,
        "subject_cn": subject_cn,
        "issuer_cn": issuer_cn,
        "chain_valid": chain_ok,
    }    
    warnings = populate_warnings(temp_meta)
    errors = populate_errors(temp_meta)

    # ------------------------------------------------------------
    # 11. Final deterministic metadata dictionary
    # ------------------------------------------------------------
    return {
        # Connection
        "host": args.host,
        "port": args.port,
        "sni": args.sni or args.host,
        "timeout": args.timeout,
        "insecure": args.insecure,

        # TLS
        "tls_version": tls_version,
        "cipher": cipher,
        "tls_state": final_tls_state,
        "tls_messages": tls_messages,
        "tls_handshake_state": tls_state,
        "tls_handshake_message": tls_msg,
        "cipher_is_aead": is_aead_cipher(cipher),
        "cipher_is_cbc": is_cbc_cipher(cipher),
        "cipher_is_rc4": is_rc4_cipher(cipher),

        # Certificate
        "subject_cn": subject_cn,
        "issuer_cn": issuer_cn,
        "signature_algorithm": sigalg,
        "signature_algorithm_state": sigalg_state,
        "signature_algorithm_message": sigalg_msg,
        "wildcard": wildcard,
        "san": san_list,
        "warning_days": warning_days,
        "critical_days": critical_days,
        "expires": not_after.strftime("%Y-%m-%d %H:%M:%S"),
        "expiration_date": expiration_date,
        "expiration_days": expiration_days,
        "hostname_matches": hostname_match,
        "self_signed": is_self_signed(cert),

        # Key Metadata
        "key_type": key_type,
        "rsa_bits": key_bits,
        "ecc_curve": curve,
        "key_state": key_state,
        "key_message": key_msg,

        # AIA
        "aia_issuer_urls": aia_urls,
        "aia_chain": aia_chain,

        # OCSP
        "ocsp_urls": ocsp_urls,
        "ocsp_status": ocsp_status,
        "ocsp_reachable": ocsp_reachable,

        # Chain Validation
        "chain_present": len(chain) > 0,
        "chain_reconstructed": chain_ok,
        "chain_valid": chain_ok,
        "chain_errors": chain_warnings,
        "chain_state": chain_state,
        "chain_message": chain_msg,

        # Warnings / Errors
        "warnings": warnings,
        "errors": errors,
    }
def fetch_tls_session_info(hostname: str, port: int, timeout: int, insecure: bool):
    """
    Enhanced TLS handshake:
      - Returns (state, tls_version, cipher, message)
      - Classifies handshake failures
      - Does NOT retrieve certificates
    """

    try:
        ctx = ssl.create_default_context()

        if insecure:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

        sock = socket.create_connection((hostname, port), timeout)

        ssock = ctx.wrap_socket(sock, server_hostname=hostname)

        tls_version = ssock.version() or "unknown"

        cipher_info = ssock.cipher()
        cipher = cipher_info[0] if cipher_info else None

        ssock.close()

        return ("OK", tls_version.lower(), cipher, "TLS handshake succeeded")

    except ssl.SSLError as e:
        return ("CRITICAL", "unknown", None, f"TLS handshake failed: {e}")

    except socket.timeout:
        return ("CRITICAL", "unknown", None, "TCP timeout during handshake")

    except ConnectionRefusedError:
        return ("CRITICAL", "unknown", None, "TCP connection refused")

    except Exception as e:
        return ("UNKNOWN", "unknown", None, f"Unexpected error during handshake: {e}")

