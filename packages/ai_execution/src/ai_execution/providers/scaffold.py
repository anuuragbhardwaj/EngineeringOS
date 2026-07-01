"""Scaffold provider — local fallback when AI providers unavailable."""

from __future__ import annotations

import time

from ai_execution.providers.base import BaseArtifactProvider
from ai_execution.types import ExecutionRequest, ExecutionResponse, ProviderHealth


class ScaffoldProvider(BaseArtifactProvider):
    """Fallback provider — editor-independent deterministic artifact generation."""

    def __init__(self) -> None:
        super().__init__(
            provider_id="scaffold",
            capabilities=["reasoning", "planning", "documentation", "coding"],
            priority=0,
        )

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider_id=self._provider_id,
            available=True,
            message="Scaffold fallback provider ready",
        )

    def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        start = time.perf_counter()
        result = self._write_artifact(request)
        return self._build_response(request, result, start, ["execution.completed"])
