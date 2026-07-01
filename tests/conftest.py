"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from company_cli.context import reset_api_cache


@pytest.fixture(autouse=True)
def _reset_cli_api_cache() -> None:
    reset_api_cache()
    yield
    reset_api_cache()
