"""Base registry for MCP resources (extends RegistryBase)."""

from __future__ import annotations

from ..tools.registry_base import RegistryBase


class ResourceRegistry(RegistryBase):
    """Base class for resource registries. Shares the same Template Method pattern as tool registries."""

    def register_resources(self) -> None:
        self.register()
