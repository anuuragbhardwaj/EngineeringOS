"""Context resolver — single source of active execution context."""

from __future__ import annotations

from pathlib import Path

from company_core.config.loader import discover_framework_root, discover_instance_root, load_manifest
from workspace_execution.context.types import (
    CurrentContext,
    ExecutionContext,
    ProjectContext,
    SessionContext,
    WorkspaceContext,
)
from workspace_execution.errors import NoActiveCompanyError
from workspace_execution.history.recorder import record_event
from workspace_execution.navigation.recent import touch_project, touch_workspace
from workspace_execution.session.store import load_session, save_session


class ContextResolver:
    """Resolves active company, workspace, project, and execution state."""

    def resolve(self, instance_root: Path | None = None) -> CurrentContext:
        root = instance_root or discover_instance_root()
        if root is None:
            session = SessionContext()
            return CurrentContext(
                company_id=None,
                instance_root=None,
                workspace=None,
                project=None,
                execution=None,
                session=session,
            )

        root = root.resolve()
        session = load_session(root)
        manifest = load_manifest(root / "company.yaml")
        session.company_id = manifest.instance_id

        workspace_ctx = None
        if session.workspace_id:
            from company_lifecycle.workspace.manager import workspace_info

            try:
                info = workspace_info(root, session.workspace_id)
                workspace_ctx = WorkspaceContext(
                    workspace_id=session.workspace_id,
                    root=info["root"],
                    project_count=info["project_count"],
                )
            except Exception:
                pass

        project_ctx = None
        if session.project_id and session.workspace_id:
            project_root = self._project_root(root, session.workspace_id, session.project_id, manifest.workspaces_root)
            if project_root.is_dir():
                project_ctx = ProjectContext(
                    project_id=session.project_id,
                    root=project_root,
                    workspace_id=session.workspace_id,
                    status=session.execution_status,
                )
                session.runtime_state_location = str(project_root / ".runtime" / "state.json")

        execution_ctx = ExecutionContext(
            pipeline=session.pipeline,
            current_phase=session.current_phase,
            current_gate=session.current_gate,
            current_employee=session.current_employee,
            execution_status=session.execution_status,
            checkpoint_id=session.checkpoint_id,
            runtime_state_location=session.runtime_state_location,
            provider_id=session.provider_id,
            can_resume=session.execution_status in {"paused", "interrupted", "active"},
            pending_approval=session.execution_status == "pending_approval",
        )

        save_session(root, session)

        return CurrentContext(
            company_id=manifest.instance_id,
            instance_root=root,
            workspace=workspace_ctx,
            project=project_ctx,
            execution=execution_ctx,
            session=session,
        )

    def set_workspace(self, workspace_id: str, instance_root: Path | None = None) -> CurrentContext:
        root = self._require_root(instance_root)
        session = load_session(root)
        session.workspace_id = workspace_id
        save_session(root, session)
        touch_workspace(root, workspace_id)
        record_event(root, event_type="workspace_selected", workspace_id=workspace_id)
        return self.resolve(root)

    def set_project(self, project_id: str, instance_root: Path | None = None) -> CurrentContext:
        root = self._require_root(instance_root)
        session = load_session(root)
        session.project_id = project_id
        save_session(root, session)
        touch_project(root, project_id)
        record_event(root, event_type="project_selected", project_id=project_id, workspace_id=session.workspace_id)
        return self.sync_runtime(root)

    def record_command(self, command: str, instance_root: Path | None = None) -> None:
        root = instance_root or discover_instance_root()
        if root is None:
            return
        session = load_session(root)
        recent = [c for c in session.recent_commands if c != command]
        recent.insert(0, command)
        session.recent_commands = recent[:50]
        save_session(root, session)
        record_event(root, event_type="command", command=command, project_id=session.project_id)

    def reset(self, instance_root: Path | None = None) -> CurrentContext:
        root = self._require_root(instance_root)
        manifest = load_manifest(root / "company.yaml")
        session = SessionContext(
            company_id=manifest.instance_id,
            instance_root=str(root),
            workspace_id=manifest.default_workspace,
        )
        save_session(root, session)
        record_event(root, event_type="context_reset")
        return self.resolve(root)

    def sync_runtime(self, instance_root: Path | None = None) -> CurrentContext:
        """Sync session from active runtime state."""
        root = instance_root or discover_instance_root()
        if root is None:
            return self.resolve(None)

        ctx = self.resolve(root)
        if not ctx.project:
            return ctx

        try:
            from runtime_engine.factory import create_runtime

            framework = discover_framework_root(root)
            runtime = create_runtime(framework_root=framework)
            if not runtime._store.exists(ctx.project.project_id):  # noqa: SLF001
                return ctx
            view = runtime.status(ctx.project.project_id)
            session = load_session(root)
            session.current_phase = view.current_phase_id
            session.current_gate = view.current_gate_id
            session.current_employee = view.metadata.get("active_agent_id") if view.metadata else None
            session.pipeline = "planning"
            if view.status.value == "PAUSED":
                session.execution_status = "paused"
            elif view.blockers:
                session.execution_status = "blocked"
            elif getattr(view, "pipeline_completed", False):
                session.execution_status = "completed"
            else:
                session.execution_status = "active"
            session.runtime_state_location = str(
                ctx.project.root / ".runtime" / "state.json"
            )
            save_session(root, session)
        except Exception:
            pass
        return self.resolve(root)

    def active_project_id(self, instance_root: Path | None = None) -> str | None:
        return self.resolve(instance_root).session.project_id

    def active_workspace_id(self, instance_root: Path | None = None) -> str | None:
        return self.resolve(instance_root).session.workspace_id

    def _require_root(self, instance_root: Path | None) -> Path:
        root = instance_root or discover_instance_root()
        if root is None:
            raise NoActiveCompanyError("No company instance found — run engineeringos open")
        return root.resolve()

    def _project_root(
        self, instance_root: Path, workspace_id: str, project_id: str, workspaces_root: str
    ) -> Path:
        return instance_root / workspaces_root.strip("/") / workspace_id / "projects" / project_id
