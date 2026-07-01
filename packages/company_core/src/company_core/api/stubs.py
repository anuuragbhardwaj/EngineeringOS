"""Placeholder API implementations for future phases."""

from __future__ import annotations

from company_core.models.common import EmployeeInfo, Project, ProjectInfo, Workspace, WorkspaceInfo
from company_core.models.errors import NotImplementedFeatureError


class WorkspaceAPI:
    def create(self, workspace_id: str) -> Workspace:
        raise NotImplementedFeatureError("workspace create is not yet implemented")

    def list(self) -> list[WorkspaceInfo]:
        raise NotImplementedFeatureError("workspace list is not yet implemented")

    def open(self, workspace_id: str) -> Workspace:
        raise NotImplementedFeatureError("workspace open is not yet implemented")

    def current(self) -> Workspace | None:
        return None


class ProjectAPI:
    def create(self, project_id: str, workspace: Workspace) -> Project:
        raise NotImplementedFeatureError("project create is not yet implemented")

    def list(self, workspace: Workspace) -> list[ProjectInfo]:
        raise NotImplementedFeatureError("project list is not yet implemented")

    def archive(self, project_id: str) -> None:
        raise NotImplementedFeatureError("project archive is not yet implemented")

    def get_runtime(self, project_id: str) -> object:
        raise NotImplementedFeatureError("project runtime is not yet implemented")


class EmployeeAPI:
    def list(self) -> list[EmployeeInfo]:
        raise NotImplementedFeatureError("employees list is not yet implemented")

    def get(self, employee_id: str) -> object:
        raise NotImplementedFeatureError("employee get is not yet implemented")

    def for_phase(self, phase_id: str) -> list[object]:
        raise NotImplementedFeatureError("employees for_phase is not yet implemented")

    def resolve_path(self, employee_id: str) -> object:
        raise NotImplementedFeatureError("employee resolve_path is not yet implemented")


class IntegrationAPI:
    def install(self, editor: str) -> object:
        raise NotImplementedFeatureError("integration install is not yet implemented")

    def uninstall(self, editor: str) -> None:
        raise NotImplementedFeatureError("integration uninstall is not yet implemented")

    def list_editors(self) -> list[object]:
        raise NotImplementedFeatureError("integration list_editors is not yet implemented")

    def sync(self, editor: str) -> object:
        raise NotImplementedFeatureError("integration sync is not yet implemented")

    def doctor(self, editor: str) -> object:
        raise NotImplementedFeatureError("integration doctor is not yet implemented")
