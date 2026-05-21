# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC

"""
 Package: RunUpdates
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
 Created: 2026-04-16
Modified: 2026-04-17
 File: PythonTools/ansible/vault_loader.py
 Version: 1.0.0
 Description: Generic deterministic Ansible Vault decryptor.

    This module MUST remain project‑agnostic.
    It provides:
    - password resolution (literal or file)
    - deterministic vault decryption
    - optional YAML parsing

    It does NOT:
    - assume any project name
    - filter YAML by project key
    - enforce schema
"""

from pathlib import Path
import subprocess
import yaml


class VaultError(Exception):
    """Raised when vault decryption or file access fails."""
    pass


class VaultLoader:
    """
    Deterministic vault loader.

    - Accepts a password source (literal string OR path)
    - Determines whether the password source is a file
    - Reads the password only if needed
    - Decrypts an Ansible vault file
    - Optionally extracts a subtree based on program_name
    """

    def __init__(self, vault_file: str | Path, password_source: str, program_name: str | None = None):
        self.vault_file = Path(vault_file).expanduser()
        self.password_source = password_source  # literal OR path
        self.program_name = program_name.lower() if program_name else None

    # ------------------------------------------------------------
    # Password Handling
    # ------------------------------------------------------------
    def resolve_password(self) -> str:
        p = Path(self.password_source).expanduser()

        if p.exists() and p.is_file():
            try:
                return p.read_text(encoding="utf-8").strip()
            except Exception as exc:
                raise VaultError(f"Failed to read password file: {p}") from exc

        return self.password_source.strip()

    # ------------------------------------------------------------
    # Vault Decryption
    # ------------------------------------------------------------
    def decrypt(self) -> str:
        if not self.vault_file.exists():
            raise VaultError(f"Vault file not found: {self.vault_file}")

        password = self.resolve_password()

        import tempfile

        with tempfile.NamedTemporaryFile("w", delete=True) as tmp:
            tmp.write(password)
            tmp.flush()

            cmd = [
                "ansible-vault",
                "view",
                "--vault-password-file",
                tmp.name,
                str(self.vault_file),
            ]

            try:
                return subprocess.check_output(cmd, text=True)
            except subprocess.CalledProcessError as exc:
                raise VaultError(f"Vault decryption failed: {exc}") from exc

    # ------------------------------------------------------------
    # YAML Parsing + Optional Subtree Extraction
    # ------------------------------------------------------------
    def decrypt_yaml(self) -> dict:

        plaintext = self.decrypt()

        try:
            data = yaml.safe_load(plaintext) or {}
        except Exception as exc:
            raise VaultError("Vault decrypted but YAML parsing failed") from exc

        if not isinstance(data, dict):
            raise VaultError("Vault YAML must contain a top-level dictionary")

        # If no program name was provided, return full structure
        if not self.program_name:
            return data

        # Extract subtree
        if self.program_name not in data:
            raise VaultError(
                f"Vault does not contain a section for '{self.program_name}'"
            )

        subtree = data[self.program_name]

        if not isinstance(subtree, dict):
            raise VaultError(
                f"Vault section '{self.program_name}' must contain a dictionary"
            )

        return subtree
