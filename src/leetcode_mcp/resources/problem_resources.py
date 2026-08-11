"""Problem-related MCP resources: categories, tags, langs, problem-detail."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from ..constants import PROBLEM_CATEGORIES, PROBLEM_TAGS, PROGRAMMING_LANGS
from ..leetcode.base_service import LeetCodeBaseService
from .resource_registry import ResourceRegistry


class ProblemResourceRegistry(ResourceRegistry):

    def register_common(self) -> None:
        server = self.server
        service = self.service

        @server.resource("categories://problems/all")
        async def problem_categories() -> str:
            """A list of all problem classification categories on LeetCode."""
            return json.dumps(PROBLEM_CATEGORIES)

        @server.resource("tags://problems/all")
        async def problem_tags() -> str:
            """All algorithmic and data structure tags used by LeetCode to categorize problems."""
            return json.dumps(PROBLEM_TAGS)

        @server.resource("langs://problems/all")
        async def problem_langs() -> str:
            """All programming languages supported by LeetCode for code submission."""
            return json.dumps(PROGRAMMING_LANGS)

        @server.resource("problem://{titleSlug}")
        async def problem_detail(titleSlug: str) -> str:
            """Provides details about a specific LeetCode problem by titleSlug."""
            try:
                data = await service.fetch_problem(titleSlug)
                return json.dumps({"titleSlug": titleSlug, "problem": data})
            except Exception as e:
                return json.dumps({"error": str(e)})


def register_problem_resources(server: FastMCP, service: LeetCodeBaseService) -> None:
    ProblemResourceRegistry(server, service).register_resources()
