"""Async HTTP client for LeetCode API (GraphQL + REST)."""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
from loguru import logger

from .config import Config
from .exceptions import (
    AuthenticationError,
    GraphQLError,
    NetworkError,
    RateLimitError,
    SubmissionError,
)


def _looks_like_html(text: str) -> bool:
    stripped = text.strip().lower()
    return stripped.startswith("<!doctype html") or stripped.startswith("<html")


def _is_pending_state(state: Any) -> bool:
    if not isinstance(state, str):
        return True
    return state.upper() in ("PENDING", "STARTED")


class LeetCodeClient:
    """Low-level async HTTP client for LeetCode APIs."""

    def __init__(self, config: Config) -> None:
        self._config = config
        self._base_url = config.base_url
        self._client: httpx.AsyncClient | None = None

    def _build_headers(self) -> dict[str, str]:
        headers: dict[str, str] = {
            "content-type": "application/json",
            "origin": self._base_url,
            "referer": f"{self._base_url}/",
        }
        if self._config.is_authenticated:
            session = self._config.auth.session
            csrf = self._config.auth.csrf_token
            cookie_parts: list[str] = []
            if "LEETCODE_SESSION=" in session:
                cookie_parts.append(session)
            else:
                cookie_parts.append(f"LEETCODE_SESSION={session}")
            if "csrftoken=" not in session:
                cookie_parts.append(f"csrftoken={csrf}")
            headers["cookie"] = "; ".join(cookie_parts)
            headers["x-csrftoken"] = csrf
        return headers

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    # ── GraphQL ──────────────────────────────────────────────────

    async def graphql(self, query: str, variables: dict[str, Any] | None = None) -> Any:
        """Execute a GraphQL query and return the 'data' field."""
        url = f"{self._base_url}/graphql"
        body: dict[str, Any] = {"query": query}
        if variables:
            body["variables"] = variables

        headers = self._build_headers()
        # GraphQL endpoint should not carry x-csrftoken on GET-style queries
        # but POST with JSON body is standard
        logger.debug("GraphQL request: {}", query[:100])

        client = await self._get_client()
        try:
            resp = await client.post(url, json=body, headers=headers)
        except httpx.RequestError as e:
            raise NetworkError(f"GraphQL request failed: {e}") from e

        if resp.status_code == 429:
            retry_after = resp.headers.get("retry-after")
            raise RateLimitError(retry_after=float(retry_after) if retry_after else None)

        text = resp.text
        if _looks_like_html(text):
            raise AuthenticationError(
                "Received HTML response (likely not authenticated or blocked)"
            )

        if resp.status_code != 200:
            raise NetworkError(f"GraphQL HTTP {resp.status_code}: {text[:200]}")

        try:
            payload = resp.json()
        except json.JSONDecodeError as e:
            raise NetworkError(f"Invalid JSON from GraphQL: {e}") from e

        if "errors" in payload:
            raise GraphQLError(payload["errors"])

        return payload.get("data")

    # ── REST helpers ─────────────────────────────────────────────

    async def post_json(self, path: str, body: Any = None) -> Any:
        """POST to a REST endpoint, return parsed JSON."""
        url = f"{self._base_url}{path}"
        headers = self._build_headers()

        client = await self._get_client()
        try:
            resp = await client.post(url, json=body or {}, headers=headers)
        except httpx.RequestError as e:
            raise NetworkError(f"POST {path} failed: {e}") from e

        if resp.status_code == 429:
            retry_after = resp.headers.get("retry-after")
            raise RateLimitError(retry_after=float(retry_after) if retry_after else None)

        text = resp.text
        if _looks_like_html(text):
            raise AuthenticationError(f"POST {path}: not authenticated or blocked")

        if not resp.is_success:
            raise NetworkError(f"POST {path}: HTTP {resp.status_code}")

        try:
            return resp.json()
        except json.JSONDecodeError as e:
            raise NetworkError(f"POST {path}: invalid JSON: {e}") from e

    async def get_json(self, path: str) -> Any:
        """GET a REST endpoint, return parsed JSON."""
        url = f"{self._base_url}{path}"
        headers = self._build_headers()

        client = await self._get_client()
        try:
            resp = await client.get(url, headers=headers)
        except httpx.RequestError as e:
            raise NetworkError(f"GET {path} failed: {e}") from e

        if resp.status_code == 429:
            retry_after = resp.headers.get("retry-after")
            raise RateLimitError(retry_after=float(retry_after) if retry_after else None)

        text = resp.text
        if _looks_like_html(text):
            raise AuthenticationError(f"GET {path}: not authenticated or blocked")

        if not resp.is_success:
            raise NetworkError(f"GET {path}: HTTP {resp.status_code}")

        try:
            return resp.json()
        except json.JSONDecodeError as e:
            raise NetworkError(f"GET {path}: invalid JSON: {e}") from e

    async def poll_check(
        self,
        check_path: str,
        timeout_ms: float = 120_000,
        poll_interval_ms: float = 1_500,
    ) -> dict[str, Any]:
        """Poll a check endpoint until state is no longer PENDING/STARTED."""
        deadline = asyncio.get_event_loop().time() + timeout_ms / 1000
        interval = max(0.2, poll_interval_ms / 1000)

        while True:
            if asyncio.get_event_loop().time() > deadline:
                raise SubmissionError(f"Polling timed out for {check_path}")

            client = await self._get_client()
            url = f"{self._base_url}{check_path}"
            headers = self._build_headers()

            try:
                resp = await client.get(url, headers=headers)
            except httpx.RequestError as e:
                raise NetworkError(f"GET {check_path} failed: {e}") from e

            if resp.status_code == 429:
                retry_after = resp.headers.get("retry-after")
                backoff = float(retry_after) if retry_after else min(interval * 2, 10)
                await asyncio.sleep(backoff)
                interval = backoff
                continue

            text = resp.text
            if _looks_like_html(text):
                raise AuthenticationError(f"GET {check_path}: not authenticated or blocked")

            if not resp.is_success:
                raise NetworkError(f"GET {check_path}: HTTP {resp.status_code}")

            try:
                data = resp.json()
            except json.JSONDecodeError as e:
                raise NetworkError(f"GET {check_path}: invalid JSON: {e}") from e

            if not isinstance(data, dict):
                raise SubmissionError(f"GET {check_path}: unexpected response type")

            if not _is_pending_state(data.get("state")):
                return data

            await asyncio.sleep(interval)
