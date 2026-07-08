# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-07-08
 File: PythonTools/nagios/banners.py
 Version: 1.0.0
 Description: Standardized start/end banners for logging.
"""


def start_banner(name: str, meta: dict) -> str:
    """
    Operator-grade START banner.
    Deterministic, grep-friendly, consistent across all tools.
    """
    parts = [f"[START] {name}"]

    # Only include fields that are meaningful for logging.
    # Deterministic ordering.
    keys = [
        "host",
        "port",
        "sni",
        "timeout",
        "insecure",
        "warning_days",
        "critical_days",
        "mode",
    ]

    for key in keys:
        if key in meta:
            parts.append(f"{key}={meta[key]}")

    return " ".join(parts)


def end_banner(name: str, state: str) -> str:
    return f"[END] check={name} state={state}"

def cert_banner(meta: dict) -> str:
    """
    Canonical CERT banner for log files.
    Deterministic, operator-grade, and consistent with JSON/verbose output.
    Enforcement fields intentionally excluded.
    """

    parts = [
        f"host={meta['host']}",
        f"port={meta['port']}",
        f"sni={meta['sni']}",

        # TLS
        f"tls_version={meta['tls_version']}",
        f"cipher={meta['cipher']}",
        f"aead={meta['cipher_is_aead']}",
        f"cbc={meta['cipher_is_cbc']}",
        f"rc4={meta['cipher_is_rc4']}",

        # Certificate
        f"subject_cn={meta['subject_cn']}",
        f"issuer_cn={meta['issuer_cn']}",
        f"sigalg={meta['signature_algorithm']}",
        f"wildcard={meta['wildcard']}",
        f"self_signed={meta['self_signed']}",
        f"hostname_matches={meta['hostname_matches']}",
        f"expires={meta['expires']}",
        f"expiration_days={meta['expiration_days']}",

        # Key
        f"key_type={meta['key_type']}",
        f"rsa_bits={meta['rsa_bits']}",
        f"ecc_curve={meta['ecc_curve']}",

        # OCSP
        f"ocsp_status={meta['ocsp_status']}",
        f"ocsp_reachable={meta['ocsp_reachable']}",

        # Chain
        f"chain_server_sent={meta['chain_present']}",
        f"chain_reconstructed={meta['chain_reconstructed']}",
        f"chain_valid={meta['chain_valid']}",
        f"chain_errors={len(meta['chain_errors'])}",
    ]

    return "[CERT] " + " ".join(parts)

def result_banner(state: str, failures: list) -> str:
    """
    Operator-grade RESULT banner for log files.
    Deterministic and grep-friendly.
    """
    return (
        f"[RESULT] state={state}"
        f" failed={len(failures)}"
        f" failures={failures}"
    )
