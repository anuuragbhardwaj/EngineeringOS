"""Execution context types — consumed by all packages."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SessionContext:
    """Persistent execution session metadata."""

    framework_version: str = "2.0.0"
    company_id: str | None = None
    instance_root: str | None = None
    workspace_id: str | None = None
    project_id: str | None = None
    pipeline: str | None = None
    current_phase: str | None = None
    current_gate: str | None = None
    current_employee: str | None = None
    execution_status: str = "idle"
    conversation_ids: dict[str, str] = field(default_factory=dict)
    runtime_state_location: str | None = None
    checkpoint_id: str | None = None
    last_activity: str | None = None
    recent_commands: list[str] = field(default_factory=list)
    recent_projects: list[str] = field(default_factory=list)
    recent_workspaces: list[str] = field(default_factory=list)
    provider_id: str | None = None
    pinned_workspaces: list[str] = field(default_factory=list)
    pinned_projects: list[str] = field(default_factory=list)
    favorite_workspaces: list[str] = field(default_factory=list)
    favorite_projects: list[str] = field(default_factory=list)


@dataclass
class WorkspaceContext:
    workspace_id: str
    root: Path
    project_count: int = 0


@dataclass
class ProjectContext:
    project_id: str
    root: Path
    workspace_id: str
    status: str = "unknown"


@dataclass
class ExecutionContext:
    pipeline: str | None
    current_phase: str | None
    current_gate: str | None
    current_employee: str | None
    execution_status: str
    checkpoint_id: str | None
    runtime_state_location: str | None
    provider_id: str | None
    can_resume: bool = False
    pending_approval: bool = False


@dataclass
class CurrentContext:
    """Full active execution context."""

    company_id: str | None
    instance_root: Path | None
    workspace: WorkspaceContext | None
    project: ProjectContext | None
    execution: ExecutionContext | None
    session: SessionContext


@dataclass
class UnifiedStatus:
    """Unified status engine output."""

    company_id: str | None
    workspace_id: str | None
    project_id: str | None
    current_phase: str | None
    current_employee: str | None
    pipeline_progress: str | None
    execution_status: str
    runtime_healthy: bool
    mcp_healthy: bool
    pending_actions: list[str] = field(default_factory=list)
    pending_approvals: list[str] = field(default_factory=list)
    resume_points: list[str] = field(default_factory=list)
    recent_activity: list[str] = field(default_factory=list)
    message: str = ""
