"""Unit tests for cache.py."""

from __future__ import annotations

import asyncio
import time

import pytest

from leetcode_mcp.cache import TTLCache, cached, configure_cache, get_cache


class TestTTLCache:
    """Test TTLCache class."""

    def test_set_and_get(self):
        cache = TTLCache(maxsize=10, ttl=60)
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_nonexistent_key(self):
        cache = TTLCache()
        assert cache.get("nonexistent") is None

    def test_ttl_expiration(self):
        cache = TTLCache(ttl=0.1)  # 100ms TTL
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

        time.sleep(0.15)  # Wait for expiration
        assert cache.get("key1") is None

    def test_lru_eviction(self):
        cache = TTLCache(maxsize=2, ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # Should evict key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"

    def test_invalidate(self):
        cache = TTLCache()
        cache.set("key1", "value1")
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_clear(self):
        cache = TTLCache()
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.clear()
        assert cache.get("key1") is None
        assert cache.get("key2") is None

    def test_lru_order_update(self):
        cache = TTLCache(maxsize=2, ttl=60)
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        _ = cache.get("key1")  # Access key1 to update LRU order
        cache.set("key3", "value3")  # Should evict key2 (LRU)

        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"


class TestDefaultCache:
    """Test module-level cache functions."""

    def test_get_cache_returns_singleton(self):
        cache1 = get_cache()
        cache2 = get_cache()
        assert cache1 is cache2

    def test_configure_cache(self):
        configure_cache(maxsize=128, ttl=60)
        cache = get_cache()
        assert cache._maxsize == 128
        assert cache._ttl == 60

        # Reset to default
        configure_cache(maxsize=256, ttl=300)


class TestCachedDecorator:
    """Test @cached decorator."""

    @pytest.mark.asyncio
    async def test_cached_function(self):
        configure_cache(ttl=60)
        call_count = 0

        @cached(ttl=60)
        async def expensive_function(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        result2 = await expensive_function(5)  # Should use cache
        assert result2 == 10
        assert call_count == 1  # Not called again

    @pytest.mark.asyncio
    async def test_cached_different_args(self):
        configure_cache(ttl=60)
        call_count = 0

        @cached(ttl=60)
        async def add(a: int, b: int) -> int:
            nonlocal call_count
            call_count += 1
            return a + b

        result1 = await add(1, 2)
        result2 = await add(3, 4)
        assert result1 == 3
        assert result2 == 7
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_cached_method(self):
        configure_cache(ttl=60)
        call_count = 0

        class MyService:
            @cached(ttl=60)
            async def get_data(self, key: str) -> str:
                nonlocal call_count
                call_count += 1
                return f"data_{key}"

        service = MyService()
        result1 = await service.get_data("test")
        result2 = await service.get_data("test")
        assert result1 == "data_test"
        assert call_count == 1
