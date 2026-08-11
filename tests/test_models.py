"""Unit tests for models.py."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from leetcode_mcp.models import (
    CreateNoteParams,
    Difficulty,
    GetAllSubmissionsParams,
    GetProblemParams,
    GetRecentSubmissionsParams,
    GetUserProfileParams,
    GetUserProgressParams,
    ListSolutionsParams,
    NoteOrderBy,
    RunCodeParams,
    SearchProblemsParams,
    SolutionOrderByCN,
    SolutionOrderByGlobal,
    SubmissionStatus,
    SubmitSolutionParams,
    UpdateNoteParams,
)


class TestEnums:
    """Test enum definitions."""

    def test_difficulty_values(self):
        assert Difficulty.EASY == "EASY"
        assert Difficulty.MEDIUM == "MEDIUM"
        assert Difficulty.HARD == "HARD"

    def test_submission_status_values(self):
        assert SubmissionStatus.AC == "AC"
        assert SubmissionStatus.WA == "WA"

    def test_note_order_by_values(self):
        assert NoteOrderBy.ASCENDING == "ASCENDING"
        assert NoteOrderBy.DESCENDING == "DESCENDING"

    def test_solution_order_by_cn_values(self):
        assert SolutionOrderByCN.DEFAULT == "DEFAULT"
        assert SolutionOrderByCN.MOST_UPVOTE == "MOST_UPVOTE"
        assert SolutionOrderByCN.HOT == "HOT"

    def test_solution_order_by_global_values(self):
        assert SolutionOrderByGlobal.HOT == "HOT"
        assert SolutionOrderByGlobal.MOST_RECENT == "MOST_RECENT"
        assert SolutionOrderByGlobal.MOST_VOTES == "MOST_VOTES"


class TestGetProblemParams:
    """Test GetProblemParams model."""

    def test_valid_params(self):
        params = GetProblemParams(title_slug="two-sum")
        assert params.title_slug == "two-sum"

    def test_required_field(self):
        with pytest.raises(ValidationError):
            GetProblemParams()


class TestSearchProblemsParams:
    """Test SearchProblemsParams model."""

    def test_default_params(self):
        params = SearchProblemsParams()
        assert params.category == "all-code-essentials"
        assert params.tags == []
        assert params.difficulty is None
        assert params.search_keywords is None
        assert params.limit == 10
        assert params.offset == 0

    def test_custom_params(self):
        params = SearchProblemsParams(
            tags=["array", "dynamic-programming"],
            difficulty=Difficulty.MEDIUM,
            limit=20,
        )
        assert params.tags == ["array", "dynamic-programming"]
        assert params.difficulty == Difficulty.MEDIUM
        assert params.limit == 20

    def test_limit_validation(self):
        with pytest.raises(ValidationError):
            SearchProblemsParams(limit=0)  # min is 1

        with pytest.raises(ValidationError):
            SearchProblemsParams(limit=101)  # max is 100


class TestGetUserProfileParams:
    """Test GetUserProfileParams model."""

    def test_valid_params(self):
        params = GetUserProfileParams(username="testuser")
        assert params.username == "testuser"

    def test_required_field(self):
        with pytest.raises(ValidationError):
            GetUserProfileParams()


class TestGetRecentSubmissionsParams:
    """Test GetRecentSubmissionsParams model."""

    def test_default_params(self):
        params = GetRecentSubmissionsParams(username="testuser")
        assert params.username == "testuser"
        assert params.limit == 10

    def test_custom_limit(self):
        params = GetRecentSubmissionsParams(username="testuser", limit=50)
        assert params.limit == 50


class TestGetAllSubmissionsParams:
    """Test GetAllSubmissionsParams model."""

    def test_default_params(self):
        params = GetAllSubmissionsParams()
        assert params.limit == 20
        assert params.offset == 0
        assert params.question_slug is None
        assert params.lang is None
        assert params.status is None
        assert params.last_key is None

    def test_with_filters(self):
        params = GetAllSubmissionsParams(
            question_slug="two-sum",
            lang="python3",
            status=SubmissionStatus.AC,
        )
        assert params.question_slug == "two-sum"
        assert params.lang == "python3"
        assert params.status == SubmissionStatus.AC


class TestGetUserProgressParams:
    """Test GetUserProgressParams model."""

    def test_default_params(self):
        params = GetUserProgressParams()
        assert params.offset == 0
        assert params.limit == 100
        assert params.question_status is None
        assert params.difficulty is None

    def test_with_filters(self):
        params = GetUserProgressParams(
            question_status="SOLVED",
            difficulty=["EASY", "MEDIUM"],
        )
        assert params.question_status == "SOLVED"
        assert params.difficulty == ["EASY", "MEDIUM"]


class TestListSolutionsParams:
    """Test ListSolutionsParams model."""

    def test_valid_params(self):
        params = ListSolutionsParams(question_slug="two-sum")
        assert params.question_slug == "two-sum"
        assert params.limit == 10
        assert params.skip == 0

    def test_required_field(self):
        with pytest.raises(ValidationError):
            ListSolutionsParams()


class TestRunCodeParams:
    """Test RunCodeParams model."""

    def test_valid_params(self):
        params = RunCodeParams(
            title_slug="two-sum",
            lang="python3",
            typed_code="def twoSum(nums, target): pass",
        )
        assert params.title_slug == "two-sum"
        assert params.lang == "python3"
        assert params.data_input == ""
        assert params.timeout_ms == 120_000
        assert params.poll_interval_ms == 1_500

    def test_custom_params(self):
        params = RunCodeParams(
            title_slug="two-sum",
            lang="python3",
            typed_code="def twoSum(nums, target): pass",
            data_input="[2,7,11,15]\n9",
            timeout_ms=60_000,
        )
        assert params.data_input == "[2,7,11,15]\n9"
        assert params.timeout_ms == 60_000


class TestSubmitSolutionParams:
    """Test SubmitSolutionParams model."""

    def test_valid_params(self):
        params = SubmitSolutionParams(
            title_slug="two-sum",
            lang="python3",
            typed_code="def twoSum(nums, target): pass",
        )
        assert params.title_slug == "two-sum"
        assert params.timeout_ms == 120_000


class TestNoteParams:
    """Test note-related parameter models."""

    def test_create_note_params(self):
        params = CreateNoteParams(
            question_id="1",
            content="# Solution\nThis is a note.",
            summary="My solution",
        )
        assert params.question_id == "1"
        assert params.content == "# Solution\nThis is a note."
        assert params.summary == "My solution"

    def test_update_note_params(self):
        params = UpdateNoteParams(
            note_id="123",
            content="Updated content",
            summary="Updated summary",
        )
        assert params.note_id == "123"
        assert params.content == "Updated content"
