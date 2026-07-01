"""Capability routing tests."""

from pathlib import Path

from ai_execution.capabilities import CapabilityResolver
from ai_execution.factory import create_platform

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_capability_resolver_selects_cursor() -> None:
    platform = create_platform(REPO_ROOT)
    resolver = platform._resolver  # noqa: SLF001
    provider = resolver.select_provider(["planning", "reasoning"])
    assert provider.provider_id == "cursor"


def test_phase_capabilities_mapping() -> None:
    platform = create_platform(REPO_ROOT)
    resolver = platform._resolver  # noqa: SLF001
    caps = resolver.resolve_for_phase("architecture")
    assert "documentation" in caps
    provider = resolver.select_provider(caps)
    assert provider.provider_id in ("cursor", "scaffold")
