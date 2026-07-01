"""Repository status engine."""

from __future__ import annotations

from pathlib import Path

from source_control.providers.registry import ProviderRegistry
from source_control.types import RepositoryContext, RepositoryStatus


class StatusEngine:
    """Unified repository status."""

    def status(self, repo_ctx: RepositoryContext) -> RepositoryStatus:
        provider = ProviderRegistry().get(repo_ctx.provider_id)
        return provider.status(Path(repo_ctx.repo_root))
