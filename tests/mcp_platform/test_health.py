"""MCP Platform health check tests."""

from __future__ import annotations

from pathlib import Path

from company_core.config.loader import discover_framework_root_from_path
from mcp_platform.health import (
    check_context7,
    check_npx_available,
    check_sequential_thinking,
    run_health_checks,
)


def test_check_npx_available() -> None:
    result = check_npx_available()
    assert result.check == "health"
    assert isinstance(result.passed, bool)


def test_check_context7() -> None:
    result = check_context7()
    assert result.passed is True


def test_check_sequential_thinking_skip_when_not_installed() -> None:
    root = discover_framework_root_from_path()
    assert root is not None
    result = check_sequential_thinking(root)
    assert result.check == "health"


def test_run_health_checks_smoke() -> None:
    root = discover_framework_root_from_path()
    assert root is not None
    results = run_health_checks(root=root)
    assert len(results) >= 2
    assert all(r.check == "health" for r in results)
