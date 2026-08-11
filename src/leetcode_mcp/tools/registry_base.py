"""Template Method base class for tool/resource registration.

Registration order (mirrors the TypeScript reference):
  1. registerCommon()                       — unauthenticated, both sites
  2. registerChina() / registerGlobal()     — unauthenticated, site-specific
  3. if authenticated:
       registerAuthenticatedCommon()         — authenticated, both sites
       registerAuthenticatedChina() / registerAuthenticatedGlobal()
"""

from __future__ import annotations

from abc import ABC

from mcp.server.fastmcp import FastMCP

from ..leetcode.base_service import LeetCodeBaseService


class RegistryBase(ABC):
    """Abstract base for tool/resource registries."""

    def __init__(self, server: FastMCP, service: LeetCodeBaseService) -> None:
        self.server = server
        self.service = service

    def is_cn(self) -> bool:
        return self.service.is_cn()

    def is_authenticated(self) -> bool:
        return self.service.is_authenticated()

    def register(self) -> None:
        """Run the full registration sequence."""
        self.register_common()

        if self.is_cn():
            self.register_china()
        else:
            self.register_global()

        if self.is_authenticated():
            self.register_authenticated_common()

            if self.is_cn():
                self.register_authenticated_china()
            else:
                self.register_authenticated_global()

    # ── Hook methods (override in subclasses) ────────────────────

    def register_common(self) -> None: ...
    def register_global(self) -> None: ...
    def register_china(self) -> None: ...
    def register_authenticated_common(self) -> None: ...
    def register_authenticated_global(self) -> None: ...
    def register_authenticated_china(self) -> None: ...
