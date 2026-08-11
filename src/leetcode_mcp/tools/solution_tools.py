"""Solution-related MCP tools: list and get solution articles."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from ..exceptions import LeetCodeError
from ..leetcode.base_service import LeetCodeBaseService
from .registry_base import RegistryBase


class SolutionToolRegistry(RegistryBase):

    def register_global(self) -> None:
        server = self.server
        service = self.service

        @server.tool()
        async def list_problem_solutions(
            question_slug: str,
            limit: int = 10,
            skip: int = 0,
            order_by: str = "HOT",
            user_input: str | None = None,
            tag_slugs: list[str] | None = None,
        ) -> str:
            """Lists community solution articles for a problem on LeetCode Global (read-only, no auth). Returns topicId for get_problem_solution."""
            try:
                data = await service.fetch_question_solution_articles(
                    question_slug,
                    {"limit": limit, "skip": skip, "orderBy": order_by, "userInput": user_input, "tagSlugs": tag_slugs or []},
                )
                return json.dumps({"questionSlug": question_slug, "solutionArticles": data})
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})

        @server.tool()
        async def get_problem_solution(topic_id: str) -> str:
            """Retrieves full content of a community solution on LeetCode Global (read-only, no auth). Use topicId from list_problem_solutions."""
            try:
                data = await service.fetch_solution_article_detail(topic_id)
                return json.dumps({"topicId": topic_id, "solution": data})
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})

    def register_china(self) -> None:
        server = self.server
        service = self.service

        @server.tool()
        async def list_problem_solutions(
            question_slug: str,
            limit: int = 10,
            skip: int = 0,
            order_by: str = "DEFAULT",
            user_input: str | None = None,
            tag_slugs: list[str] | None = None,
        ) -> str:
            """Lists community solution articles for a problem on LeetCode CN (read-only, no auth). Returns slug for get_problem_solution."""
            try:
                data = await service.fetch_question_solution_articles(
                    question_slug,
                    {"limit": limit, "skip": skip, "orderBy": order_by, "userInput": user_input, "tagSlugs": tag_slugs or []},
                )
                return json.dumps({"questionSlug": question_slug, "solutionArticles": data})
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})

        @server.tool()
        async def get_problem_solution(slug: str) -> str:
            """Retrieves full content of a community solution on LeetCode CN (read-only, no auth). Use slug from list_problem_solutions."""
            try:
                data = await service.fetch_solution_article_detail(slug)
                return json.dumps({"slug": slug, "solution": data})
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})


def register_solution_tools(server: FastMCP, service: LeetCodeBaseService) -> None:
    SolutionToolRegistry(server, service).register()
