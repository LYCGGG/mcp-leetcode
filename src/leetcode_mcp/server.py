"""MCP Server entry point: CLI parsing, service creation, tool/resource registration."""

from __future__ import annotations

import sys

from loguru import logger
from mcp.server.fastmcp import FastMCP

from .cache import configure_cache
from .config import load_config
from .leetcode.service_factory import create_service
from .resources.problem_resources import register_problem_resources
from .resources.solution_resources import register_solution_resources
from .tools.note_tools import register_note_tools
from .tools.problem_tools import register_problem_tools
from .tools.solution_tools import register_solution_tools
from .tools.submission_tools import register_submission_tools
from .tools.user_tools import register_user_tools


def _setup_logging(level: str) -> None:
    """Configure loguru based on config level."""
    logger.remove()
    logger.add(sys.stderr, level=level, format="{time:HH:mm:ss} | {level:<7} | {message}")


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with all tools and resources."""
    config = load_config()
    _setup_logging(config.logging.level)

    if config.cache.enabled:
        configure_cache(ttl=config.cache.ttl_seconds)

    logger.info("Starting mcp-leetcode | site={} | auth={}", config.site, config.is_authenticated)

    service, client = create_service(config)

    server = FastMCP(
        name="mcp-leetcode",
    )

    # Register tools
    register_problem_tools(server, service)
    register_user_tools(server, service)
    register_submission_tools(server, service)
    register_solution_tools(server, service)
    register_note_tools(server, service)

    # Register resources
    register_problem_resources(server, service)
    register_solution_resources(server, service)

    return server


def main() -> None:
    """CLI entry point for `mcp-leetcode` command."""
    server = create_mcp_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
