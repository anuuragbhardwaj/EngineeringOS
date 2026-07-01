"""Workspace execution platform facade."""

from __future__ import annotations

from pathlib import Path

from workspace_execution.context.types import CurrentContext, UnifiedStatus
from workspace_execution.execution.pause import pause_execution
from workspace_execution.execution.resume import continue_execution, detect_resume_points, resume_execution
from workspace_execution.history.recorder import load_history, record_event
from workspace_execution.navigation.recent import (
    favorite_project,
    favorite_workspace,
    pin_project,
    pin_workspace,
    recent_projects,
    recent_workspaces,
)
from workspace_execution.resolver.resolver import ContextResolver
from workspace_execution.session.store import ensure_company_dirs, load_session, save_session
from workspace_execution.status.engine import StatusEngine


class WorkspaceExecutionPlatform:
    """Context-aware execution layer for EngineeringOS."""

    def __init__(self) -> None:
        self._resolver = ContextResolver()
        self._status = StatusEngine()

    @property
    def resolver(self) -> ContextResolver:
        return self._resolver

    def current(self, instance_root: Path | None = None) -> CurrentContext:
        return self._resolver.sync_runtime(instance_root)

    def status(self, instance_root: Path | None = None) -> UnifiedStatus:
        return self._status.summarize(instance_root)

    def context(self, instance_root: Path | None = None) -> CurrentContext:
        return self.current(instance_root)

    def reset_context(self, instance_root: Path | None = None) -> CurrentContext:
        return self._resolver.reset(instance_root)

    def use_workspace(self, workspace_id: str, instance_root: Path | None = None) -> CurrentContext:
        return self._resolver.set_workspace(workspace_id, instance_root)

    def use_project(self, project_id: str, instance_root: Path | None = None) -> CurrentContext:
        return self._resolver.set_project(project_id, instance_root)

    def open_company(self, instance_root: Path, workspace_id: str | None = None) -> CurrentContext:
        ensure_company_dirs(instance_root)
        session = load_session(instance_root)
        if workspace_id:
            session.workspace_id = workspace_id
        elif not session.workspace_id:
            from company_core.config.loader import load_manifest

            manifest = load_manifest(instance_root / "company.yaml")
            session.workspace_id = manifest.default_workspace
        save_session(instance_root, session)
        record_event(instance_root, event_type="company_opened", workspace_id=session.workspace_id)
        return self._resolver.sync_runtime(instance_root)

    def pause(self, instance_root: Path, project_id: str | None = None) -> dict:
        return pause_execution(instance_root, project_id)

    def resume(self, instance_root: Path, project_id: str | None = None) -> dict:
        return resume_execution(instance_root, project_id)

    def continue_execution(self, instance_root: Path) -> dict:
        return continue_execution(instance_root)

    def history(
        self,
        instance_root: Path,
        *,
        project_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[dict]:
        return load_history(instance_root, project_id=project_id, event_type=event_type, limit=limit)

    def recent_workspaces(self, instance_root: Path) -> list[str]:
        return recent_workspaces(instance_root)

    def recent_projects(self, instance_root: Path) -> list[str]:
        return recent_projects(instance_root)

    def resume_points(self, instance_root: Path) -> list[dict]:
        return detect_resume_points(instance_root)

    def record_command(self, command: str, instance_root: Path | None = None) -> None:
        self._resolver.record_command(command, instance_root)

    def update_execution(
        self,
        instance_root: Path,
        *,
        project_id: str | None = None,
        phase_id: str | None = None,
        employee_id: str | None = None,
        status: str | None = None,
        provider_id: str | None = None,
        checkpoint_id: str | None = None,
        conversation_ids: dict[str, str] | None = None,
    ) -> None:
        session = load_session(instance_root)
        if project_id:
            session.project_id = project_id
        if phase_id:
            session.current_phase = phase_id
        if employee_id:
            session.current_employee = employee_id
        if status:
            session.execution_status = status
        if provider_id:
            session.provider_id = provider_id
        if checkpoint_id:
            session.checkpoint_id = checkpoint_id
        if conversation_ids:
            session.conversation_ids.update(conversation_ids)
        session.pipeline = session.pipeline or "planning"
        save_session(instance_root, session)
