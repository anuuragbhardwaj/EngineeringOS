"""Source control engine — orchestrates repository operations."""

from __future__ import annotations

from pathlib import Path

from source_control.branches.manager import BranchManager
from source_control.commits.engine import CommitEngine
from source_control.hooks.approval import SourceControlApproval
from source_control.providers.registry import ProviderRegistry
from source_control.release.planner import ReleasePlanner
from source_control.repository.resolver import RepositoryResolver
from source_control.status.engine import StatusEngine
from source_control.types import ApprovalAction, CommitMessage, CommitResult, ReleasePlan, RepositoryContext
from source_control.validation.validator import RepositoryValidator


class SourceControlEngine:
    """Central source control orchestration — owned by Source Control Engineer."""

    def __init__(self) -> None:
        self._resolver = RepositoryResolver()
        self._validator = RepositoryValidator()
        self._status = StatusEngine()
        self._commits = CommitEngine()
        self._branches = BranchManager()
        self._release = ReleasePlanner(self._commits)
        self._approval = SourceControlApproval()
        self._providers = ProviderRegistry()

    @property
    def resolver(self) -> RepositoryResolver:
        return self._resolver

    @property
    def validator(self) -> RepositoryValidator:
        return self._validator

    @property
    def approval(self) -> SourceControlApproval:
        return self._approval

    @property
    def commit_engine(self) -> CommitEngine:
        return self._commits

    @property
    def branch_manager(self) -> BranchManager:
        return self._branches

    @property
    def release_planner(self) -> ReleasePlanner:
        return self._release

    @property
    def providers(self) -> ProviderRegistry:
        return self._providers

    def resolve(self, instance_root: Path | None = None, **kwargs) -> RepositoryContext:
        return self._resolver.resolve(instance_root, **kwargs)

    def validate(self, repo_ctx: RepositoryContext):
        return self._validator.validate(repo_ctx)

    def status(self, repo_ctx: RepositoryContext):
        return self._status.status(repo_ctx)

    def diff(self, repo_ctx: RepositoryContext, **kwargs) -> str:
        provider = self._providers.get(repo_ctx.provider_id)
        return provider.diff(Path(repo_ctx.repo_root), **kwargs)

    def log(self, repo_ctx: RepositoryContext, limit: int = 20) -> list[dict]:
        provider = self._providers.get(repo_ctx.provider_id)
        return provider.log(Path(repo_ctx.repo_root), limit=limit)

    def stage(self, repo_ctx: RepositoryContext, paths: list[str] | None = None) -> list[str]:
        provider = self._providers.get(repo_ctx.provider_id)
        return provider.stage(Path(repo_ctx.repo_root), paths)

    def unstage(self, repo_ctx: RepositoryContext, paths: list[str] | None = None) -> list[str]:
        provider = self._providers.get(repo_ctx.provider_id)
        return provider.unstage(Path(repo_ctx.repo_root), paths)

    def generate_commit_message(self, repo_ctx: RepositoryContext, **kwargs) -> CommitMessage:
        return self._commits.generate(
            repo_ctx,
            instance_root=Path(repo_ctx.instance_root),
            **kwargs,
        )

    def commit(
        self,
        repo_ctx: RepositoryContext,
        *,
        message: str | None = None,
        require_approval: bool = True,
        stage_all: bool = True,
    ) -> CommitResult:
        project_id = repo_ctx.project_id or "company"
        if require_approval:
            self._approval.require(
                Path(repo_ctx.instance_root), project_id, ApprovalAction.COMMIT.value
            )
        provider = self._providers.get(repo_ctx.provider_id)
        repo_root = Path(repo_ctx.repo_root)
        if stage_all:
            provider.stage(repo_root, None)
        if not message:
            msg = self.generate_commit_message(repo_ctx)
            message = msg.full_message
        return provider.commit(repo_root, message)

    def push(
        self,
        repo_ctx: RepositoryContext,
        *,
        require_approval: bool = True,
        remote: str = "origin",
        branch: str | None = None,
    ) -> dict:
        project_id = repo_ctx.project_id or "company"
        if require_approval:
            self._approval.require(
                Path(repo_ctx.instance_root), project_id, ApprovalAction.PUSH.value
            )
        provider = self._providers.get(repo_ctx.provider_id)
        return provider.push(Path(repo_ctx.repo_root), remote=remote, branch=branch)

    def tag(
        self,
        repo_ctx: RepositoryContext,
        name: str,
        message: str = "",
        *,
        require_approval: bool = True,
    ) -> dict:
        project_id = repo_ctx.project_id or "company"
        if require_approval:
            self._approval.require(
                Path(repo_ctx.instance_root), project_id, ApprovalAction.RELEASE.value
            )
        provider = self._providers.get(repo_ctx.provider_id)
        return provider.tag(Path(repo_ctx.repo_root), name, message)

    def plan_release(self, repo_ctx: RepositoryContext, version: str | None = None) -> ReleasePlan:
        return self._release.plan(
            repo_ctx,
            version=version,
            instance_root=Path(repo_ctx.instance_root),
        )

    def doctor(self, repo_ctx: RepositoryContext) -> dict:
        validation = self.validate(repo_ctx)
        status = self.status(repo_ctx)
        return {
            "repository": repo_ctx.to_dict(),
            "validation": validation.to_dict(),
            "status": status.to_dict(),
            "providers": self._providers.list_providers(),
        }
