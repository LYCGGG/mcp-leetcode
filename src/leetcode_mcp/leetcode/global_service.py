"""LeetCode Global (leetcode.com) service implementation."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger

from ..client import LeetCodeClient
from ..config import Config
from ..exceptions import AuthenticationError, NotFoundError
from ..graphql.lc_global.search_problems import SEARCH_PROBLEMS_QUERY
from ..graphql.lc_global.solution_articles import SOLUTION_ARTICLES_QUERY
from ..graphql.lc_global.solution_detail import SOLUTION_DETAIL_QUERY
from .base_service import LeetCodeBaseService


class LeetCodeGlobalService(LeetCodeBaseService):
    """LeetCode Global API service implementation."""

    def __init__(self, client: LeetCodeClient, config: Config) -> None:
        self._client = client
        self._config = config
        self._origin = "https://leetcode.com"

    def _require_auth(self, action: str) -> None:
        if not self.is_authenticated():
            raise AuthenticationError(f"Authentication required to {action}")

    # ── User ─────────────────────────────────────────────────────

    async def fetch_user_profile(self, username: str) -> Any:
        data = await self._client.graphql(
            query="""
            query getUserProfile($username: String!) {
                matchedUser(username: $username) {
                    username
                    profile {
                        realName userAvatar countryName company school ranking
                    }
                    githubUrl
                    submitStats {
                        totalSubmissionNum { difficulty count submissions }
                    }
                }
            }
            """,
            variables={"username": username},
        )
        matched = (data or {}).get("matchedUser")
        if not matched:
            return None
        profile = matched.get("profile") or {}
        return {
            "username": matched.get("username"),
            "realName": profile.get("realName"),
            "userAvatar": profile.get("userAvatar"),
            "countryName": profile.get("countryName"),
            "githubUrl": matched.get("githubUrl"),
            "company": profile.get("company"),
            "school": profile.get("school"),
            "ranking": profile.get("ranking"),
            "totalSubmissionNum": (matched.get("submitStats") or {}).get("totalSubmissionNum"),
        }

    async def fetch_user_status(self) -> Any:
        self._require_auth("fetch user status")
        data = await self._client.graphql(
            query="query { userStatus { isSignedIn username avatar isAdmin } }"
        )
        status = (data or {}).get("userStatus") or {}
        return {
            "isSignedIn": status.get("isSignedIn", False),
            "username": status.get("username", ""),
            "avatar": status.get("avatar", ""),
            "isAdmin": status.get("isAdmin", False),
        }

    async def fetch_user_all_submissions(
        self,
        offset: int,
        limit: int,
        question_slug: str | None = None,
        last_key: str | None = None,
        lang: str | None = None,
        status: str | None = None,
    ) -> Any:
        self._require_auth("fetch user submissions")
        data = await self._client.graphql(
            query="""
            query submissionList($offset: Int!, $limit: Int!, $questionSlug: String) {
                submissionList(offset: $offset, limit: $limit, questionSlug: $questionSlug) {
                    submissions {
                        id title status lang runtime url memory
                    }
                }
            }
            """,
            variables={
                "offset": offset,
                "limit": limit,
                "questionSlug": question_slug,
            },
        )
        return (data or {}).get("submissionList") or {"submissions": []}

    async def fetch_user_progress_question_list(
        self,
        offset: int = 0,
        limit: int = 20,
        question_status: str | None = None,
        difficulty: list[str] | None = None,
    ) -> Any:
        self._require_auth("fetch user progress")
        data = await self._client.graphql(
            query="""
            query userProgressQuestions($filters: UserProgressQuestionsFilterInput) {
                userProgressQuestions(filters: $filters) {
                    questions {
                        translatedTitle titleSlug questionId difficulty
                        lastSubmittedAt numSubmittedTotalTopics
                    }
                    totalNum
                }
            }
            """,
            variables={
                "filters": {
                    "skip": offset,
                    "limit": limit,
                    "questionStatus": question_status,
                    "difficulty": difficulty,
                }
            },
        )
        return (data or {}).get("userProgressQuestions")

    async def fetch_user_recent_submissions(
        self, username: str, limit: int | None = None
    ) -> Any:
        data = await self._client.graphql(
            query="""
            query recentSubmissions($username: String!, $limit: Int) {
                recentSubmissionList(username: $username, limit: $limit) {
                    id title titleSlug timestamp statusDisplay lang
                }
            }
            """,
            variables={"username": username, "limit": limit},
        )
        return (data or {}).get("recentSubmissionList") or []

    async def fetch_user_recent_ac_submissions(
        self, username: str, limit: int | None = None
    ) -> Any:
        data = await self._client.graphql(
            query="""
            query recentACSubmissions($username: String!, $limit: Int) {
                recentAcSubmissionList(username: $username, limit: $limit) {
                    id title titleSlug time timestamp statusDisplay lang
                }
            }
            """,
            variables={"username": username, "limit": limit},
        )
        return (data or {}).get("recentAcSubmissionList") or []

    async def fetch_user_submission_detail(self, submission_id: int) -> Any:
        self._require_auth("fetch submission detail")
        data = await self._client.graphql(
            query="""
            query submissionDetail($submissionId: ID!) {
                submissionDetail(submissionId: $submissionId) {
                    code
                    status { status runtime memory }
                    lang { name verboseName }
                    question { questionId titleSlug }
                }
            }
            """,
            variables={"submissionId": str(submission_id)},
        )
        return (data or {}).get("submissionDetail")

    async def fetch_user_contest_ranking(
        self, username: str, attended: bool = True
    ) -> Any:
        data = await self._client.graphql(
            query="""
            query userContestRankingInfo($username: String!) {
                userContestRanking(username: $username) {
                    attendedContestsCount
                    rating
                    globalRanking
                    totalParticipants
                    topPercentage
                }
                userContestRankingHistory(username: $username) {
                    attended trendDirection contest { title startTime }
                    ranking rating
                }
            }
            """,
            variables={"username": username},
        )
        history = (data or {}).get("userContestRankingHistory") or []
        if attended:
            history = [h for h in history if h and h.get("attended")]
        return {
            "userContestRanking": (data or {}).get("userContestRanking"),
            "userContestRankingHistory": history,
        }

    # ── Problem ──────────────────────────────────────────────────

    async def fetch_daily_challenge(self) -> Any:
        data = await self._client.graphql(
            query="""
            query questionOfToday {
                activeDailyCodingChallengeQuestion {
                    date link
                    question {
                        questionId titleSlug title difficulty
                        topicTags { slug }
                    }
                }
            }
            """
        )
        challenge = (data or {}).get("activeDailyCodingChallengeQuestion")
        if not challenge:
            return None
        question = challenge.get("question") or {}
        return {
            "date": challenge.get("date"),
            "link": challenge.get("link"),
            "questionId": question.get("questionId"),
            "title": question.get("title"),
            "titleSlug": question.get("titleSlug"),
            "difficulty": question.get("difficulty"),
            "topicTags": [t.get("slug") for t in (question.get("topicTags") or [])],
        }

    async def fetch_problem(self, title_slug: str) -> Any:
        data = await self._client.graphql(
            query="""
            query questionDetail($titleSlug: String!) {
                question(titleSlug: $titleSlug) {
                    questionId title titleSlug content difficulty
                    topicTags { slug name }
                    codeSnippets { lang langSlug code }
                    hints sampleTestCase
                    exampleTestcases
                    similarQuestions
                }
            }
            """,
            variables={"titleSlug": title_slug},
        )
        return (data or {}).get("question")

    async def fetch_problem_simplified(self, title_slug: str) -> Any:
        problem = await self.fetch_problem(title_slug)
        if not problem:
            raise NotFoundError(f"Problem '{title_slug}' not found")

        topic_tags = [t.get("slug") for t in (problem.get("topicTags") or [])]
        code_snippets = [
            s
            for s in (problem.get("codeSnippets") or [])
            if s.get("langSlug") in ("cpp", "python3", "java")
        ]

        similar: list[dict] = []
        raw = problem.get("similarQuestions")
        if raw:
            try:
                all_q = json.loads(raw) if isinstance(raw, str) else raw
                similar = [
                    {"titleSlug": q["titleSlug"], "difficulty": q["difficulty"]}
                    for q in all_q[:3]
                ]
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                logger.warning("Failed to parse similarQuestions: {}", e)

        return {
            "titleSlug": title_slug,
            "questionId": problem.get("questionId"),
            "title": problem.get("title"),
            "content": problem.get("content"),
            "difficulty": problem.get("difficulty"),
            "topicTags": topic_tags,
            "codeSnippets": code_snippets,
            "exampleTestcases": problem.get("exampleTestcases"),
            "hints": problem.get("hints"),
            "similarQuestions": similar,
        }

    async def search_problems(
        self,
        category: str | None = None,
        tags: list[str] | None = None,
        difficulty: str | None = None,
        limit: int = 10,
        offset: int = 0,
        search_keywords: str | None = None,
    ) -> Any:
        filters: dict[str, Any] = {}
        if difficulty:
            filters["difficulty"] = difficulty.upper()
        if tags:
            filters["tags"] = tags
        if search_keywords:
            filters["searchKeywords"] = search_keywords

        data = await self._client.graphql(
            query=SEARCH_PROBLEMS_QUERY,
            variables={
                "categorySlug": category,
                "limit": limit,
                "skip": offset,
                "filters": filters,
            },
        )

        question_list = (data or {}).get("problemsetQuestionList")
        if not question_list:
            return {"total": 0, "questions": []}

        return {
            "total": question_list.get("total", 0),
            "questions": [
                {
                    "title": q.get("title"),
                    "titleSlug": q.get("titleSlug"),
                    "difficulty": q.get("difficulty"),
                    "acRate": q.get("acRate"),
                    "topicTags": [t.get("slug") for t in (q.get("topicTags") or [])],
                }
                for q in (question_list.get("questions") or [])
            ],
        }

    # ── Solution ─────────────────────────────────────────────────

    async def fetch_question_solution_articles(
        self, question_slug: str, options: dict[str, Any] | None = None
    ) -> Any:
        opts = options or {}
        data = await self._client.graphql(
            query=SOLUTION_ARTICLES_QUERY,
            variables={
                "questionSlug": question_slug,
                "first": opts.get("limit", 5),
                "skip": opts.get("skip", 0),
                "orderBy": opts.get("orderBy", "HOT"),
                "userInput": opts.get("userInput"),
                "tagSlugs": opts.get("tagSlugs", []),
            },
        )

        articles_data = (data or {}).get("ugcArticleSolutionArticles")
        if not articles_data:
            return {"totalNum": 0, "hasNextPage": False, "articles": []}

        page_info = articles_data.get("pageInfo") or {}
        edges = articles_data.get("edges") or []
        articles = []
        for edge in edges:
            node = edge.get("node") if edge else None
            if not node or not node.get("canSee"):
                continue
            if node.get("topicId") and node.get("slug"):
                node["articleUrl"] = (
                    f"https://leetcode.com/problems/{question_slug}"
                    f"/solutions/{node['topicId']}/{node['slug']}"
                )
            articles.append(node)

        return {
            "totalNum": articles_data.get("totalNum", 0),
            "hasNextPage": page_info.get("hasNextPage", False),
            "articles": articles,
        }

    async def fetch_solution_article_detail(self, identifier: str) -> Any:
        data = await self._client.graphql(
            query=SOLUTION_DETAIL_QUERY,
            variables={"topicId": identifier},
        )
        return (data or {}).get("ugcArticleSolutionArticle")

    # ── Note (not supported on Global) ───────────────────────────

    async def fetch_user_notes(self, **kwargs: Any) -> Any:
        raise NotImplementedError("Notes feature is not supported on LeetCode Global")

    async def fetch_notes_by_question_id(self, **kwargs: Any) -> Any:
        raise NotImplementedError("Notes feature is not supported on LeetCode Global")

    async def create_user_note(self, **kwargs: Any) -> Any:
        raise NotImplementedError("Notes feature is not supported on LeetCode Global")

    async def update_user_note(self, **kwargs: Any) -> Any:
        raise NotImplementedError("Notes feature is not supported on LeetCode Global")

    # ── Code Execution ───────────────────────────────────────────

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
        self._require_auth("run code")
        start_path = f"/problems/{title_slug}/interpret_solution/"
        start = await self._client.post_json(
            start_path,
            {
                "data_input": data_input,
                "lang": lang,
                "question_id": question_id,
                "typed_code": typed_code,
            },
        )

        interpret_id = start.get("interpret_id")
        if not interpret_id:
            raise NotFoundError("No interpret_id in run response")

        check_path = f"/submissions/detail/{interpret_id}/check/"
        check = await self._client.poll_check(
            check_path, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms
        )
        return {"start": start, "checkUrl": check_path, "check": check}

    async def submit_solution(
        self,
        title_slug: str,
        question_id: str,
        lang: str,
        typed_code: str,
        timeout_ms: float = 120_000,
        poll_interval_ms: float = 1_500,
    ) -> Any:
        self._require_auth("submit solution")
        start_path = f"/problems/{title_slug}/submit/"
        start = await self._client.post_json(
            start_path,
            {
                "lang": lang,
                "question_id": question_id,
                "typed_code": typed_code,
            },
        )

        submission_id = start.get("submission_id")
        if not submission_id:
            raise NotFoundError("No submission_id in submit response")

        check_path = f"/submissions/detail/{submission_id}/check/"
        check = await self._client.poll_check(
            check_path, timeout_ms=timeout_ms, poll_interval_ms=poll_interval_ms
        )
        return {"start": start, "checkUrl": check_path, "check": check}

    # ── Meta ─────────────────────────────────────────────────────

    def is_authenticated(self) -> bool:
        return self._config.is_authenticated

    def is_cn(self) -> bool:
        return False
