"""ProjectAPI — delegates to Runtime."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from runtime_engine.factory import create_runtime
from runtime_engine.runtime.facade import Runtime

from company_core.config.loader import discover_framework_root, discover_instance_root
from company_core.models.common import Project, ProjectInfo
from company_core.models.errors import NotImplementedFeatureError, ProjectNotFoundError
from company_core.models.manifest import CompanyManifest


@dataclass
class ProjectCreateRequest:
    name: str
    description: str
    platform: str
    production: bool
    technology_stack: str
    location: Path


def _slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "project"


class ProjectAPI:
    """Project operations via IRuntime."""

    def __init__(self, manifest: CompanyManifest | None = None) -> None:
        self._manifest = manifest
        self._runtime: Runtime | None = None
        self._active_project_id: str | None = None

    def _get_runtime(self) -> Runtime:
        if self._runtime is None:
            instance = discover_instance_root()
            framework = discover_framework_root(instance)
            self._runtime = create_runtime(framework_root=framework)
        return self._runtime

    def create(self, project_id: str, workspace: object = None) -> Project:
        raise NotImplementedFeatureError(
            "Use create_interactive or create_from_request for project creation"
        )

    def create_from_request(self, request: ProjectCreateRequest) -> Project:
        runtime = self._get_runtime()
        project_id = _slugify(request.name)
        location = request.location.resolve()
        location.mkdir(parents=True, exist_ok=True)

        metadata = {
            "name": request.name,
            "description": request.description,
            "platform": request.platform,
            "mode": "production" if request.production else "prototype",
            "technology_stack": request.technology_stack,
        }

        runtime.init_project(project_id, artifact_root=str(location), metadata=metadata)
        runtime.execute_planning_pipeline(project_id, stop_after_phase="architecture")
        self._active_project_id = project_id

        return Project(project_id=project_id, root=location)

    def list(self, workspace: object = None) -> list[ProjectInfo]:
        runtime = self._get_runtime()
        projects: list[ProjectInfo] = []
        for project_id in runtime._store.list_projects():  # noqa: SLF001 — v1 listing
            try:
                view = runtime.status(project_id)
                projects.append(
                    ProjectInfo(
                        project_id=project_id,
                        status=view.status.value,
                    )
                )
            except Exception:
                continue
        return projects

    def get_runtime(self, project_id: str) -> Runtime:
        runtime = self._get_runtime()
        if not runtime._store.exists(project_id):  # noqa: SLF001
            raise ProjectNotFoundError(f"Project not found: {project_id}")
        self._active_project_id = project_id
        return runtime

    def status(self, project_id: str | None = None) -> object:
        pid = project_id or self._active_project_id
        if not pid:
            raise ProjectNotFoundError("No active project")
        return self._get_runtime().status(pid)

    def resume(self, project_id: str) -> object:
        return self._get_runtime().resume(project_id)

    def history(self, project_id: str) -> dict:
        return self._get_runtime().history(project_id)

    def validate(self, project_id: str) -> object:
        return self._get_runtime().validate(project_id)
