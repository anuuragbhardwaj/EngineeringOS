"""Base provider utilities."""

from __future__ import annotations

import time
from pathlib import Path

from ai_execution.artifacts.generator import render_artifact
from ai_execution.types import (
    ExecutionRequest,
    ExecutionResponse,
    ExecutionResult,
    ExecutionStatus,
    ProviderCapabilities,
    ProviderHealth,
)


class BaseArtifactProvider:
    """Shared artifact write logic for scaffold and Cursor providers."""

    def __init__(self, provider_id: str, capabilities: list[str], priority: int = 0) -> None:
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
            placeholder=False,
        )

    def cancel(self, job_id: str) -> bool:
        return False

    def _write_artifact(self, request: ExecutionRequest) -> ExecutionResult:
        ctx = request.context
        root = Path(ctx.artifact_root)
        root.mkdir(parents=True, exist_ok=True)
        artifact = ctx.deliverable
        content = render_artifact(ctx, artifact)
        (root / artifact).write_text(content, encoding="utf-8")
        return ExecutionResult(
            status=ExecutionStatus.COMPLETED,
            content=content,
            artifacts_touched=[artifact],
            provider_id=self._provider_id,
            message=f"Artifact {artifact} generated",
        )

    def _build_response(
        self,
        request: ExecutionRequest,
        result: ExecutionResult,
        start: float,
        events: list[str],
    ) -> ExecutionResponse:
        return ExecutionResponse(
            request_id=request.request_id,
            result=result,
            conversation_id=request.conversation_id,
            session_id=request.session_id,
            provider_id=self._provider_id,
            duration_ms=(time.perf_counter() - start) * 1000,
            events=events,
        )
