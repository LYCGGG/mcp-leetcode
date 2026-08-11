"""Note-related MCP tools (CN + auth only): search, get, create, update."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from ..exceptions import LeetCodeError
from ..leetcode.base_service import LeetCodeBaseService
from .registry_base import RegistryBase


class NoteToolRegistry(RegistryBase):

    def register_authenticated_china(self) -> None:
        server = self.server
        service = self.service

        @server.tool()
        async def search_notes(
            keyword: str | None = None,
            limit: int = 10,
            skip: int = 0,
            order_by: str = "DESCENDING",
        ) -> str:
            """Searches the authenticated user's personal notes across all problems (read-only, requires auth, CN only)."""
            try:
                data = await service.fetch_user_notes(
                    aggregate_type="QUESTION_NOTE",
                    keyword=keyword,
                    order_by=order_by,
                    limit=limit,
                    skip=skip,
                )
                return json.dumps({
                    "filters": {"keyword": keyword, "orderBy": order_by},
                    "pagination": {"limit": limit, "skip": skip, "totalCount": data.get("count", 0)},
                    "notes": data.get("userNotes", []),
                })
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})

        @server.tool()
        async def get_note(question_id: str, limit: int = 10, skip: int = 0) -> str:
            """Retrieves personal notes for a specific problem by questionId (read-only, requires auth, CN only)."""
            try:
                data = await service.fetch_notes_by_question_id(question_id, limit, skip)
                return json.dumps({
                    "questionId": question_id,
                    "count": data.get("count", 0),
                    "notes": data.get("userNotes", []),
                })
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})

        @server.tool()
        async def create_note(question_id: str, content: str, summary: str = "") -> str:
            """Creates a new personal note for a problem (write operation, requires auth, CN only)."""
            try:
                data = await service.create_user_note(content, "COMMON_QUESTION", question_id, summary)
                return json.dumps({"success": data.get("ok", False), "note": data.get("note")})
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})

        @server.tool()
        async def update_note(note_id: str, content: str, summary: str = "") -> str:
            """Updates an existing personal note by noteId (write operation, requires auth, CN only)."""
            try:
                data = await service.update_user_note(note_id, content, summary)
                return json.dumps({"success": data.get("ok", False), "note": data.get("note")})
            except LeetCodeError as e:
                return json.dumps({"error": str(e)})


def register_note_tools(server: FastMCP, service: LeetCodeBaseService) -> None:
    NoteToolRegistry(server, service).register()
