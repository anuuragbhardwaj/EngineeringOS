"""Shared CLI context and utilities."""

from __future__ import annotations

from functools import lru_cache

from company_core import FrameworkAPI

from company_cli.version import CLI_VERSION


@lru_cache(maxsize=1)
def get_api() -> FrameworkAPI:
    return FrameworkAPI(cli_version=CLI_VERSION)


def reset_api_cache() -> None:
    """Clear cached FrameworkAPI (for tests and instance switches)."""
    get_api.cache_clear()
