"""Shared pytest fixtures."""

from __future__ import annotations

import pytest

from company_cli.context import reset_api_cache
from company_core.runtime_bridge import configure_runtime_factory, reset_runtime_factory


@pytest.fixture(autouse=True)
def _reset_cli_api_cache() -> None:
    from runtime_engine.factory import create_runtime

    configure_runtime_factory(create_runtime)
    reset_api_cache()
    yield
    reset_api_cache()
    reset_runtime_factory()
