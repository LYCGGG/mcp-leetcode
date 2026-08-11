"""Abstract base class defining the LeetCode service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LeetCodeBaseService(ABC):
    """Interface that all LeetCode service implementations must provide."""

    # ── User ─────────────────────────────────────────────────────

    @abstractmethod
    async def fetch_user_profile(self, username: str) -> Any:
        ...

    @abstractmethod
    async def fetch_user_status(self) -> Any:
        ...

    @abstractmethod
    async def fetch_user_all_submissions(
        self,
        offset: int,
        limit: int,
        question_slug: str | None = None,
        last_key: str | None = None,
        lang: str | None = None,
        status: str | None = None,
    ) -> Any:
        ...

    @abstractmethod
    async def fetch_user_progress_question_list(
        self,
        offset: int = 0,
        limit: int = 20,
        question_status: str | None = None,
        difficulty: list[str] | None = None,
    ) -> Any:
        ...

    @abstractmethod
    async def fetch_user_recent_submissions(
        self, username: str, limit: int | None = None
    ) -> Any:
        ...

    @abstractmethod
    async def fetch_user_recent_ac_submissions(
        self, username: str, limit: int | None = None
    ) -> Any:
        ...

    @abstractmethod
    async def fetch_user_submission_detail(self, submission_id: int) -> Any:
        ...

    @abstractmethod
    async def fetch_user_contest_ranking(
        self, username: str, attended: bool = True
    ) -> Any:
        ...

    # ── Problem ──────────────────────────────────────────────────

    @abstractmethod
    async def fetch_daily_challenge(self) -> Any:
        ...

    @abstractmethod
    async def fetch_problem(self, title_slug: str) -> Any:
        ...

    @abstractmethod
    async def fetch_problem_simplified(self, title_slug: str) -> Any:
        ...

    @abstractmethod
    async def search_problems(
        self,
        category: str | None = None,
        tags: list[str] | None = None,
        difficulty: str | None = None,
        limit: int = 10,
        offset: int = 0,
        search_keywords: str | None = None,
    ) -> Any:
        ...

    # ── Solution ─────────────────────────────────────────────────

    @abstractmethod
    async def fetch_question_solution_articles(
        self, question_slug: str, options: dict[str, Any] | None = None
    ) -> Any:
        ...

    @abstractmethod
    async def fetch_solution_article_detail(self, identifier: str) -> Any:
        ...

    # ── Note (CN only) ───────────────────────────────────────────

    @abstractmethod
    async def fetch_user_notes(
        self,
        aggregate_type: str = "QUESTION_NOTE",
        keyword: str | None = None,
        order_by: str | None = None,
        limit: int = 20,
        skip: int = 0,
    ) -> Any:
        ...

    @abstractmethod
    async def fetch_notes_by_question_id(
        self, question_id: str, limit: int = 20, skip: int = 0
    ) -> Any:
        ...

    @abstractmethod
    async def create_user_note(
        self, content: str, note_type: str, target_id: str, summary: str
    ) -> Any:
        ...

    @abstractmethod
    async def update_user_note(
        self, note_id: str, content: str, summary: str
    ) -> Any:
        ...

    # ── Code Execution ───────────────────────────────────────────

    @abstractmethod
    async def run_code(
        self,
        title_slug: str,
        question_id: str,
        lang: str,
        typed_code: str,
        data_input: str = "",
        timeout_ms: float = 120_000,
        poll_interval_ms: float = 1_500,
    ) -> Any:
        ...

    @abstractmethod
    async def submit_solution(
        self,
        title_slug: str,
        question_id: str,
        lang: str,
        typed_code: str,
        timeout_ms: float = 120_000,
        poll_interval_ms: float = 1_500,
    ) -> Any:
        ...

    # ── Meta ─────────────────────────────────────────────────────

    @abstractmethod
    def is_authenticated(self) -> bool:
        ...

    @abstractmethod
    def is_cn(self) -> bool:
        ...
