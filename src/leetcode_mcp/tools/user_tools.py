"""User-related MCP tools: profile, submissions, progress, contest."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from ..exceptions import LeetCodeError
from ..leetcode.base_service import LeetCodeBaseService
from .registry_base import RegistryBase


class UserToolRegistry(RegistryBase):

    def register_common(self) -> None:
        server = self.server
        service = self.service

        @server.tool()
        async def get_user_profile(username: str) -> str:
            """Retrieves any user's public profile by username (read-only, no auth). Returns ranking, avatar, submission stats."""
            data = await service.fetch_user_profile(username)
            return json.dumps({"username": username, "profile": data})

        @server.tool()
        async def get_recent_ac_submissions(username: str, limit: int = 10) -> str:
            """Retrieves a user's recent accepted (AC) submissions (read-only, no auth)."""
            try:
                data = await service.fetch_user_recent_ac_submissions(username, limit)
                return json.dumps({"username": username, "submissions": data})
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})

        @server.tool()
        async def get_user_contest_ranking(username: str, attended: bool = True) -> str:
            """Retrieves a user's contest ranking information (read-only, no auth)."""
            data = await service.fetch_user_contest_ranking(username, attended)
            return json.dumps({"username": username, "contest": data})

    def register_global(self) -> None:
        server = self.server
        service = self.service

        @server.tool()
        async def get_recent_submissions(username: str, limit: int = 10) -> str:
            """Retrieves a user's recent submissions on LeetCode Global (read-only, no auth). Includes both AC and failed. Global only."""
            try:
                data = await service.fetch_user_recent_submissions(username, limit)
                return json.dumps({"username": username, "submissions": data})
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})

    def register_authenticated_common(self) -> None:
        server = self.server
        service = self.service

        @server.tool()
        async def get_user_status() -> str:
            """Checks the authenticated user's LeetCode login session (read-only, requires auth)."""
            try:
                data = await service.fetch_user_status()
                return json.dumps({"status": data})
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})

        @server.tool()
        async def get_problem_submission_report(id: int) -> str:
            """Retrieves full details for one submission by ID (read-only, requires auth)."""
            try:
                data = await service.fetch_user_submission_detail(id)
                return json.dumps({"submissionId": id, "detail": data})
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})

        @server.tool()
        async def get_problem_progress(
            offset: int = 0,
            limit: int = 100,
            question_status: str | None = None,
            difficulty: list[str] | None = None,
        ) -> str:
            """Retrieves the authenticated user's per-problem solving progress (read-only, requires auth)."""
            try:
                data = await service.fetch_user_progress_question_list(
                    offset=offset,
                    limit=limit,
                    question_status=question_status,
                    difficulty=difficulty,
                )
                return json.dumps({
                    "filters": {"offset": offset, "limit": limit, "questionStatus": question_status, "difficulty": difficulty},
                    "questions": data,
                })
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})

    def register_authenticated_global(self) -> None:
        server = self.server
        service = self.service

        @server.tool()
        async def get_all_submissions(
            limit: int = 20,
            offset: int = 0,
            question_slug: str | None = None,
        ) -> str:
            """Retrieves paginated submission history for the authenticated user on LeetCode Global (read-only, requires auth)."""
            try:
                data = await service.fetch_user_all_submissions(
                    offset=offset, limit=limit, question_slug=question_slug
                )
                return json.dumps({"problem": question_slug, "submissions": data})
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})

    def register_authenticated_china(self) -> None:
        server = self.server
        service = self.service

        @server.tool()
        async def get_all_submissions(
            limit: int = 20,
            offset: int = 0,
            question_slug: str | None = None,
            lang: str | None = None,
            status: str | None = None,
            last_key: str | None = None,
        ) -> str:
            """Retrieves paginated submission history for the authenticated user on LeetCode CN (read-only, requires auth). Supports filtering by lang and AC/WA status."""
            try:
                data = await service.fetch_user_all_submissions(
                    offset=offset,
                    limit=limit,
                    question_slug=question_slug,
                    lang=lang,
                    status=status,
                    last_key=last_key,
                )
                return json.dumps(data)
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})


def register_user_tools(server: FastMCP, service: LeetCodeBaseService) -> None:
    UserToolRegistry(server, service).register()
