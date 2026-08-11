"""TTL LRU cache for reducing redundant API calls."""

from __future__ import annotations

import functools
import time
from collections import OrderedDict
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class TTLCache:
    """A simple in-memory LRU cache with per-entry TTL expiration."""

    def __init__(self, maxsize: int = 256, ttl: float = 300.0) -> None:
        self._maxsize = maxsize
        self._ttl = ttl
        self._store: OrderedDict[str, tuple[float, Any]] = OrderedDict()

    def get(self, key: str) -> Any | None:
        """Return cached value if present and not expired, else None."""
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        # Move to end (most recently used)
        self._store.move_to_end(key)
        return value

    def set(self, key: str, value: Any) -> None:
        """Store a value with the configured TTL."""
        if key in self._store:
            self._store.move_to_end(key)
        self._store[key] = (time.monotonic() + self._ttl, value)
        if len(self._store) > self._maxsize:
            self._store.popitem(last=False)

    def invalidate(self, key: str) -> None:
        """Remove a specific key from the cache."""
        self._store.pop(key, None)

    def clear(self) -> None:
        """Remove all entries."""
        self._store.clear()


# Module-level default cache instance
_default_cache = TTLCache()


def get_cache() -> TTLCache:
    """Return the default module-level cache."""
    return _default_cache


def configure_cache(maxsize: int = 256, ttl: float = 300.0) -> None:
    """Reconfigure the default cache."""
    global _default_cache
    _default_cache = TTLCache(maxsize=maxsize, ttl=ttl)


def cached(ttl: float | None = None) -> Callable[[F], F]:
    """Decorator that caches async function results by their arguments.

    Usage:
        @cached(ttl=300)
        async def get_problem(title_slug: str) -> dict:
            ...
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            cache = get_cache()
            # Build a cache key from function name and arguments
            # Skip 'self' argument for methods
            key_parts = [func.__qualname__]
            start = 1 if args and hasattr(args[0], "__class__") else 0
            for arg in args[start:]:
                key_parts.append(repr(arg))
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v!r}")
            cache_key = "|".join(key_parts)

            result = cache.get(cache_key)
            if result is not None:
                return result

            result = await func(*args, **kwargs)
            effective_ttl = ttl if ttl is not None else get_cache()._ttl
            # Use a temporary cache with custom TTL
            if effective_ttl != get_cache()._ttl:
                temp = TTLCache(maxsize=1, ttl=effective_ttl)
                temp.set(cache_key, result)
                # Store in main cache too
                get_cache()._store[cache_key] = (time.monotonic() + effective_ttl, result)
            else:
                get_cache().set(cache_key, result)
            return result

        return wrapper  # type: ignore[return-value]

    return decorator
