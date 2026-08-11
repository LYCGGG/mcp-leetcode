"""Problem-related MCP tools: daily challenge, problem details, search."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from ..leetcode.base_service import LeetCodeBaseService
from .registry_base import RegistryBase


class ProblemToolRegistry(RegistryBase):

    def register_common(self) -> None:
        server = self.server
        service = self.service

        @server.tool()
        async def get_daily_challenge() -> str:
            """Retrieves today's LeetCode Daily Challenge problem with full description (read-only, no auth). Use get_problem for a specific titleSlug; use search_problems to discover problems."""
            data = await service.fetch_daily_challenge()
            return json.dumps({"date": data.get("date") if data else None, "problem": data})

        @server.tool()
        async def get_problem(title_slug: str) -> str:
            """Retrieves a single LeetCode problem by titleSlug (read-only, no auth). Returns description, examples, constraints, and metadata as JSON."""
            data = await service.fetch_problem_simplified(title_slug)
            return json.dumps({"titleSlug": title_slug, "problem": data})

        @server.tool()
        async def search_problems(
            category: str = "all-code-essentials",
            tags: list[str] | None = None,
            difficulty: str | None = None,
            search_keywords: str | None = None,
            limit: int = 10,
            offset: int = 0,
        ) -> str:
            """Searches LeetCode problems by category, tags, difficulty, and keywords (read-only, no auth). Supports pagination via limit/offset."""
            data = await service.search_problems(
                category=category,
                tags=tags,
                difficulty=difficulty,
                limit=limit,
                offset=offset,
                search_keywords=search_keywords,
            )
            return json.dumps({
                "filters": {"tags": tags, "difficulty": difficulty, "searchKeywords": search_keywords},
                "pagination": {"limit": limit, "offset": offset},
                "problems": data,
            })


def register_problem_tools(server: FastMCP, service: LeetCodeBaseService) -> None:
    ProblemToolRegistry(server, service).register()
