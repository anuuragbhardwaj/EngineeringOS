"""Orchestrator shared types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Protocol


@dataclass
class ExecutionPolicy:
    name: str
    sequential: bool = True
    max_retries: int = 2
    timeout_seconds: int = 300
    approval_required: bool = False
    context_max_chars: int = 32000
    mcp_evidence_required: bool = False


@dataclass
class AssembledContext:
    """Normalized context produced by Context Engine."""

    project_id: str
    phase_id: str
    employee_id: str
    employee_role: str
    artifact_root: str
    project_metadata: dict[str, Any]
    workflow_state: dict[str, Any]
    artifacts: dict[str, str]
    execution_history: list[dict[str, Any]]
    company_config: dict[str, Any]
    mcp_evidence: dict[str, Any]
    conversation_id: str | None = None
    deliverable: str = ""
    required_inputs: list[str] = field(default_factory=list)
    knowledge_snippets: dict[str, str] = field(default_factory=dict)


@dataclass
class Checkpoint:
    checkpoint_id: str
    project_id: str
    phase_id: str
    employee_id: str
    created_at: datetime
    status: str  # active | paused | completed | rolled_back
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionRecord:
    project_id: str
    employee_id: str
    timestamp: datetime
    provider_id: str | None
    duration_ms: float | None
    input_artifacts: list[str]
    output_artifacts: list[str]
    status: str
    retry_count: int
    policy: str
    checkpoint_id: str | None
    phase_id: str
    orchestrator_id: str


@dataclass
class LifecycleCallbacks:
    """Runtime lifecycle operations — Orchestrator never persists directly."""

    persist: Callable[[Any], None]
    validate: Callable[[], Any]
    evaluate_gate: Callable[[], Any]
    record_gate: Callable[[str, bool, str], None]
    advance: Callable[[], Any]
    publish_event: Callable[[str, dict], None]
    mutator: Any
    is_approved: Callable[[str], bool] | None = None


class IAgentAdapter(Protocol):
    def invoke(self, descriptor: Any, context: Any) -> Any: ...

    def cancel(self, job_id: str) -> bool: ...

    def health(self) -> Any: ...
