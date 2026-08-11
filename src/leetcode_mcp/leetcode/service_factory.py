"""Factory for creating the appropriate LeetCode service based on site config."""

from __future__ import annotations

from ..client import LeetCodeClient
from ..config import Config
from .base_service import LeetCodeBaseService
from .cn_service import LeetCodeCNService
from .global_service import LeetCodeGlobalService


def create_service(config: Config) -> tuple[LeetCodeBaseService, LeetCodeClient]:
    """Create a LeetCode service and its underlying HTTP client.

    Returns:
        A (service, client) tuple. The caller should close the client when done.
    """
    client = LeetCodeClient(config)
    if config.is_cn:
        service: LeetCodeBaseService = LeetCodeCNService(client, config)
    else:
        service = LeetCodeGlobalService(client, config)
    return service, client
