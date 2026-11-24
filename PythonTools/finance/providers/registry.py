# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Leon McClatchey, Linktech Engineering LLC
"""
 Package: PythonTools
 Author: Leon McClatchey
 Company: Linktech Engineering LLC
Created: 2026-07-07
 Modified: 2026-11-24
 File: PythonTools/finance/providers/registry.py
 Version: 1.0.0
 Description: Module description here
"""

from typing import Any

class ProviderRegistry:
    """
    Central registry for all providers used by check_ticker.
    Each provider class must define:
        - name: str
        - requires_key: bool
        - accepts_key: bool
    """

    providers: list[Any] = []

    @classmethod
    def register(cls, provider_cls) -> type:
        cls.providers.append(provider_cls())
        return provider_cls

    @classmethod
    def provider_names(cls) -> list[str]:
        return [p.name for p in cls.providers]

    @classmethod
    def get(cls, name) -> Any | None:
        for p in cls.providers:
            if p.name == name:
                return p
        return None

