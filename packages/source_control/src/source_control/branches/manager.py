"""Branch management."""

from __future__ import annotations

from pathlib import Path

from source_control.providers.registry import ProviderRegistry
from source_control.types import RepositoryContext


class BranchManager:
    """Branch operations via provider abstraction."""

    def list_branches(self, repo_ctx: RepositoryContext) -> list[str]:
        provider = ProviderRegistry().get(repo_ctx.provider_id)
        return provider.branches(Path(repo_ctx.repo_root))

    def checkout(self, repo_ctx: RepositoryContext, branch: str) -> str:
        provider = ProviderRegistry().get(repo_ctx.provider_id)
        provider.checkout(Path(repo_ctx.repo_root), branch)
        return branch

    def current(self, repo_ctx: RepositoryContext) -> str | None:
        provider = ProviderRegistry().get(repo_ctx.provider_id)
        return provider.current_branch(Path(repo_ctx.repo_root))
