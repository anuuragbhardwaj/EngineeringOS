"""Placeholder providers for future AI platforms."""

from __future__ import annotations

from ai_execution.errors import ProviderPlaceholderError
from ai_execution.types import (
    ExecutionRequest,
    ExecutionResponse,
    ProviderCapabilities,
    ProviderHealth,
)


class PlaceholderProvider:
    """Registered but not implemented — enables discovery without Runtime changes."""

    def __init__(self, provider_id: str, capabilities: list[str], priority: int = 50) -> None:
        self._provider_id = provider_id
        self._capabilities = capabilities
        self._priority = priority

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            provider_id=self._provider_id,
            capabilities=self._capabilities,
            priority=self._priority,
            placeholder=True,
        )

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider_id=self._provider_id,
            available=False,
            message=f"{self._provider_id} provider not yet implemented",
        )

    def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        raise ProviderPlaceholderError(
            f"Provider {self._provider_id} is not yet implemented"
        )

    def cancel(self, job_id: str) -> bool:
        return False


PLACEHOLDER_IDS = (
    "claude-code",
    "openai",
    "gemini",
    "opencode",
    "roo-code",
    "local",
)
