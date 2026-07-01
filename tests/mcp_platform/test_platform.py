"""MCP Platform smoke and resolution tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from company_core.config.loader import discover_framework_root_from_path
from mcp_platform.resolver import is_usable, resolve_capability
from mcp_platform.validator import validate_all, validate_registry


@pytest.fixture
def framework_root() -> Path:
    root = discover_framework_root_from_path()
    assert root is not None
    return root


def test_discover_framework_root_from_path() -> None:
    root = discover_framework_root_from_path()
    assert root is not None
    assert (root / "workflow.yaml").is_file()
    assert (root / "mcp" / "registry.yaml").is_file()


def test_validate_registry_passes(framework_root: Path) -> None:
    results = validate_registry(framework_root)
    assert results
    assert all(r.passed for r in results), [r.message for r in results if not r.passed]


def test_validate_all_smoke(framework_root: Path) -> None:
    results = validate_all(framework_root)
    failed = [r for r in results if not r.passed]
    assert not failed, [r.message for r in failed]


def test_resolve_documentation_capability(framework_root: Path) -> None:
    resolution = resolve_capability("documentation-lookup", framework_root)
    assert resolution.mcp_id is not None
    assert resolution.source in ("primary", "fallback", "unavailable")


def test_is_usable_installed() -> None:
    assert is_usable("installed") is True
    assert is_usable("missing") is False
