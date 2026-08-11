"""Code execution MCP tools: run_code, submit_solution."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from ..exceptions import LeetCodeError
from ..leetcode.base_service import LeetCodeBaseService
from .registry_base import RegistryBase


class SubmissionToolRegistry(RegistryBase):

    def register_authenticated_common(self) -> None:
        server = self.server
        service = self.service

        @server.tool()
        async def run_code(
            title_slug: str,
            lang: str,
            typed_code: str,
            data_input: str = "",
            timeout_ms: int = 120_000,
            poll_interval_ms: int = 1_500,
        ) -> str:
            """Runs code against test cases without submitting (requires auth). Returns execution result as JSON. Use submit_solution for official judging."""
            try:
                problem = await service.fetch_problem_simplified(title_slug)
                question_id = str(problem.get("questionId", ""))
                if not question_id:
                    return json.dumps({"error": f"Failed to resolve questionId for {title_slug}"})

                result = await service.run_code(
                    title_slug=title_slug,
                    question_id=question_id,
                    lang=lang,
                    typed_code=typed_code,
                    data_input=data_input,
                    timeout_ms=timeout_ms,
                    poll_interval_ms=poll_interval_ms,
                )
                return json.dumps({
                    "titleSlug": title_slug,
                    "questionId": question_id,
                    "start": result["start"],
                    "checkUrl": result["checkUrl"],
                    "check": result["check"],
                })
            except LeetCodeError as e:
                return json.dumps({"error": "Failed to run code", "message": str(e)})

        @server.tool()
        async def submit_solution(
            title_slug: str,
            lang: str,
            typed_code: str,
            timeout_ms: int = 120_000,
            poll_interval_ms: int = 1_500,
        ) -> str:
            """Submits code for official judging (requires auth). Returns submission result as JSON."""
            try:
                problem = await service.fetch_problem_simplified(title_slug)
                question_id = str(problem.get("questionId", ""))
                if not question_id:
                    return json.dumps({"error": f"Failed to resolve questionId for {title_slug}"})

                result = await service.submit_solution(
                    title_slug=title_slug,
                    question_id=question_id,
                    lang=lang,
                    typed_code=typed_code,
                    timeout_ms=timeout_ms,
                    poll_interval_ms=poll_interval_ms,
                )
                return json.dumps({
                    "titleSlug": title_slug,
                    "questionId": question_id,
                    "start": result["start"],
                    "checkUrl": result["checkUrl"],
                    "check": result["check"],
                })
            except LeetCodeError as e:
                return json.dumps({"error": "Failed to submit solution", "message": str(e)})


def register_submission_tools(server: FastMCP, service: LeetCodeBaseService) -> None:
    SubmissionToolRegistry(server, service).register()
