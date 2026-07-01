"""Repository resolver — derives repo from company/workspace/project context."""

from __future__ import annotations

from pathlib import Path

from source_control.errors import RepositoryNotFoundError
from source_control.repository.discovery import discover_from_paths
from source_control.types import RepositoryContext
from workspace_execution.session.store import load_session


class RepositoryResolver:
    """Resolve active repository from execution context — no manual paths."""

    def resolve(
        self,
        instance_root: Path | None = None,
        *,
        workspace_id: str | None = None,
        project_id: str | None = None,
        provider_id: str = "git",
    ) -> RepositoryContext:
        from company_core.config.loader import discover_instance_root, load_manifest

        root = instance_root or discover_instance_root()
        if root is None:
            raise RepositoryNotFoundError("No active company — open a company first")

        root = root.resolve()
        session = load_session(root)
        ws_id = workspace_id or session.workspace_id
        proj_id = project_id or session.project_id

        manifest = load_manifest(root / "company.yaml")
        project_root = None
        if ws_id and proj_id:
            project_root = (
                root / manifest.workspaces_root.strip("/") / ws_id / "projects" / proj_id
            )

        repo_root = discover_from_paths(project_root, root)
        if repo_root is None:
            raise RepositoryNotFoundError(
                f"No git repository found for project {proj_id or '—'} in workspace {ws_id or '—'}"
            )

        from source_control.providers.registry import ProviderRegistry

        provider = ProviderRegistry().get(provider_id)
        branch = provider.current_branch(repo_root)
        remote = provider.remote_url(repo_root)
        detached = branch is None or provider.status(repo_root).detached_head

        return RepositoryContext(
            repo_root=str(repo_root),
            instance_root=str(root),
            workspace_id=ws_id,
            project_id=proj_id,
            provider_id=provider_id,
            remote_url=remote,
            current_branch=branch,
            is_detached=detached,
        )

    def project_root(self, instance_root: Path, workspace_id: str, project_id: str) -> Path:
        from company_core.config.loader import load_manifest

        manifest = load_manifest(instance_root / "company.yaml")
        return instance_root / manifest.workspaces_root.strip("/") / workspace_id / "projects" / project_id
