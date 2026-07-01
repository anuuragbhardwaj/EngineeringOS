"""AI Execution Platform orchestrator."""

from __future__ import annotations

import time
from collections.abc import Callable
from pathlib import Path

from ai_execution import events as exec_events
from ai_execution.capabilities import CapabilityResolver
from ai_execution.context import build_execution_context, new_request_id
from ai_execution.conversation.manager import ConversationManager
from ai_execution.errors import (
    ExecutionError,
    ProviderUnavailableError,
    RateLimitError,
)
from ai_execution.registry.provider_registry import ProviderRegistry
from ai_execution.types import ExecutionEvent, ExecutionRequest, ExecutionResponse


class ExecutionPlatform:
    """Central orchestrator — Runtime communicates only through this platform."""

    def __init__(
        self,
        registry: ProviderRegistry,
        conversations: ConversationManager,
        resolver: CapabilityResolver,
    ) -> None:
        self._registry = registry
        self._conversations = conversations
        self._resolver = resolver
        self._event_handlers: list[Callable[[ExecutionEvent], None]] = []

    def on_event(self, handler: Callable[[ExecutionEvent], None]) -> None:
        self._event_handlers.append(handler)

    def _emit(self, event_type: str, request: ExecutionRequest, payload: dict) -> None:
        event = ExecutionEvent(
            event_type=event_type,
            request_id=request.request_id,
            project_id=request.context.project_id,
            timestamp=__import__("datetime").datetime.utcnow(),
            payload=payload,
        )
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception:
                pass

    def execute(
        self,
        descriptor: object,
        invocation_context: object,
        *,
        workflow_state: dict | None = None,
        execution_history: list | None = None,
    ) -> ExecutionResponse:
        ctx = build_execution_context(
            descriptor,
            invocation_context,
            workflow_state=workflow_state,
            execution_history=execution_history,
        )
        session = self._conversations.create_session(
            ctx.project_id,
            ctx.employee_id,
            ctx.phase_id,
        )
        session.conversation_id  # bound via create_session
        conv = self._conversations.get_conversation(session.conversation_id)

        capabilities = self._resolver.resolve_for_phase(ctx.phase_id)
        request = ExecutionRequest(
            request_id=new_request_id(),
            context=ctx,
            conversation_id=conv.conversation_id,
            session_id=session.session_id,
            capabilities=capabilities,
        )

        self._emit(
            exec_events.ExecutionRequested,
            request,
            {"capabilities": capabilities, "phase_id": ctx.phase_id},
        )

        return self._execute_with_retry(request)

    def _execute_with_retry(self, request: ExecutionRequest) -> ExecutionResponse:
        last_error: Exception | None = None
        for attempt in range(request.max_retries + 1):
            request.retry_count = attempt
            try:
                provider = self._resolver.select_provider(request.capabilities)
                self._emit(
                    exec_events.ProviderSelected,
                    request,
                    {"provider_id": provider.provider_id},
                )
                self._emit(exec_events.ExecutionStarted, request, {})
                start = time.perf_counter()
                response = provider.execute(request)
                self._conversations.end_session(
                    request.session_id, provider.provider_id
                )
                self._emit(
                    exec_events.ExecutionCompleted,
                    request,
                    {
                        "provider_id": provider.provider_id,
                        "duration_ms": (time.perf_counter() - start) * 1000,
                    },
                )
                return response
            except (ProviderUnavailableError, RateLimitError, ExecutionError) as exc:
                last_error = exc
                self._emit(
                    exec_events.RetryAttempted,
                    request,
                    {"attempt": attempt, "error": str(exc)},
                )
                if attempt < request.max_retries:
                    fallback = self._registry.get(self._registry.fallback_provider_id)
                    if fallback and fallback.health().available:
                        self._emit(
                            exec_events.ProviderFallback,
                            request,
                            {"fallback_id": fallback.provider_id},
                        )
                        response = fallback.execute(request)
                        self._conversations.end_session(
                            request.session_id, fallback.provider_id
                        )
                        return response

        self._emit(
            exec_events.ExecutionFailed,
            request,
            {"error": str(last_error)},
        )
        raise last_error or ExecutionError("Execution failed")

    def set_project_storage(self, project_root: Path) -> None:
        self._conversations.set_storage_root(project_root)

    def diagnostics(self) -> dict:
        return {
            "providers": self._registry.health_all(),
            "default": self._registry.default_provider_id,
            "fallback": self._registry.fallback_provider_id,
        }
