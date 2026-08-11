"""LeetCode CN (leetcode.cn) service implementation."""

from __future__ import annotations

import json
from typing import Any

from loguru import logger

from ..client import LeetCodeClient
from ..config import Config
from ..exceptions import AuthenticationError, NotFoundError
from ..graphql.cn.note_queries import (
    NOTE_AGGREGATE_QUERY,
    NOTE_BY_QUESTION_ID_QUERY,
    NOTE_CREATE_MUTATION,
    NOTE_UPDATE_MUTATION,
)
from ..graphql.cn.search_problems import SEARCH_PROBLEMS_QUERY
from ..graphql.cn.solution_articles import SOLUTION_ARTICLES_QUERY
from ..graphql.cn.solution_detail import SOLUTION_DETAIL_QUERY
from .base_service import LeetCodeBaseService


class LeetCodeCNService(LeetCodeBaseService):
    """LeetCode CN API service implementation."""

    def __init__(self, client: LeetCodeClient, config: Config) -> None:
        self._client = client
        self._config = config
        self._origin = "https://leetcode.cn"

    # ── Internal helpers ─────────────────────────────────────────

    def _require_auth(self, action: str) -> None:
        if not self.is_authenticated():
            raise AuthenticationError(f"Authentication required to {action}")

    # ── User ─────────────────────────────────────────────────────

    async def fetch_user_profile(self, username: str) -> Any:
        data = await self._client.graphql(
            query="""
            query userProfilePublicProfile($userSlug: String!) {
                userProfilePublicProfile(userSlug: $userSlug) {
                    siteRanking
                    profile {
                        userSlug
                        realName
                        userAvatar
                        globalLocation { country city }
                        school
                        socialAccounts { profileUrl }
                        skillSet {
                            topics { slug }
                            topicAreaScores { topicArea { slug } score }
                        }
                    }
                }
                userProfileUserQuestionProgress(userSlug: $userSlug) {
                    numAcceptedQuestions { difficulty count }
                    numFailedQuestions { difficulty count }
                    numUntouchedQuestions { difficulty count }
                }
            }
            """,
            variables={"userSlug": username},
        )
        if not data:
            return None

        public_profile = data.get("userProfilePublicProfile") or {}
        profile = public_profile.get("profile") or {}
        skill_set = profile.get("skillSet") or {}
        topics = skill_set.get("topics") or []
        scores = skill_set.get("topicAreaScores") or []
        social = profile.get("socialAccounts") or []

        location = profile.get("globalLocation") or {}
        return {
            "username": profile.get("userSlug"),
            "questionProgress": data.get("userProfileUserQuestionProgress"),
            "siteRanking": public_profile.get("siteRanking"),
            "profile": {
                "userSlug": profile.get("userSlug"),
                "realName": profile.get("realName"),
                "userAvatar": profile.get("userAvatar"),
                "globalLocation": f"{location.get('city', '')}, {location.get('country', '')}".strip(", "),
                "school": profile.get("school"),
                "socialAccounts": [a for a in social if a.get("profileUrl")],
                "skillSet": {
                    "topics": [t.get("slug") for t in topics],
                    "topicAreaScores": [
                        {
                            "slug": (s.get("topicArea") or {}).get("slug"),
                            "score": s.get("score"),
                        }
                        for s in scores
                    ],
                },
            },
        }

    async def fetch_user_status(self) -> Any:
        self._require_auth("fetch user status")
        data = await self._client.graphql(
            query="query { userStatus { isSignedIn username avatar isAdmin useTranslation } }"
        )
        status = (data or {}).get("userStatus") or {}
        return {
            "isSignedIn": status.get("isSignedIn", False),
            "username": status.get("username", ""),
            "avatar": status.get("avatar", ""),
            "isAdmin": status.get("isAdmin", False),
            "useTranslation": status.get("useTranslation", False),
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
        return await self._client.graphql(
            query="""
            query submissionList(
                $offset: Int!, $limit: Int!, $lastKey: String,
                $questionSlug: String, $lang: String, $status: SubmissionStatusEnum
            ) {
                submissionList(
                    offset: $offset, limit: $limit, lastKey: $lastKey,
                    questionSlug: $questionSlug, lang: $lang, status: $status
                ) {
                    lastKey
                    hasNext
                    submissions {
                        id title status lang runtime url memory frontendId
                    }
                }
            }
            """,
            variables={
                "offset": offset,
                "limit": limit,
                "lastKey": last_key,
                "questionSlug": question_slug,
                "lang": lang,
                "status": status,
            },
        )

    async def fetch_user_progress_question_list(
        self,
        offset: int = 0,
        limit: int = 20,
        question_status: str | None = None,
        difficulty: list[str] | None = None,
    ) -> Any:
        self._require_auth("fetch user progress")
        return await self._client.graphql(
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

    async def fetch_user_recent_submissions(
        self, username: str, limit: int | None = None
    ) -> Any:
        raise NotImplementedError(
            "fetchUserRecentSubmissions is not supported on LeetCode CN. "
            "Use fetch_user_recent_ac_submissions instead."
        )

    async def fetch_user_recent_ac_submissions(
        self, username: str, limit: int | None = None
    ) -> Any:
        data = await self._client.graphql(
            query="""
            query recentACSubmissions($userSlug: String!) {
                recentACSubmissionList(userSlug: $userSlug) {
                    id title slug
                    timestamp
                    statusDisplay lang
                }
            }
            """,
            variables={"userSlug": username},
        )
        submissions = (data or {}).get("recentACSubmissionList") or []
        if limit:
            submissions = submissions[:limit]
        return submissions

    async def fetch_user_submission_detail(self, submission_id: int) -> Any:
        self._require_auth("fetch submission detail")
        return await self._client.graphql(
            query="""
            query submissionDetail($submissionId: ID!) {
                submissionDetail(submissionId: $submissionId) {
                    code
                    status { status runtime memory }
                    lang { name verboseName }
                    question { questionId titleSlug }
                    inputFormattedOutput
                    expectedOutput
                }
            }
            """,
            variables={"submissionId": str(submission_id)},
        )

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
            query {
                todayRecord {
                    date
                    question {
                        questionId titleSlug title difficulty
                        topicTags { slug }
                    }
                }
            }
            """
        )
        records = (data or {}).get("todayRecord") or []
        if not records:
            return None
        challenge = records[0]
        question = challenge.get("question") or {}
        return {
            "date": challenge.get("date"),
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
            return {"hasMore": False, "total": 0, "questions": []}

        return {
            "hasMore": question_list.get("hasMore", False),
            "total": question_list.get("total", 0),
            "questions": [
                {
                    "title": q.get("title"),
                    "titleCn": q.get("titleCn"),
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
                "orderBy": opts.get("orderBy", "DEFAULT"),
                "userInput": opts.get("userInput"),
                "tagSlugs": opts.get("tagSlugs", []),
            },
        )

        articles_data = (data or {}).get("questionSolutionArticles")
        if not articles_data:
            return {"totalNum": 0, "hasNextPage": False, "articles": []}

        edges = articles_data.get("edges") or []
        articles = []
        for edge in edges:
            node = edge.get("node") if edge else None
            if not node or not node.get("canSee"):
                continue
            topic = node.get("topic") or {}
            if topic.get("id") and node.get("slug"):
                node["articleUrl"] = (
                    f"https://leetcode.cn/problems/{question_slug}"
                    f"/solutions/{topic['id']}/{node['slug']}"
                )
            articles.append(node)

        page_info = articles_data.get("pageInfo") or {}
        return {
            "totalNum": articles_data.get("totalNum", 0),
            "hasNextPage": page_info.get("hasNextPage", False),
            "articles": articles,
        }

    async def fetch_solution_article_detail(self, identifier: str) -> Any:
        data = await self._client.graphql(
            query=SOLUTION_DETAIL_QUERY,
            variables={"slug": identifier},
        )
        return (data or {}).get("solutionArticle")

    # ── Note ─────────────────────────────────────────────────────

    async def fetch_user_notes(
        self,
        aggregate_type: str = "QUESTION_NOTE",
        keyword: str | None = None,
        order_by: str | None = None,
        limit: int = 20,
        skip: int = 0,
    ) -> Any:
        self._require_auth("fetch user notes")
        data = await self._client.graphql(
            query=NOTE_AGGREGATE_QUERY,
            variables={
                "aggregateType": aggregate_type,
                "keyword": keyword,
                "orderBy": order_by or "DESCENDING",
                "limit": limit,
                "skip": skip,
            },
        )
        return (data or {}).get("noteAggregateNote") or {"count": 0, "userNotes": []}

    async def fetch_notes_by_question_id(
        self, question_id: str, limit: int = 20, skip: int = 0
    ) -> Any:
        self._require_auth("fetch notes by question ID")
        data = await self._client.graphql(
            query=NOTE_BY_QUESTION_ID_QUERY,
            variables={
                "noteType": "COMMON_QUESTION",
                "questionId": question_id,
                "limit": limit,
                "skip": skip,
            },
        )
        return (data or {}).get("noteOneTargetCommonNote") or {"count": 0, "userNotes": []}

    async def create_user_note(
        self, content: str, note_type: str, target_id: str, summary: str
    ) -> Any:
        self._require_auth("create notes")
        data = await self._client.graphql(
            query=NOTE_CREATE_MUTATION,
            variables={
                "content": content,
                "noteType": note_type,
                "targetId": target_id,
                "summary": summary or "",
            },
        )
        return (data or {}).get("noteCreateCommonNote") or {"ok": False, "note": None}

    async def update_user_note(
        self, note_id: str, content: str, summary: str
    ) -> Any:
        self._require_auth("update notes")
        data = await self._client.graphql(
            query=NOTE_UPDATE_MUTATION,
            variables={
                "noteId": note_id,
                "content": content,
                "summary": summary or "",
            },
        )
        return (data or {}).get("noteUpdateUserNote") or {"ok": False, "note": None}

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
        return True
