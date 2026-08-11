"""Integration tests for server.py."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from leetcode_mcp.server import create_mcp_server


class TestCreateMcpServer:
    """Test create_mcp_server function."""

    def test_server_creation(self):
        """Test that server is created successfully."""
        server = create_mcp_server()
        assert server is not None
        assert server.name == "mcp-leetcode"

    def test_tools_registered(self):
        """Test that all tools are registered."""
        server = create_mcp_server()
        tools = server._tool_manager._tools

        expected_tools = [
            "get_daily_challenge",
            "get_problem",
            "get_problem_solution",
            "get_recent_ac_submissions",
            "get_user_contest_ranking",
            "get_user_profile",
            "list_problem_solutions",
            "search_problems",
        ]

        for tool_name in expected_tools:
            assert tool_name in tools, f"Tool {tool_name} not registered"

    def test_resources_registered(self):
        """Test that resources are registered."""
        server = create_mcp_server()
        resources = server._resource_manager._resources

        expected_resources = [
            "categories://problems/all",
            "tags://problems/all",
            "langs://problems/all",
        ]

        for resource_uri in expected_resources:
            assert resource_uri in resources, f"Resource {resource_uri} not registered"

    def test_server_has_correct_name(self):
        """Test server name."""
        server = create_mcp_server()
        assert server.name == "mcp-leetcode"
