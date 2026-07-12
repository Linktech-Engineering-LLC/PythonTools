# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-12
Modified: 2026-07-12
 File: PythonTools/certs/fetch_certs.py
 Version: 1.0.0
 Description: Fetches and parses certificates
"""
import ssl
import socket

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, ed448
from cryptography.x509.oid import ExtensionOID, NameOID, AuthorityInformationAccessOID
from cryptography.x509.ocsp import load_der_ocsp_response  # optional, see OCSP stub
from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, ed448
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple, Optional, List, Union, cast, Dict
from typing_extensions import TypedDict
from urllib import request, error, parse
# -----------------------------
#  Certificate Fetch/Parse
# -----------------------------
def fetch_certificate_and_socket(hostname: str, port: int = 443, timeout: int = 10, insecure: bool = False):
    """Perform TLS handshake using stdlib ssl and return:
       - leaf certificate (cryptography.x509)
       - empty chain (list)
       - ocsp_resp = None (OCSP unsupported)
       - TLS info (version, cipher)
    """
    try:
        if insecure:
            ctx = ssl._create_unverified_context()
        else:
            ctx = ssl.create_default_context()

        # If insecure, hostname checking is already disabled
        # If secure, we want hostname checking ON
        if insecure:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
        sock = socket.create_connection((hostname, port), timeout)
        ssock = ctx.wrap_socket(sock, server_hostname=hostname)

        der = ssock.getpeercert(binary_form=True)
        if der is None:
            raise RuntimeError("No certificate received from peer")

        pem = ssl.DER_cert_to_PEM_cert(der)
        cert = x509.load_pem_x509_certificate(pem.encode(), default_backend())

        tls_version, cipher = get_tls_info(ssock)
        cipher_info = ssock.cipher()
        cipher = cipher_info[0] if cipher_info is not None else None

        ocsp_resp = None
        chain = []  # stdlib doesn't expose full chain cleanly

        return cert, chain, tls_version, cipher
    except Exception as e:
        raise RuntimeError(f"TLS handshake or certificate retrieval failed: {e}")
def fetch_aia_certificate(url, timeout=5):
    """
    Fetch an intermediate certificate from an AIA URL.
    Returns raw certificate bytes (DER or PEM).
    Returns None on failure.
    """

    # Deterministic user-agent
    headers = {
        "User-Agent": "NMS_Tools/1.0 (AIA Fetcher)"
    }

    req = request.Request(url, headers=headers)

    try:
        # AIA URLs are HTTP, not HTTPS — but we still set a context for consistency
        ctx = ssl.create_default_context()
        with request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read()

    except error.HTTPError as e:
        # 404, 403, etc.
        return None

    except error.URLError as e:
        # DNS failure, timeout, refused connection
        return None

    except Exception:
        # Any other unexpected failure
        return None
def parse_cert_bytes(raw):
    try:
        # PEM
        if raw.startswith(b"-----BEGIN CERTIFICATE-----"):
            return x509.load_pem_x509_certificate(raw, default_backend())
        # DER
        else:
            return x509.load_der_x509_certificate(raw, default_backend())
    except Exception:
        return None    
def parse_intermediate_cert(url, raw_bytes):
    """
    Parse an intermediate certificate fetched via AIA.
    Returns a dict with parsed fields or an error entry.
    """

    entry = {"url": url}

    if raw_bytes is None:
        entry["error"] = "fetch_failed"
        return entry

    cert_obj = parse_cert_bytes(raw_bytes)
    if cert_obj is None:
        entry["error"] = "parse_failed"
        return entry

    # Extract fields
    subject_cn = get_subject_cn(cert_obj)
    issuer_cn = get_issuer_cn(cert_obj)
    algo = cert_obj.signature_hash_algorithm
    sigalg = algo.name if algo is not None else cert_obj.signature_algorithm_oid._name
    key_type, key_bits, curve = get_key_info(cert_obj)

    # Extract OCSP URLs
    ocsp_urls = get_ocsp_urls(cert_obj)

    entry.update({
        "subject_cn": subject_cn,
        "issuer_cn": issuer_cn,
        "signature_algorithm": sigalg,
        "key_type": key_type,
        "ocsp_urls": ocsp_urls,
    })

    return entry
# -----------------------------
#  Extractors
# -----------------------------
def get_cert_expiry(cert):
    return cert.not_valid_after_utc
def get_cn(cert_obj):
    try:
        return cert_obj.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    except Exception:
        return None
def get_key_info(cert: x509.Certificate) -> Tuple[str, Optional[int], Optional[str]]:
    """
    Returns (key_type, key_bits, curve) in a deterministic format.
    - RSA: ('rsa', bits, None)
    - EC: ('ecdsa', None, curve_name)
    - Ed25519/Ed448: ('ed25519'/'ed448', None, None)
    - Fallback: ('unknown', None, None)
    """
    pub = cert.public_key()

    # RSA
    if isinstance(pub, rsa.RSAPublicKey):
        return ("rsa", pub.key_size, None)

    # Elliptic Curve (ECDSA)
    if isinstance(pub, ec.EllipticCurvePublicKey):
        curve_name = pub.curve.name.lower()
        return ("ecdsa", None, curve_name)

    # Ed25519
    if isinstance(pub, ed25519.Ed25519PublicKey):
        return ("ed25519", None, None)

    # Ed448
    if isinstance(pub, ed448.Ed448PublicKey):
        return ("ed448", None, None)

    # Fallback
    return ("unknown", None, None)
def get_ocsp_status(cert: x509.Certificate, timeout: float = 1.0) -> str:
    """
    Returns OCSP reachability status:
    - 'reachable' if TCP connect to OCSP responder succeeds
    - 'unreachable' if connect fails
    - 'none' if no OCSP URL is present
    """
    # Extract OCSP URL from AIA
    try:
        aia = cert.extensions.get_extension_for_oid(ExtensionOID.AUTHORITY_INFORMATION_ACCESS).value
    except x509.ExtensionNotFound:
        return "none"

    ocsp_urls = [
        desc.access_location.value
        for desc in aia
        if desc.access_method == AuthorityInformationAccessOID.OCSP
    ]

    if not ocsp_urls:
        return "none"

    ocsp_url = ocsp_urls[0]

    # Parse host/port from URL
    try:
        # Example: http://ocsp.int-x3.letsencrypt.org
        host = ocsp_url.split("://", 1)[1].split("/", 1)[0]
        if ":" in host:
            hostname, port = host.split(":", 1)
            port = int(port)
        else:
            hostname, port = host, 80
    except Exception:
        return "unreachable"

    # Attempt TCP connection
    try:
        with socket.create_connection((hostname, port), timeout=timeout):
            return "reachable"
    except Exception:
        return "unreachable"
def get_san_list(cert):
    try:
        san = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME)
        return san.value.get_values_for_type(x509.DNSName)
    except x509.ExtensionNotFound:
        return []
def get_issuer_cn(cert):
    try:
        for attr in cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME):
            return attr.value
    except Exception:
        return None
    return None
def get_subject_cn(cert) -> str:
    """
    Extract the certificate's subject CN and always return a string.
    Never returns bytes, bytearray, memoryview, or None.
    """

    try:
        attrs = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        if not attrs:
            return ""
        value = attrs[0].value
    except Exception:
        return ""

    # Normalize to string
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="ignore")
    if isinstance(value, bytearray):
        return value.decode("utf-8", errors="ignore")
    if isinstance(value, memoryview):
        return value.tobytes().decode("utf-8", errors="ignore")
    if value is None:
        return ""

    return str(value)
def get_signature_algorithm(cert: x509.Certificate) -> str:
    """
    Returns a deterministic signature algorithm name for any certificate.
    - RSA/ECDSA: returns the hash name (e.g., 'sha256')
    - Ed25519/Ed448: returns the algorithm name (e.g., 'ed25519')
    - Fallback: OID name
    """
    # Case 1: Algorithms with a hash (RSA, ECDSA)
    algo = cert.signature_hash_algorithm
    if algo is not None:
        return algo.name.lower()

    # Case 2: Algorithms without a hash (Ed25519, Ed448)
    oid_name = cert.signature_algorithm_oid._name
    if oid_name:
        return oid_name.lower()

    # Case 3: Absolute fallback (should never happen)
    return cert.signature_algorithm_oid.dotted_string
def get_ocsp_urls(cert_obj):
    urls = []
    try:
        aia = cert_obj.extensions.get_extension_for_oid(
            AuthorityInformationAccessOID.AUTHORITY_INFORMATION_ACCESS
        ).value

        for desc in aia:
            if desc.access_method == AuthorityInformationAccessOID.OCSP:
                urls.append(desc.access_location.value)
    except Exception:
        pass

    return urls
def get_tls_info(ssock) -> Tuple[str, Optional[str]]:
    """
    Returns (tls_version, cipher) in a normalized, deterministic format.
    - tls_version: 'tls1.3', 'tls1.2', etc.
    - cipher: canonical OpenSSL cipher name or None
    """
    # Normalize TLS version
    version = ssock.version()
    tls_version = version.lower() if version else "unknown"

    # Normalize cipher
    cipher_info = ssock.cipher()
    cipher = cipher_info[0] if cipher_info else None

    return tls_version, cipher
def is_wildcard_cert(cert):
    san_list = get_san_list(cert)
    if any(name.startswith("*.") for name in san_list):
        return True

    try:
        for attr in cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME):
            if attr.value.startswith("*."):
                return True
    except Exception:
        pass

    return False
def check_ocsp_reachability(url, timeout=5):
    """
    Returns:
        "reachable"   – HTTP 200/301/302
        "unreachable" – DNS failure, TCP failure, timeout, non-200
        "none"        – no OCSP URL provided
    """

    if not url:
        return "none"

    try:
        parsed = parse.urlparse(url)
        host = parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        path = parsed.path or "/"

        # DNS resolution
        try:
            socket.gethostbyname(host)
        except Exception:
            return "unreachable"

        # TCP connect
        s = socket.create_connection((host, port), timeout=timeout)

        # Minimal HTTP GET
        req = f"GET {path} HTTP/1.0\r\nHost: {host}\r\n\r\n"
        s.send(req.encode("ascii"))
        resp = s.recv(1024).decode("latin1", errors="ignore")
        s.close()

        if resp.startswith("HTTP/1.1 200") or resp.startswith("HTTP/1.0 200"):
            return "reachable"
        if resp.startswith("HTTP/1.1 301") or resp.startswith("HTTP/1.1 302"):
            return "reachable"

        return "unreachable"

    except Exception:
        return "unreachable"
