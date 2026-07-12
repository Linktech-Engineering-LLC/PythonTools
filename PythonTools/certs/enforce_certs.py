# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-12
Modified: 2026-07-12
 File: PythonTools/certs/enforce_certs.py
 Version: 1.0.0
 Description: Certificate Enforcement Modules
"""
from typing import Dict, List, cast


from .models import EnforcementResults
from .status_helpers import tls_version_rank

def empty_enforcement_results() -> EnforcementResults:
    return {
        "min_tls": None,
        "require_tls": None,
        "require_cipher": None,
        "forbid_cipher": None,
        "require_aead": None,
        "forbid_cbc": None,
        "forbid_rc4": None,
        "enforce_san": None,
        "issuer": None,
        "sigalg": None,
        "min_rsa": None,
        "require_curve": None,
        "require_wildcard": None,
        "forbid_wildcard": None,
        "require_ocsp": None,
        "forbid_ocsp": None,
        "ocsp_status": None,

        "self_signed": None,
        "chain_valid": None,
        "hostname_match": None,
        "san_present": None,
        "expiration": None,
        "ocsp": None,

        "errors": [],
    }
def run_enforcement_checks(args, meta) -> EnforcementResults:
    """
    Evaluate all enforcement rules and return raw results.
    meta = extracted certificate metadata.
    """

    results = empty_enforcement_results()

    # --- TLS Requirements ---
    results["min_tls"] = (
        None if not args.min_tls
        else tls_version_rank(meta["tls_version"]) >= tls_version_rank(args.min_tls)
    )

    results["require_tls"] = (
        None if not args.require_tls
        else meta["tls_version"] == args.require_tls
    )

    results["require_cipher"] = (
        None if not args.require_cipher
        else meta["cipher"] == args.require_cipher
    )

    results["forbid_cipher"] = (
        None if not args.forbid_cipher
        else meta["cipher"] != args.forbid_cipher
    )

    results["require_aead"] = (
        None if not args.require_aead
        else meta["cipher_is_aead"]
    )

    results["forbid_cbc"] = (
        None if not args.forbid_cbc
        else not meta["cipher_is_cbc"]
    )

    results["forbid_rc4"] = (
        None if not args.forbid_rc4
        else not meta["cipher_is_rc4"]
    )

    # --- Certificate Requirements ---
    results["enforce_san"] = (
        None if not args.enforce_san
        else meta["hostname_in_san"]
    )

    results["issuer"] = (
        None if not args.issuer
        else args.issuer.lower() in meta["issuer_cn"].lower()
    )

    results["sigalg"] = (
        None if not args.sigalg
        else meta["signature_algorithm"].lower() == args.sigalg.lower()
    )

    results["min_rsa"] = (
        None if not args.min_rsa
        else (meta["key_type"] == "rsa" and meta["rsa_bits"] >= args.min_rsa)
    )

    results["require_curve"] = (
        None if not args.require_curve
        else (meta["key_type"] == "ecdsa" and meta["ecc_curve"] == args.require_curve)
    )

    results["require_wildcard"] = (
        None if not args.require_wildcard
        else meta["wildcard"]
    )

    results["forbid_wildcard"] = (
        None if not args.forbid_wildcard
        else not meta["wildcard"]
    )

    # --- OCSP Requirements ---
    results["require_ocsp"] = (
        None if not args.require_ocsp
        else meta["ocsp_reachable"]
    )

    results["forbid_ocsp"] = (
        None if not args.forbid_ocsp
        else not meta["ocsp_reachable"]
    )

    results["ocsp_status"] = (
        None if not args.ocsp_status
        else meta["ocsp_status"] == args.ocsp_status
    )

    return results
def run_monitoring_checks(args, meta) -> EnforcementResults:
    results = empty_enforcement_results()

    if args.check_self_signed:
        results["self_signed"] = not meta["self_signed"]

    if args.check_chain:
        results["chain_valid"] = meta["chain_valid"]

    if args.check_hostname:
        results["hostname_match"] = meta["hostname_matches"]

    if args.check_san:
        results["san_present"] = len(meta["san"]) > 0

    if args.check_expiration:
        if meta["expiration_days"] < args.critical:
            results["expiration"] = False
        elif meta["expiration_days"] < args.warning:
            results["expiration"] = "warning"
        else:
            results["expiration"] = True

    if args.check_ocsp:
        results["ocsp"] = meta["ocsp_reachable"]

    return results
def merge_enforcement(
    policy: EnforcementResults,
    monitoring: EnforcementResults
) -> Dict[str, List[str]]:
    """
    Merge policy enforcement results and monitoring enforcement results
    into a unified enforcement block.

    Output schema:
        {
            "applied": [str],
            "passed": [str],
            "failed": [str],
            "errors": [str]
        }
    """

    enf = {
        "applied": [],
        "passed": [],
        "failed": [],
        "errors": []
    }

    # ------------------------------------------------------------
    # Merge Policy Rules
    # ------------------------------------------------------------
    for rule, outcome in policy.items():

        # Special case: errors list
        if rule == "errors":
            enf["errors"].extend(cast(List[str], outcome))
            continue

        # Skip rules that were not applied
        if outcome is None:
            continue

        enf["applied"].append(rule)

        # Boolean outcomes
        if outcome is True:
            enf["passed"].append(rule)
        elif outcome is False:
            enf["failed"].append(rule)

        # Warning outcomes (string)
        elif isinstance(outcome, str) and outcome == "warning":
            enf["failed"].append(f"{rule}_warning")

    # ------------------------------------------------------------
    # Merge Monitoring Rules
    # ------------------------------------------------------------
    for rule, outcome in monitoring.items():

        # Special case: errors list
        if rule == "errors":
            enf["errors"].extend(cast(List[str], outcome))
            continue

        if outcome is None:
            continue

        enf["applied"].append(rule)

        if outcome is True:
            enf["passed"].append(rule)
        elif outcome is False:
            enf["failed"].append(rule)
        elif isinstance(outcome, str) and outcome == "warning":
            enf["failed"].append(f"{rule}_warning")

    return enf
def build_enforcement_dict(args, results) -> Dict:
    """
    Build a deterministic enforcement dictionary for verbose, JSON, and Nagios modes.

    `args`    = argparse Namespace
    `results` = dict of individual enforcement check results, e.g.:
        {
            "min_tls": True/False/None,
            "require_tls": True/False/None,
            "require_cipher": True/False/None,
            "forbid_cipher": True/False/None,
            "require_aead": True/False/None,
            "forbid_cbc": True/False/None,
            "forbid_rc4": True/False/None,
            "enforce_san": True/False/None,
            "issuer": True/False/None,
            "sigalg": True/False/None,
            "min_rsa": True/False/None,
            "require_curve": True/False/None,
            "require_wildcard": True/False/None,
            "forbid_wildcard": True/False/None,
            "require_ocsp": True/False/None,
            "forbid_ocsp": True/False/None,
            "ocsp_status": True/False/None,
            "errors": [ ... ]
        }
    """

    applied = []
    passed = []
    failed = []
    errors = []

    # Map CLI flags to human-readable rule names
    rule_map = {
        "min_tls":          args.min_tls,
        "require_tls":      args.require_tls,
        "require_cipher":   args.require_cipher,
        "forbid_cipher":    args.forbid_cipher,
        "require_aead":     args.require_aead,
        "forbid_cbc":       args.forbid_cbc,
        "forbid_rc4":       args.forbid_rc4,
        "enforce_san":      args.enforce_san,
        "issuer":           args.issuer,
        "sigalg":           args.sigalg,
        "min_rsa":          args.min_rsa,
        "require_curve":    args.require_curve,
        "require_wildcard": args.require_wildcard,
        "forbid_wildcard":  args.forbid_wildcard,
        "require_ocsp":     args.require_ocsp,
        "forbid_ocsp":      args.forbid_ocsp,
        "ocsp_status":      args.ocsp_status,
    }

    # Build applied/passed/failed lists
    for rule, value in rule_map.items():
        if value is None or value is False:
            continue  # rule not requested

        applied.append(f"{rule}={value}" if value not in (True, False) else rule)

        result = results.get(rule)
        if result is True:
            passed.append(f"{rule}={value}" if value not in (True, False) else rule)
        elif result is False:
            failed.append(f"{rule}={value}" if value not in (True, False) else rule)

    # Collect enforcement errors
    if "errors" in results and results["errors"]:
        errors.extend(results["errors"])

    return {
        "applied": applied,
        "passed": passed,
        "failed": failed,
        "errors": errors,
    }

