"""ProjectAPI — lifecycle scaffolding + Runtime execution + execution context."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from company_core.config.loader import discover_framework_root, discover_instance_root
from company_core.models.common import Project, ProjectInfo
from company_core.models.errors import ManifestNotFoundError, ProjectNotFoundError
from company_core.models.manifest import CompanyManifest
from company_core.ports.runtime_port import IRuntimePort
from company_core.runtime_bridge import create_runtime
from company_lifecycle.factory import create_lifecycle_platform
from company_lifecycle.types import ProjectCreateOptions
from workspace_execution.factory import create_execution_platform


@dataclass
class ProjectCreateRequest:
    name: str
    description: str
    platform: str
    production: bool
    technology_stack: str
    location: Path | None = None
    template_profile: str = "production"
    workspace_id: str | None = None
    run_planning_pipeline: bool = True


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "project"


class ProjectAPI:
    """Project operations — lifecycle scaffolding then Runtime pipeline."""

    def __init__(self, manifest: CompanyManifest | None = None) -> None:
        self._manifest = manifest
        self._runtime: IRuntimePort | None = None
        self._lifecycle = create_lifecycle_platform()
        self._execution = create_execution_platform()

    def _get_runtime(self) -> IRuntimePort:
        if self._runtime is None:
            instance = discover_instance_root()
            framework = discover_framework_root(instance)
            self._runtime = create_runtime(framework_root=framework)
        return self._runtime

    def _active_project_id(self) -> str | None:
        return self._execution.resolver.active_project_id()

    def create_from_request(self, request: ProjectCreateRequest) -> Project:
        instance = discover_instance_root()
        if instance is None:
            raise ManifestNotFoundError("company.yaml not found — run engineeringos init")

        ws = request.workspace_id or self._execution.resolver.active_workspace_id()
        options = ProjectCreateOptions(
            name=request.name,
            description=request.description,
            platform=request.platform,
            production=request.production,
            technology_stack=request.technology_stack,
            template_profile=request.template_profile,
            workspace_id=ws,
            location=request.location,
            run_planning_pipeline=request.run_planning_pipeline,
        )
        location, project_id, workspace_id = self._lifecycle.scaffold_project(instance, options)

        if request.run_planning_pipeline:
            runtime = self._get_runtime()
            metadata = {
                "name": request.name,
                "description": request.description,
                "platform": request.platform,
                "mode": "production" if request.production else "prototype",
                "technology_stack": request.technology_stack,
            }
            runtime.init_project(project_id, artifact_root=str(location), metadata=metadata)
            runtime.execute_planning_pipeline(project_id, stop_after_phase="architecture")

        self._execution.use_project(project_id, instance)
        self._execution.update_execution(
            instance,
            project_id=project_id,
            status="active",
            phase_id="architecture" if request.run_planning_pipeline else None,
        )
        return Project(project_id=project_id, root=location)

    def create(self, project_id: str, workspace: object = None) -> Project:
        raise NotImplementedError("Use create_from_request")

    def list(self, workspace: object = None) -> list[ProjectInfo]:
        instance = discover_instance_root()
        if instance is None:
            runtime = self._get_runtime()
            projects: list[ProjectInfo] = []
            for pid in runtime.list_project_ids():
                try:
                    view = runtime.status(pid)
                    projects.append(ProjectInfo(project_id=pid, status=view.status.value))
                except Exception:
                    continue
            return projects

        ws_id = getattr(workspace, "workspace_id", None) if workspace else self._execution.resolver.active_workspace_id()
        entries = self._lifecycle.list_projects(workspace_id=ws_id, instance_root=instance)
        return [
            ProjectInfo(project_id=e["project_id"], status=e.get("status", "active"))
            for e in entries
        ]

    def clone(self, source: Path, name: str, workspace_id: str | None = None) -> Project:
        instance = discover_instance_root()
        if instance is None:
            raise ManifestNotFoundError("company.yaml not found")
        dest = self._lifecycle.clone_project(source, name, workspace_id, instance)
        project_id = _slugify(name)
        self._execution.use_project(project_id, instance)
        return Project(project_id=project_id, root=dest)

    def archive(self, project_id: str, workspace_id: str | None = None) -> Path:
        instance = discover_instance_root()
        if instance is None:
            raise ManifestNotFoundError("company.yaml not found")
        return self._lifecycle.archive_project(project_id, workspace_id, instance)

    def remove(self, project_id: str, workspace_id: str | None = None) -> None:
        instance = discover_instance_root()
        if instance is None:
            raise ManifestNotFoundError("company.yaml not found")
        self._lifecycle.remove_project(project_id, workspace_id, instance)

    def get_runtime(self, project_id: str | None = None) -> IRuntimePort:
        pid = project_id or self._active_project_id()
        if not pid:
            raise ProjectNotFoundError("No active project")
        runtime = self._get_runtime()
        if not runtime.project_exists(pid):
            raise ProjectNotFoundError(f"Project not found: {pid}")
        instance = discover_instance_root()
        if instance:
            self._execution.use_project(pid, instance)
        return runtime

    def status(self, project_id: str | None = None) -> object:
        pid = project_id or self._active_project_id()
        if not pid:
            raise ProjectNotFoundError("No active project — use engineeringos project use <id>")
        view = self._get_runtime().status(pid)
        instance = discover_instance_root()
        if instance:
            self._execution.update_execution(
                instance,
                project_id=pid,
                phase_id=view.current_phase_id,
                status=view.status.value,
            )
        return view

    def resume(self, project_id: str | None = None) -> object:
        instance = discover_instance_root()
        if instance is None:
            raise ManifestNotFoundError("company.yaml not found")
        result = self._execution.resume(instance, project_id)
        pid = result.get("project_id") or project_id or self._active_project_id()
        if pid:
            return self._get_runtime().load_project(pid)
        raise ProjectNotFoundError("Resume failed")

    def history(self, project_id: str | None = None) -> dict:
        pid = project_id or self._active_project_id()
        if not pid:
            raise ProjectNotFoundError("No active project")
        runtime_history = self._get_runtime().history(pid)
        instance = discover_instance_root()
        if instance:
            exec_history = self._execution.history(instance, project_id=pid)
            runtime_history["execution_context"] = exec_history
        return runtime_history

    def validate(self, project_id: str | None = None) -> object:
        pid = project_id or self._active_project_id()
        if not pid:
            raise ProjectNotFoundError("No active project")
        return self._get_runtime().validate(pid)

    def use(self, project_id: str) -> Project:
        instance = discover_instance_root()
        if instance is None:
            raise ManifestNotFoundError("company.yaml not found")
        ctx = self._execution.use_project(project_id, instance)
        if not ctx.project:
            raise ProjectNotFoundError(f"Project not found: {project_id}")
        return Project(project_id=project_id, root=ctx.project.root)
