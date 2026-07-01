"""Capability-based provider resolution."""

from __future__ import annotations

from ai_execution.errors import CapabilityNotSupportedError, ProviderNotFoundError
from ai_execution.registry.provider_registry import ProviderRegistry
from ai_execution.types import IExecutionProvider, PHASE_CAPABILITIES


class CapabilityResolver:
    """Routes execution requests to providers by capability — never by provider name."""

    def __init__(self, registry: ProviderRegistry) -> None:
        self._registry = registry

    def resolve_for_phase(self, phase_id: str) -> list[str]:
        return list(PHASE_CAPABILITIES.get(phase_id, ["reasoning", "coding"]))

    def select_provider(
        self,
        capabilities: list[str],
        *,
        exclude_placeholders: bool = True,
    ) -> IExecutionProvider:
        candidates = self._registry.find_by_capabilities(
            capabilities,
            exclude_placeholders=exclude_placeholders,
        )
        if not candidates:
            fallback_id = self._registry.fallback_provider_id
            provider = self._registry.get(fallback_id)
            if provider and provider.health().available:
                return provider
            raise CapabilityNotSupportedError(
                f"No provider supports capabilities: {capabilities}"
            )

        for provider in candidates:
            health = provider.health()
            if health.available:
                return provider

        fallback = self._registry.get(self._registry.fallback_provider_id)
        if fallback:
            return fallback
        raise ProviderNotFoundError("No available provider for requested capabilities")
