"""Cursor execution provider — first AI platform implementation."""

from __future__ import annotations

import time
from pathlib import Path

from ai_execution.conversation.manager import ConversationManager
from ai_execution.providers.base import BaseArtifactProvider
from ai_execution.types import ExecutionRequest, ExecutionResponse, ProviderHealth


class CursorProvider(BaseArtifactProvider):
    """Executes through Cursor — normalizes responses; never exposes Cursor APIs to Runtime."""

    def __init__(
        self,
        framework_root: Path,
        conversation_manager: ConversationManager,
    ) -> None:
        super().__init__(
            provider_id="cursor",
            capabilities=[
                "reasoning",
                "planning",
                "implementation",
                "review",
                "documentation",
                "vision",
                "tool-use",
                "long-context",
                "coding",
            ],
            priority=100,
        )
        self._framework_root = framework_root
        self._conversations = conversation_manager
        self._agents_dir = framework_root / ".cursor" / "agents"

    def health(self) -> ProviderHealth:
        available = self._agents_dir.is_dir()
        agent_count = len(list(self._agents_dir.glob("*.md"))) if available else 0
        return ProviderHealth(
            provider_id=self._provider_id,
            available=available and agent_count > 0,
            message=(
                f"Cursor agents available ({agent_count} prompts)"
                if available
                else "Cursor agent directory not found"
            ),
            metadata={"agent_count": agent_count},
        )

    def execute(self, request: ExecutionRequest) -> ExecutionResponse:
        start = time.perf_counter()
        ctx = request.context
        events: list[str] = ["execution.started"]

        prompt = self._load_employee_prompt(ctx.employee_id, ctx.employee_prompt_path)
        if prompt:
            self._conversations.add_system_prompt(request.conversation_id, prompt)
            events.append("conversation.system_prompt_loaded")

        user_context = self._build_user_context(ctx)
        self._conversations.add_user_context(request.conversation_id, user_context)
        events.append("conversation.context_added")

        result = self._write_artifact(request)
        self._conversations.add_assistant_response(
            request.conversation_id,
            result.content[:500] + ("..." if len(result.content) > 500 else ""),
        )
        events.append("execution.completed")

        result.metadata["execution_boundary"] = "ai_execution"
        result.metadata["provider"] = self._provider_id
        return self._build_response(request, result, start, events)

    def _load_employee_prompt(self, employee_id: str, prompt_path: str | None) -> str | None:
        if prompt_path and Path(prompt_path).is_file():
            return Path(prompt_path).read_text(encoding="utf-8")
        candidate = self._agents_dir / f"{employee_id}.md"
        if candidate.is_file():
            return candidate.read_text(encoding="utf-8")
        return None

    def _build_user_context(self, ctx) -> str:
        lines = [
            f"Project: {ctx.project_id}",
            f"Phase: {ctx.phase_id}",
            f"Employee: {ctx.employee_id} ({ctx.employee_role})",
            f"Deliverable: {ctx.deliverable}",
            f"Brief: {ctx.delegation_brief}",
        ]
        if ctx.required_inputs:
            lines.append(f"Inputs: {', '.join(ctx.required_inputs)}")
        if ctx.mcp_evidence:
            lines.append(f"MCP evidence context: {ctx.mcp_evidence}")
        return "\n".join(lines)
