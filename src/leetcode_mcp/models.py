"""Pydantic data models for tool parameters and internal structures."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field

# ── Enums ────────────────────────────────────────────────────────


class Difficulty(StrEnum):
    EASY = "EASY"
    MEDIUM = "MEDIUM"
    HARD = "HARD"


class SubmissionStatus(StrEnum):
    AC = "AC"
    WA = "WA"


class NoteOrderBy(StrEnum):
    ASCENDING = "ASCENDING"
    DESCENDING = "DESCENDING"


class SolutionOrderByCN(StrEnum):
    DEFAULT = "DEFAULT"
    MOST_UPVOTE = "MOST_UPVOTE"
    HOT = "HOT"
    NEWEST_TO_OLDEST = "NEWEST_TO_OLDEST"
    OLDEST_TO_NEWEST = "OLDEST_TO_NEWEST"


class SolutionOrderByGlobal(StrEnum):
    HOT = "HOT"
    MOST_RECENT = "MOST_RECENT"
    MOST_VOTES = "MOST_VOTES"


# ── Tool Parameter Models ────────────────────────────────────────


class GetProblemParams(BaseModel):
    title_slug: str = Field(description="The URL slug/identifier of the problem")


class SearchProblemsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: str = Field(default="all-code-essentials", description="Problem category filter")
    tags: list[str] = Field(default_factory=list, description="Topic tags to filter by")
    difficulty: Difficulty | None = Field(default=None, description="Difficulty level filter")
    search_keywords: str | None = Field(default=None, description="Keywords to search")
    limit: int = Field(default=10, ge=1, le=100, description="Max problems to return")
    offset: int = Field(default=0, ge=0, description="Number of problems to skip")


class GetUserProfileParams(BaseModel):
    username: str = Field(description="LeetCode username")


class GetRecentSubmissionsParams(BaseModel):
    username: str = Field(description="LeetCode username")
    limit: int = Field(default=10, ge=1, le=50, description="Max submissions to return")


class GetAllSubmissionsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=20, ge=1, le=100, description="Max submissions to return")
    offset: int = Field(default=0, ge=0, description="Number of submissions to skip")
    question_slug: str | None = Field(default=None, description="Filter by problem slug")
    lang: str | None = Field(default=None, description="Filter by language (CN only)")
    status: SubmissionStatus | None = Field(default=None, description="Filter by status (CN only)")
    last_key: str | None = Field(default=None, description="Pagination token (CN only)")


class GetSubmissionReportParams(BaseModel):
    id: int = Field(description="Submission ID")


class GetUserProgressParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    offset: int = Field(default=0, ge=0, description="Number of questions to skip")
    limit: int = Field(default=100, ge=1, le=500, description="Max questions to return")
    question_status: str | None = Field(default=None, description="Filter: ATTEMPTED or SOLVED")
    difficulty: list[str] | None = Field(default=None, description="Filter by difficulty levels")


class GetContestRankingParams(BaseModel):
    username: str = Field(description="LeetCode username")
    attended: bool = Field(default=True, description="Only include attended contests")


class ListSolutionsParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_slug: str = Field(description="Problem slug")
    limit: int = Field(default=10, ge=1, le=50, description="Max solutions to return")
    skip: int = Field(default=0, ge=0, description="Solutions to skip")
    user_input: str | None = Field(default=None, description="Search term to filter")
    tag_slugs: list[str] = Field(default_factory=list, description="Tag slugs to filter")
    order_by: str | None = Field(default=None, description="Sort order")


class GetSolutionDetailParams(BaseModel):
    identifier: str = Field(description="Solution identifier (topicId for Global, slug for CN)")


class SearchNotesParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    keyword: str | None = Field(default=None, description="Search term to filter notes")
    limit: int = Field(default=10, ge=1, le=50, description="Max notes to return")
    skip: int = Field(default=0, ge=0, description="Notes to skip")
    order_by: NoteOrderBy = Field(default=NoteOrderBy.DESCENDING, description="Sort order")


class GetNoteParams(BaseModel):
    question_id: str = Field(description="Question ID to get notes for")
    limit: int = Field(default=10, ge=1, le=50, description="Max notes to return")
    skip: int = Field(default=0, ge=0, description="Notes to skip")


class CreateNoteParams(BaseModel):
    question_id: str = Field(description="Question ID to create note for")
    content: str = Field(description="Note content (markdown supported)")
    summary: str = Field(default="", description="Short summary/title for the note")


class UpdateNoteParams(BaseModel):
    note_id: str = Field(description="Note ID to update")
    content: str = Field(description="New note content (markdown supported)")
    summary: str = Field(default="", description="New summary/title")


class RunCodeParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title_slug: str = Field(description="Problem slug")
    lang: str = Field(description="Programming language (e.g. python3, cpp, java)")
    typed_code: str = Field(description="Source code to run")
    data_input: str = Field(default="", description="Custom test input")
    timeout_ms: int = Field(default=120_000, ge=1000, description="Polling timeout in ms")
    poll_interval_ms: int = Field(default=1_500, ge=200, description="Polling interval in ms")


class SubmitSolutionParams(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title_slug: str = Field(description="Problem slug")
    lang: str = Field(description="Programming language (e.g. python3, cpp, java)")
    typed_code: str = Field(description="Source code to submit")
    timeout_ms: int = Field(default=120_000, ge=1000, description="Polling timeout in ms")
    poll_interval_ms: int = Field(default=1_500, ge=200, description="Polling interval in ms")
