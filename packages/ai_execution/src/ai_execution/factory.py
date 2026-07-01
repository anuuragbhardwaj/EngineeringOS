"""AI Execution Platform factory."""

from __future__ import annotations

from pathlib import Path

from ai_execution.capabilities import CapabilityResolver
from ai_execution.conversation.manager import ConversationManager
from ai_execution.platform import ExecutionPlatform
from ai_execution.providers.cursor import CursorProvider
from ai_execution.providers.placeholders import PLACEHOLDER_IDS, PlaceholderProvider
from ai_execution.providers.scaffold import ScaffoldProvider
from ai_execution.registry.provider_registry import ProviderRegistry


def discover_framework_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for directory in [current, *current.parents]:
        if (directory / "workflow.yaml").is_file() and (directory / "runtime").is_dir():
            return directory
    package_root = Path(__file__).resolve().parents[3]
    if (package_root / "workflow.yaml").is_file():
        return package_root
    raise FileNotFoundError("Cannot locate framework root")


def create_platform(
    framework_root: Path | None = None,
    providers_config: Path | None = None,
) -> ExecutionPlatform:
    root = framework_root or discover_framework_root()
    config_path = providers_config or (
        Path(__file__).resolve().parents[2] / "providers.yaml"
    )

    registry = ProviderRegistry()
    registry.load_config(config_path)

    conversations = ConversationManager()
    registry.register(ScaffoldProvider())
    registry.register(CursorProvider(root, conversations))

    for provider_id in PLACEHOLDER_IDS:
        cfg = registry._config.get(provider_id)  # noqa: SLF001 — factory bootstrap
        caps = cfg.capabilities if cfg else []
        priority = cfg.priority if cfg else 50
        registry.register(PlaceholderProvider(provider_id, caps, priority))

    resolver = CapabilityResolver(registry)
    return ExecutionPlatform(registry, conversations, resolver)
