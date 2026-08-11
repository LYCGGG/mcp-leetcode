"""Configuration management: YAML file + environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

import yaml


@dataclass(frozen=True)
class AuthConfig:
    session: str = ""
    csrf_token: str = ""


@dataclass(frozen=True)
class CacheConfig:
    enabled: bool = True
    ttl_seconds: int = 300


@dataclass(frozen=True)
class LoggingConfig:
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


@dataclass(frozen=True)
class Config:
    site: Literal["cn", "global"] = "cn"
    auth: AuthConfig = field(default_factory=AuthConfig)
    cache: CacheConfig = field(default_factory=CacheConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)

    @property
    def is_cn(self) -> bool:
        return self.site == "cn"

    @property
    def base_url(self) -> str:
        return "https://leetcode.cn" if self.is_cn else "https://leetcode.com"

    @property
    def is_authenticated(self) -> bool:
        return bool(self.auth.session)


def _find_config_file() -> Path | None:
    """Search for config.yaml in cwd and parents."""
    candidates = [
        Path.cwd() / "config.yaml",
        Path.cwd() / "config.yml",
    ]
    # Also check next to the package
    pkg_dir = Path(__file__).resolve().parent.parent.parent
    candidates.append(pkg_dir / "config.yaml")
    candidates.append(pkg_dir / "config.yml")

    for p in candidates:
        if p.is_file():
            return p
    return None


def _load_yaml(path: Path) -> dict:
    """Load YAML config file and return as dict."""
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _deep_merge(base: dict, override: dict) -> dict:
    """Recursively merge override into base."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _apply_env_overrides(raw: dict) -> dict:
    """Apply environment variable overrides onto a raw config dict."""
    env_site = os.environ.get("LEETCODE_SITE")
    if env_site:
        raw["site"] = env_site

    env_session = os.environ.get("LEETCODE_SESSION")
    if env_session:
        raw.setdefault("auth", {})["session"] = env_session

    env_csrf = os.environ.get("LEETCODE_CSRF")
    if env_csrf:
        raw.setdefault("auth", {})["csrf_token"] = env_csrf

    env_log = os.environ.get("LEETCODE_LOG_LEVEL")
    if env_log:
        raw.setdefault("logging", {})["level"] = env_log

    return raw


def _dict_to_config(raw: dict) -> Config:
    """Convert a raw dict to a validated Config object."""
    auth_raw = raw.get("auth", {})
    cache_raw = raw.get("cache", {})
    log_raw = raw.get("logging", {})

    site = raw.get("site", "cn")
    if site not in ("cn", "global"):
        site = "cn"

    return Config(
        site=site,
        auth=AuthConfig(
            session=auth_raw.get("session", ""),
            csrf_token=auth_raw.get("csrf_token", ""),
        ),
        cache=CacheConfig(
            enabled=cache_raw.get("enabled", True),
            ttl_seconds=cache_raw.get("ttl_seconds", 300),
        ),
        logging=LoggingConfig(
            level=log_raw.get("level", "INFO"),
        ),
    )


def load_config(config_path: Path | None = None) -> Config:
    """Load configuration from YAML file and environment variables.

    Priority: environment variables > YAML file > defaults.
    """
    raw: dict = {}

    if config_path is None:
        config_path = _find_config_file()

    if config_path and config_path.is_file():
        raw = _load_yaml(config_path)

    raw = _apply_env_overrides(raw)
    return _dict_to_config(raw)
