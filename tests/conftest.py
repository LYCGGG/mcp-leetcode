"""Pytest configuration and fixtures."""

from __future__ import annotations

import pytest


@pytest.fixture
def anyio_backend():
    """Use asyncio backend for anyio."""
    return "asyncio"
