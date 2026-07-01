"""ContextAPI — Framework API surface for execution context."""

from __future__ import annotations

from pathlib import Path

from company_core.config.loader import discover_instance_root
from company_core.models.errors import ManifestNotFoundError
from workspace_execution.factory import create_execution_platform
from workspace_execution.context.types import CurrentContext, UnifiedStatus


class ContextAPI:
    """Expose execution context through FrameworkAPI."""

    def __init__(self, instance_root: Path | None = None) -> None:
        self._instance_root = instance_root
        self._platform = create_execution_platform()

    def _root(self) -> Path:
        root = self._instance_root or discover_instance_root()
        if root is None:
            raise ManifestNotFoundError("company.yaml not found")
        return root.resolve()

    def current(self) -> CurrentContext:
        return self._platform.current(self._instance_root)

    def status(self) -> UnifiedStatus:
        return self._platform.status(self._instance_root)

    def resolve(self) -> CurrentContext:
        return self.current()

    def reset(self) -> CurrentContext:
        return self._platform.reset_context(self._root())

    def use_workspace(self, workspace_id: str) -> CurrentContext:
        return self._platform.use_workspace(workspace_id, self._root())

    def use_project(self, project_id: str) -> CurrentContext:
        return self._platform.use_project(project_id, self._root())

    def active_project_id(self) -> str | None:
        return self._platform.resolver.active_project_id(self._instance_root)

    def active_workspace_id(self) -> str | None:
        return self._platform.resolver.active_workspace_id(self._instance_root)

    def pause(self, project_id: str | None = None) -> dict:
        return self._platform.pause(self._root(), project_id)

    def resume(self, project_id: str | None = None) -> dict:
        return self._platform.resume(self._root(), project_id)

    def continue_execution(self) -> dict:
        return self._platform.continue_execution(self._root())

    def history(self, **kwargs) -> list[dict]:
        return self._platform.history(self._root(), **kwargs)

    def recent_workspaces(self) -> list[str]:
        return self._platform.recent_workspaces(self._root())

    def recent_projects(self) -> list[str]:
        return self._platform.recent_projects(self._root())

    @property
    def resolver(self):
        return self._platform.resolver

    @property
    def platform(self):
        return self._platform
