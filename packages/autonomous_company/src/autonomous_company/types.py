"""Autonomous company shared types."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class RunnerStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    BLOCKED = "blocked"
    STOPPED = "stopped"
    COMPLETED = "completed"


class DecisionAction(str, Enum):
    CONTINUE = "continue"
    PAUSE = "pause"
    RETRY = "retry"
    ROLLBACK = "rollback"
    ESCALATE = "escalate"
    WAIT = "wait"
    RESUME = "resume"
    TERMINATE = "terminate"


class BlockerType(str, Enum):
    APPROVAL_REQUIRED = "approval_required"
    AMBIGUOUS_REQUIREMENTS = "ambiguous_requirements"
    CREDENTIALS_REQUIRED = "credentials_required"
    SECURITY_POLICY = "security_policy"
    REPOSITORY_CONFLICT = "repository_conflict"
    RUNTIME_FAILURE = "runtime_failure"
    KNOWLEDGE_CONFLICT = "knowledge_conflict"
    PROVIDER_FAILURE = "provider_failure"
    MCP_FAILURE = "mcp_failure"
    ARTIFACT_VALIDATION = "artifact_validation"
    HUMAN_INPUT = "human_input"
    RECOVERABLE = "recoverable"
    UNRECOVERABLE = "unrecoverable"


@dataclass
class ExecutionPolicy:
    max_retries: int = 3
    retry_backoff_seconds: float = 1.0
    checkpoint_interval_seconds: int = 300
    max_execution_duration_seconds: int = 86400
    autonomous_depth: str = "pipeline"  # phase | pipeline | goal
    auto_push: bool = False
    night_mode: bool = False
    cost_limit: float | None = None
    provider_priority: list[str] = field(default_factory=list)
    approval_gates: list[str] = field(default_factory=lambda: ["architecture", "implementation", "review", "commit"])

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_retries": self.max_retries,
            "retry_backoff_seconds": self.retry_backoff_seconds,
            "checkpoint_interval_seconds": self.checkpoint_interval_seconds,
            "max_execution_duration_seconds": self.max_execution_duration_seconds,
            "autonomous_depth": self.autonomous_depth,
            "auto_push": self.auto_push,
            "night_mode": self.night_mode,
            "cost_limit": self.cost_limit,
            "provider_priority": self.provider_priority,
            "approval_gates": self.approval_gates,
        }


@dataclass
class Goal:
    goal_id: str
    title: str
    description: str
    status: str = "active"
    project_id: str | None = None
    created_at: str = ""
    completed_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "goal_id": self.goal_id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "project_id": self.project_id,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "metadata": self.metadata,
        }


@dataclass
class Decision:
    decision_id: str
    action: str
    reason: str
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    project_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_id": self.decision_id,
            "action": self.action,
            "reason": self.reason,
            "context": self.context,
            "timestamp": self.timestamp,
            "project_id": self.project_id,
        }


@dataclass
class Blocker:
    blocker_id: str
    blocker_type: str
    message: str
    recoverable: bool
    actionable: str = ""
    timestamp: str = ""
    project_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "blocker_id": self.blocker_id,
            "blocker_type": self.blocker_type,
            "message": self.message,
            "recoverable": self.recoverable,
            "actionable": self.actionable,
            "timestamp": self.timestamp,
            "project_id": self.project_id,
        }


@dataclass
class ApprovalRequest:
    approval_id: str
    gate: str
    project_id: str
    approved: bool = False
    approved_by: str | None = None
    reason: str = ""
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__


@dataclass
class RunnerState:
    status: str = RunnerStatus.IDLE.value
    goal_id: str | None = None
    project_id: str | None = None
    current_phase: str | None = None
    retry_count: int = 0
    started_at: str | None = None
    last_heartbeat: str | None = None
    stopped: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "goal_id": self.goal_id,
            "project_id": self.project_id,
            "current_phase": self.current_phase,
            "retry_count": self.retry_count,
            "started_at": self.started_at,
            "last_heartbeat": self.last_heartbeat,
            "stopped": self.stopped,
        }


@dataclass
class AutonomyStatus:
    runner: RunnerState
    active_goal: Goal | None
    blockers: list[Blocker]
    pending_approvals: list[ApprovalRequest]
    recent_decisions: list[Decision]
    policy: ExecutionPolicy

    def to_dict(self) -> dict[str, Any]:
        return {
            "runner": self.runner.to_dict(),
            "active_goal": self.active_goal.to_dict() if self.active_goal else None,
            "blockers": [b.to_dict() for b in self.blockers],
            "pending_approvals": [a.to_dict() for a in self.pending_approvals],
            "recent_decisions": [d.to_dict() for d in self.recent_decisions],
            "policy": self.policy.to_dict(),
        }


def utc_now() -> str:
    return datetime.utcnow().isoformat()
