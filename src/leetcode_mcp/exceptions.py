"""Unified exception hierarchy for LeetCode MCP."""


class LeetCodeError(Exception):
    """Base exception for all LeetCode operations."""


class AuthenticationError(LeetCodeError):
    """Raised when authentication is required but missing or invalid."""


class NotFoundError(LeetCodeError):
    """Raised when a requested resource does not exist."""


class RateLimitError(LeetCodeError):
    """Raised when the API rate limit is exceeded."""

    def __init__(self, retry_after: float | None = None):
        self.retry_after = retry_after
        msg = f"Rate limited. Retry after {retry_after}s" if retry_after else "Rate limited."
        super().__init__(msg)


class NetworkError(LeetCodeError):
    """Raised on network/HTTP failures."""


class GraphQLError(LeetCodeError):
    """Raised when a GraphQL response contains errors."""

    def __init__(self, errors: list[dict]):
        self.errors = errors
        messages = "; ".join(e.get("message", str(e)) for e in errors)
        super().__init__(f"GraphQL error: {messages}")


class SubmissionError(LeetCodeError):
    """Raised when code submission or run fails."""
