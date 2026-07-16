# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-06-17
 Modified: 2026-07-15
 File: PythonTools/nagios/banners.py
 Version: 1.0.0
 Description: Standardized start/end banners for logging.
"""

SAFE_START_KEYS = [
    "host",
    "url",
    "port",
    "timeout",
    "https",
    "max_redirects",
    "expect_status",
    "expect_family",
    "sni",
    "insecure",
    "mode",
    "status_target",
    "include_aliases",
    "exclude_local",
    "ignore",
]

def start_banner(name: str, meta: dict) -> str:
    parts = [f"[START] {name}"]

    for key in SAFE_START_KEYS:
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
def html_banner(meta: dict, result: dict) -> str:
    """
    HTML operator-grade banner.
    Deterministic, grep-friendly, aligned with PythonTools.nagios.
    Equivalent to cert_banner() in check_cert.
    """

    cap = result["capture"]
    backend = result["backend"]
    backend_check = result["backend_check"]
    ct = result["content_type_check"]
    html = result["html_check"]
    status = result["status_check"]
    perf = meta.get("perfdata", {})

    parts = [
        f"url={meta.get('url', meta['host'])}",

        # HTTP status
        f"status={cap['status']}",
        f"status_ok={status['status'] == 0}",
        f"latency_ms={cap['response_time'] * 1000 if cap['response_time'] else None}",

        # Content-Type
        f"content_type={cap['content_type']}",
        f"content_type_ok={ct['status'] == 0}",

        # HTML checks
        f"text_present={html['status'] == 0}",
        f"regex_match={html['status'] == 0}",

        # Backend
        f"backend={backend['detected']}",
        f"backend_ok={backend_check['status'] == 0}",

        # Size
        f"size={len(cap['body']) if cap['body'] else None}",
        f"size_ok={ct['status'] == 0}",

        # Redirects
        f"redirects={cap['redirects']}",
        f"redirect_ok={status['status'] == 0}",

        # Security
        f"https_used={not cap['tls_error']}",
        f"hsts={'strict-transport-security' in (cap['headers'] or {})}",

        # Errors (same pattern as cert_banner)
        f"errors={sum(1 for section in ['backend_check','content_type_check','html_check','status_check']
                      if result[section]['status'] != 0)}",
    ]

    # Perfdata (flattened)
    if perf:
        parts.extend([
            f"perf_latency={perf.get('latency')}",
            f"perf_size={perf.get('size')}",
            f"perf_warn_rt={perf.get('warning_rt')}",
            f"perf_crit_rt={perf.get('critical_rt')}",
            f"perf_warn_size={perf.get('warning_size')}",
            f"perf_crit_size={perf.get('critical_size')}",
        ])

    return "[HTML] " + " ".join(parts)

def result_banner(state: str, failures: list, perfdata=None) -> str:
    """
    Operator-grade RESULT banner for log files.
    Deterministic and grep-friendly.
    """
    base = f"[RESULT] state={state} failures={len(failures)}"

    if perfdata:
        return f"[PERFDATA] {base} perfdata=\"{perfdata}\""

    return base

def _fmt(value):
    """Normalize values for logging."""
    if value is None:
        return "None"
    if isinstance(value, (list, tuple)):
        return ",".join(str(v) for v in value)
    if isinstance(value, dict):
        return ",".join(f"{k}:{v}" for k, v in value.items())
    if isinstance(value, bytes):
        return value.hex()
    return str(value)

def log_interface(iface_name, iface_meta, iface_result):
    parts = [f"[IFACE] {iface_name}"]

    for key, value in sorted(iface_meta.items()):
        parts.append(f"{key}={_fmt(value)}")

    parts.append(f"ok={iface_result.get('ok')}")
    parts.append(f"value={_fmt(iface_result.get('value'))}")

    return " ".join(parts)
