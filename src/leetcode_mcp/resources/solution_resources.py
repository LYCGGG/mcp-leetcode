"""Solution-related MCP resources."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from ..leetcode.base_service import LeetCodeBaseService
from .resource_registry import ResourceRegistry


class SolutionResourceRegistry(ResourceRegistry):

    def register_global(self) -> None:
        server = self.server
        service = self.service

        @server.resource("solution://{topicId}")
        async def solution_detail(topicId: str) -> str:
            """Full content of a solution article on LeetCode Global (use topicId from list_problem_solutions)."""
            try:
                data = await service.fetch_solution_article_detail(topicId)
                return json.dumps({"topicId": topicId, "solution": data})
            except Exception as e:
                return json.dumps({"error": str(e)})

    def register_china(self) -> None:
        server = self.server
        service = self.service

        @server.resource("solution://{slug}")
        async def solution_detail(slug: str) -> str:
            """Full content of a solution article on LeetCode CN (use slug from list_problem_solutions)."""
            try:
                data = await service.fetch_solution_article_detail(slug)
                return json.dumps({"slug": slug, "solution": data})
            except Exception as e:
                return json.dumps({"error": str(e)})


def register_solution_resources(server: FastMCP, service: LeetCodeBaseService) -> None:
    SolutionResourceRegistry(server, service).register_resources()
