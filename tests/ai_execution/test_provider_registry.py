"""Provider registry tests."""

from pathlib import Path

from ai_execution.factory import create_platform
from ai_execution.registry.provider_registry import ProviderRegistry
from ai_execution.providers.scaffold import ScaffoldProvider

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG = REPO_ROOT / "packages" / "ai_execution" / "providers.yaml"


def test_provider_registration() -> None:
    registry = ProviderRegistry()
    registry.load_config(CONFIG)
    registry.register(ScaffoldProvider())
    assert "scaffold" in registry.list_providers()


def test_platform_registers_all_providers() -> None:
    platform = create_platform(REPO_ROOT, CONFIG)
    providers = platform._registry.list_providers()  # noqa: SLF001
    assert "cursor" in providers
    assert "scaffold" in providers
    assert "openai" in providers


def test_health_diagnostics() -> None:
    platform = create_platform(REPO_ROOT, CONFIG)
    diag = platform.diagnostics()
    assert diag["default"] == "cursor"
    assert diag["fallback"] == "scaffold"
    assert diag["providers"]["scaffold"]["available"] is True
