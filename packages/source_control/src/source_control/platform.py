"""Source Control Platform facade."""

from __future__ import annotations

from pathlib import Path

from source_control.engine.engine import SourceControlEngine
from source_control.types import ApprovalAction, CommitMessage, CommitResult, ReleasePlan, RepositoryContext


class SourceControlPlatform:
    """Source control layer for EngineeringOS — owned by Source Control Engineer."""

    def __init__(self) -> None:
        self._engine = SourceControlEngine()

    @property
    def engine(self) -> SourceControlEngine:
        return self._engine

    @property
    def resolver(self):
        return self._engine.resolver

    @property
    def validator(self):
        return self._engine.validator

    @property
    def commit_engine(self):
        return self._engine.commit_engine

    @property
    def branch_manager(self):
        return self._engine.branch_manager

    @property
    def release_planner(self):
        return self._engine.release_planner

    @property
    def providers(self):
        return self._engine.providers

    @property
    def approval(self):
        return self._engine.approval

    def resolve(self, instance_root: Path | None = None, **kwargs) -> RepositoryContext:
        return self._engine.resolve(instance_root, **kwargs)

    def status(self, instance_root: Path | None = None) -> dict:
        repo = self.resolve(instance_root)
        return self._engine.status(repo).to_dict()

    def validate(self, instance_root: Path | None = None) -> dict:
        repo = self.resolve(instance_root)
        return self._engine.validate(repo).to_dict()

    def diff(self, instance_root: Path | None = None, **kwargs) -> str:
        repo = self.resolve(instance_root)
        return self._engine.diff(repo, **kwargs)

    def log(self, instance_root: Path | None = None, limit: int = 20) -> list[dict]:
        repo = self.resolve(instance_root)
        return self._engine.log(repo, limit=limit)

    def branches(self, instance_root: Path | None = None) -> list[str]:
        repo = self.resolve(instance_root)
        return self._engine.branch_manager.list_branches(repo)

    def checkout(self, instance_root: Path | None, branch: str) -> str:
        repo = self.resolve(instance_root)
        return self._engine.branch_manager.checkout(repo, branch)

    def stage(self, instance_root: Path | None = None, paths: list[str] | None = None) -> list[str]:
        repo = self.resolve(instance_root)
        return self._engine.stage(repo, paths)

    def unstage(self, instance_root: Path | None = None, paths: list[str] | None = None) -> list[str]:
        repo = self.resolve(instance_root)
        return self._engine.unstage(repo, paths)

    def generate_commit(self, instance_root: Path | None = None, **kwargs) -> CommitMessage:
        repo = self.resolve(instance_root)
        return self._engine.generate_commit_message(repo, **kwargs)

    def commit(
        self,
        instance_root: Path | None = None,
        *,
        message: str | None = None,
        require_approval: bool = True,
    ) -> CommitResult:
        repo = self.resolve(instance_root)
        return self._engine.commit(repo, message=message, require_approval=require_approval)

    def push(self, instance_root: Path | None = None, *, require_approval: bool = True, **kwargs) -> dict:
        repo = self.resolve(instance_root)
        return self._engine.push(repo, require_approval=require_approval, **kwargs)

    def tag(
        self,
        instance_root: Path | None,
        name: str,
        message: str = "",
        *,
        require_approval: bool = True,
    ) -> dict:
        repo = self.resolve(instance_root)
        return self._engine.tag(repo, name, message, require_approval=require_approval)

    def release(self, instance_root: Path | None = None, version: str | None = None) -> ReleasePlan:
        repo = self.resolve(instance_root)
        return self._engine.plan_release(repo, version=version)

    def doctor(self, instance_root: Path | None = None) -> dict:
        repo = self.resolve(instance_root)
        return self._engine.doctor(repo)

    def approve(self, instance_root: Path, action: str, project_id: str | None = None, reason: str = "") -> dict:
        root = Path(instance_root)
        pid = project_id or self.resolve(root).project_id or "company"
        record = self._engine.approval.approve(root, pid, action, reason=reason)
        return record.__dict__

    def request_approval(self, instance_root: Path, action: str, project_id: str | None = None) -> dict:
        root = Path(instance_root)
        pid = project_id or self.resolve(root).project_id or "company"
        record = self._engine.approval.request(root, pid, action)
        return record.__dict__
