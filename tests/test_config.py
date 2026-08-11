"""Unit tests for config.py."""

from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from leetcode_mcp.config import (
    AuthConfig,
    CacheConfig,
    Config,
    LoggingConfig,
    load_config,
)


class TestAuthConfig:
    """Test AuthConfig dataclass."""

    def test_default_values(self):
        config = AuthConfig()
        assert config.session == ""
        assert config.csrf_token == ""

    def test_custom_values(self):
        config = AuthConfig(session="test_session", csrf_token="test_csrf")
        assert config.session == "test_session"
        assert config.csrf_token == "test_csrf"


class TestCacheConfig:
    """Test CacheConfig dataclass."""

    def test_default_values(self):
        config = CacheConfig()
        assert config.enabled is True
        assert config.ttl_seconds == 300

    def test_custom_values(self):
        config = CacheConfig(enabled=False, ttl_seconds=60)
        assert config.enabled is False
        assert config.ttl_seconds == 60


class TestLoggingConfig:
    """Test LoggingConfig dataclass."""

    def test_default_values(self):
        config = LoggingConfig()
        assert config.level == "INFO"

    def test_custom_values(self):
        config = LoggingConfig(level="DEBUG")
        assert config.level == "DEBUG"


class TestConfig:
    """Test Config dataclass."""

    def test_default_values(self):
        config = Config()
        assert config.site == "cn"
        assert config.is_cn is True
        assert config.base_url == "https://leetcode.cn"
        assert config.is_authenticated is False

    def test_global_site(self):
        config = Config(site="global")
        assert config.is_cn is False
        assert config.base_url == "https://leetcode.com"

    def test_authenticated(self):
        config = Config(auth=AuthConfig(session="test_session"))
        assert config.is_authenticated is True

    def test_not_authenticated(self):
        config = Config(auth=AuthConfig())
        assert config.is_authenticated is False


class TestLoadConfig:
    """Test load_config function."""

    def test_default_config(self):
        config = load_config(Path("/nonexistent/config.yaml"))
        assert config.site == "cn"
        assert config.cache.enabled is True
        assert config.logging.level == "INFO"

    def test_yaml_config(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
site: global
auth:
  session: test_session
  csrf_token: test_csrf
cache:
  enabled: false
  ttl_seconds: 60
logging:
  level: DEBUG
""")
        config = load_config(config_file)
        assert config.site == "global"
        assert config.auth.session == "test_session"
        assert config.auth.csrf_token == "test_csrf"
        assert config.cache.enabled is False
        assert config.cache.ttl_seconds == 60
        assert config.logging.level == "DEBUG"

    def test_env_overrides(self, tmp_path, monkeypatch):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
site: global
""")
        monkeypatch.setenv("LEETCODE_SITE", "cn")
        monkeypatch.setenv("LEETCODE_SESSION", "env_session")
        monkeypatch.setenv("LEETCODE_CSRF", "env_csrf")

        config = load_config(config_file)
        assert config.site == "cn"
        assert config.auth.session == "env_session"
        assert config.auth.csrf_token == "env_csrf"

    def test_invalid_site_fallback(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
site: invalid_site
""")
        config = load_config(config_file)
        assert config.site == "cn"  # Falls back to default
