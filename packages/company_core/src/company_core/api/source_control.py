"""SourceControlAPI — Framework API surface for source control."""

from __future__ import annotations

from pathlib import Path

from company_core.config.loader import discover_instance_root
from company_core.models.errors import ManifestNotFoundError
from source_control.types import CommitMessage, CommitResult, ReleasePlan


class SourceControlAPI:
    """Expose source control through FrameworkAPI — no direct Git access."""

    def __init__(self, instance_root: Path | None = None) -> None:
        self._instance_root = instance_root
        self._platform = None

    def _get_platform(self):
        if self._platform is None:
            from source_control.factory import create_source_control_platform

            self._platform = create_source_control_platform()
        return self._platform

    def _root(self) -> Path:
        root = self._instance_root or discover_instance_root()
        if root is None:
            raise ManifestNotFoundError("company.yaml not found")
        return root.resolve()

    @property
    def platform(self):
        return self._get_platform()

    @property
    def engine(self):
        return self._get_platform().engine

    @property
    def resolver(self):
        return self._get_platform().resolver

    @property
    def validator(self):
        return self._get_platform().validator

    @property
    def commit_engine(self):
        return self._get_platform().commit_engine

    @property
    def branch_manager(self):
        return self._get_platform().branch_manager

    @property
    def release_planner(self):
        return self._get_platform().release_planner

    @property
    def providers(self):
        return self._get_platform().providers

    def resolve(self, **kwargs):
        return self._get_platform().resolve(self._instance_root, **kwargs)

    def status(self) -> dict:
        return self._get_platform().status(self._instance_root)

    def validate(self) -> dict:
        return self._get_platform().validate(self._instance_root)

    def diff(self, **kwargs) -> str:
        return self._get_platform().diff(self._instance_root, **kwargs)

    def log(self, limit: int = 20) -> list[dict]:
        return self._get_platform().log(self._instance_root, limit=limit)

    def branches(self) -> list[str]:
        return self._get_platform().branches(self._instance_root)

    def checkout(self, branch: str) -> str:
        return self._get_platform().checkout(self._root(), branch)

    def stage(self, paths: list[str] | None = None) -> list[str]:
        return self._get_platform().stage(self._instance_root, paths)

    def unstage(self, paths: list[str] | None = None) -> list[str]:
        return self._get_platform().unstage(self._instance_root, paths)

    def generate_commit(self, **kwargs) -> CommitMessage:
        return self._get_platform().generate_commit(self._instance_root, **kwargs)

    def commit(self, message: str | None = None, *, require_approval: bool = True) -> CommitResult:
        return self._get_platform().commit(self._instance_root, message=message, require_approval=require_approval)

    def push(self, *, require_approval: bool = True, **kwargs) -> dict:
        return self._get_platform().push(self._instance_root, require_approval=require_approval, **kwargs)

    def tag(self, name: str, message: str = "", *, require_approval: bool = True) -> dict:
        return self._get_platform().tag(self._root(), name, message, require_approval=require_approval)

    def release(self, version: str | None = None) -> ReleasePlan:
        return self._get_platform().release(self._instance_root, version=version)

    def doctor(self) -> dict:
        return self._get_platform().doctor(self._instance_root)

    def approve(self, action: str, project_id: str | None = None, reason: str = "") -> dict:
        return self._get_platform().approve(self._root(), action, project_id, reason)

    def request_approval(self, action: str, project_id: str | None = None) -> dict:
        return self._get_platform().request_approval(self._root(), action, project_id)


class RepositoryAPI(SourceControlAPI):
    """Alias for repository-focused operations."""

    pass
