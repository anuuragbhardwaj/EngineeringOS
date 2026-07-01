"""Dynamic provider registry."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from ai_execution.errors import ProviderNotFoundError, ProviderPlaceholderError
from ai_execution.types import IExecutionProvider, ProviderConfiguration


class ProviderRegistry:
    """Register, lookup, health-check, and prioritize execution providers."""

    def __init__(self) -> None:
        self._providers: dict[str, IExecutionProvider] = {}
        self._config: dict[str, ProviderConfiguration] = {}
        self._default_provider_id = "cursor"
        self._fallback_provider_id = "scaffold"

    @property
    def default_provider_id(self) -> str:
        return self._default_provider_id

    @property
    def fallback_provider_id(self) -> str:
        return self._fallback_provider_id

    def load_config(self, path: str | Path) -> None:
        config_path = Path(path)
        if not config_path.is_file():
            return
        with config_path.open(encoding="utf-8") as handle:
            raw = yaml.safe_load(handle) or {}
        self._default_provider_id = str(raw.get("default_provider", "cursor"))
        self._fallback_provider_id = str(raw.get("fallback_provider", "scaffold"))
        for provider_id, cfg in raw.get("providers", {}).items():
            self._config[provider_id] = ProviderConfiguration(
                provider_id=provider_id,
                enabled=bool(cfg.get("enabled", False)),
                priority=int(cfg.get("priority", 0)),
                capabilities=[str(c) for c in cfg.get("capabilities", [])],
                placeholder=bool(cfg.get("placeholder", False)),
                settings=dict(cfg.get("settings", {})),
            )

    def register(self, provider: IExecutionProvider) -> None:
        self._providers[provider.provider_id] = provider

    def unregister(self, provider_id: str) -> None:
        self._providers.pop(provider_id, None)

    def get(self, provider_id: str) -> IExecutionProvider | None:
        return self._providers.get(provider_id)

    def lookup(self, provider_id: str) -> IExecutionProvider:
        provider = self.get(provider_id)
        if provider is None:
            raise ProviderNotFoundError(f"Provider not registered: {provider_id}")
        cfg = self._config.get(provider_id)
        if cfg and cfg.placeholder:
            raise ProviderPlaceholderError(
                f"Provider {provider_id} is a placeholder — not yet implemented"
            )
        return provider

    def list_providers(self) -> list[str]:
        return sorted(self._providers.keys())

    def health_all(self) -> dict[str, Any]:
        return {
            pid: {
                "available": p.health().available,
                "message": p.health().message,
                "capabilities": p.capabilities().capabilities,
                "placeholder": p.capabilities().placeholder,
            }
            for pid, p in self._providers.items()
        }

    def find_by_capabilities(
        self,
        required: list[str],
        *,
        exclude_placeholders: bool = True,
    ) -> list[IExecutionProvider]:
        matches: list[tuple[int, IExecutionProvider]] = []
        for provider_id, provider in self._providers.items():
            cfg = self._config.get(provider_id)
            if cfg and not cfg.enabled:
                continue
            caps = provider.capabilities()
            if exclude_placeholders and caps.placeholder:
                continue
            if all(cap in caps.capabilities for cap in required):
                priority = cfg.priority if cfg else caps.priority
                matches.append((priority, provider))
        matches.sort(key=lambda x: x[0], reverse=True)
        return [p for _, p in matches]

    def get_default(self) -> IExecutionProvider:
        try:
            return self.lookup(self._default_provider_id)
        except (ProviderNotFoundError, ProviderPlaceholderError):
            return self.lookup(self._fallback_provider_id)
