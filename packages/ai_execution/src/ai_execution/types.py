"""Core execution types and protocols."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    DELEGATED = "delegated"
    INTERRUPTED = "interrupted"


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Conversation:
    conversation_id: str
    session_id: str
    employee_id: str
    project_id: str
    messages: list[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionSession:
    session_id: str
    project_id: str
    employee_id: str
    phase_id: str
    conversation_id: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: datetime | None = None
    provider_id: str | None = None


@dataclass
class ProviderCapabilities:
    provider_id: str
    capabilities: list[str]
    priority: int = 0
    placeholder: bool = False


@dataclass
class ProviderHealth:
    provider_id: str
    available: bool
    message: str
    latency_ms: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderConfiguration:
    provider_id: str
    enabled: bool
    priority: int
    capabilities: list[str]
    placeholder: bool = False
    settings: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionContext:
    """Standardized context for every provider execution."""

    project_id: str
    phase_id: str
    employee_id: str
    employee_role: str
    artifact_root: str
    deliverable: str
    delegation_brief: str
    project_metadata: dict[str, Any]
    workflow_state: dict[str, Any]
    required_inputs: list[str]
    artifact_paths: list[str]
    employee_prompt_path: str | None
    employee_prompt: str | None
    mcp_evidence: dict[str, Any]
    execution_history: list[dict[str, Any]]
    company_config: dict[str, Any]
    capabilities_required: list[str]


@dataclass
class ExecutionRequest:
    request_id: str
    context: ExecutionContext
    conversation_id: str
    session_id: str
    capabilities: list[str]
    stream: bool = False
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 2


@dataclass
class ExecutionResult:
    status: ExecutionStatus
    content: str
    artifacts_touched: list[str]
    provider_id: str
    message: str
    metadata: dict[str, Any] = field(default_factory=dict)
    job_id: str | None = None


@dataclass
class ExecutionResponse:
    request_id: str
    result: ExecutionResult
    conversation_id: str
    session_id: str
    provider_id: str
    duration_ms: float
    events: list[str] = field(default_factory=list)


@dataclass
class ExecutionEvent:
    event_type: str
    request_id: str
    project_id: str
    timestamp: datetime
    payload: dict[str, Any]


class IExecutionProvider(Protocol):
    @property
    def provider_id(self) -> str: ...

    def capabilities(self) -> ProviderCapabilities: ...

    def health(self) -> ProviderHealth: ...

    def execute(self, request: ExecutionRequest) -> ExecutionResponse: ...

    def cancel(self, job_id: str) -> bool: ...


class IAgentAdapter(Protocol):
    """Runtime-facing adapter — sole boundary from kernel to execution platform."""

    def invoke(self, descriptor: Any, context: Any) -> Any: ...

    def cancel(self, job_id: str) -> bool: ...

    def health(self) -> Any: ...


# Phase → capability mapping (configuration-driven defaults)
PHASE_CAPABILITIES: dict[str, list[str]] = {
    "idea": ["reasoning", "planning"],
    "requirements": ["reasoning", "planning"],
    "specification": ["reasoning", "planning"],
    "planning": ["planning", "reasoning"],
    "architecture": ["documentation", "coding", "planning"],
    "implementation": ["coding", "implementation", "tool-use"],
    "testing": ["review", "coding"],
    "review": ["review", "reasoning"],
    "documentation": ["documentation"],
}
