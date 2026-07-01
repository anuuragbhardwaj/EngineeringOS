"""WorkspaceAPI — delegates to LifecyclePlatform."""

from __future__ import annotations

from pathlib import Path

from company_core.models.common import Workspace, WorkspaceInfo
from company_core.models.errors import ManifestNotFoundError
from company_lifecycle.factory import create_lifecycle_platform


class WorkspaceAPI:
    """Workspace operations via company_lifecycle."""

    def __init__(self, instance_root: Path | None = None) -> None:
        self._instance_root = instance_root
        self._lifecycle = create_lifecycle_platform()

    def create(self, workspace_id: str) -> Workspace:
        return self._lifecycle.create_workspace(workspace_id, self._instance_root)

    def list(self) -> list[WorkspaceInfo]:
        return self._lifecycle.list_workspaces(self._instance_root)

    def open(self, workspace_id: str) -> Workspace:
        root = self._instance_root
        if root is None:
            from company_core.config.loader import discover_instance_root

            root = discover_instance_root()
        if root is None:
            raise ManifestNotFoundError("company.yaml not found")
        self._lifecycle.open_company(root, workspace_id=workspace_id)
        from company_lifecycle.workspace.manager import workspace_info

        info = workspace_info(root, workspace_id)
        return Workspace(workspace_id=workspace_id, root=info["root"])

    def current(self) -> Workspace | None:
        root = self._instance_root
        if root is None:
            from company_core.config.loader import discover_instance_root

            root = discover_instance_root()
        if root is None:
            return None
        ctx = self._lifecycle.open_company(root)
        if not ctx.active_workspace:
            return None
        from company_lifecycle.workspace.manager import workspace_info

        info = workspace_info(root, ctx.active_workspace)
        return Workspace(workspace_id=ctx.active_workspace, root=info["root"])

    def archive(self, workspace_id: str) -> Workspace:
        return self._lifecycle.archive_workspace(workspace_id, self._instance_root)

    def remove(self, workspace_id: str) -> None:
        self._lifecycle.remove_workspace(workspace_id, self._instance_root)

    def validate(self, workspace_id: str) -> object:
        return self._lifecycle.validate_workspace(workspace_id, self._instance_root)
