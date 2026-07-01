"""Release preparation — prepare only, do not publish."""

from __future__ import annotations

from pathlib import Path

from source_control.commits.engine import CommitEngine
from source_control.types import ReleasePlan, RepositoryContext


class ReleasePlanner:
    """Prepare annotated tags, summaries, and release manifests."""

    def __init__(self, commit_engine: CommitEngine | None = None) -> None:
        self._commits = commit_engine or CommitEngine()

    def plan(
        self,
        repo_ctx: RepositoryContext,
        *,
        version: str | None = None,
        instance_root: Path | None = None,
    ) -> ReleasePlan:
        message = self._commits.generate(
            repo_ctx,
            instance_root=instance_root,
            phase_id="release",
        )
        ver = version or self._suggest_version(message.semantic_impact)
        tag_name = f"v{ver}"
        changelog_entries = self._changelog_entries(instance_root, repo_ctx.project_id)
        summary = self._build_summary(repo_ctx, ver, changelog_entries)

        return ReleasePlan(
            version=ver,
            tag_name=tag_name,
            summary=summary,
            changelog_entries=changelog_entries,
            manifest={
                "version": ver,
                "project_id": repo_ctx.project_id,
                "workspace_id": repo_ctx.workspace_id,
                "repo_root": repo_ctx.repo_root,
                "branch": repo_ctx.current_branch,
            },
            github_payload={
                "tag_name": tag_name,
                "name": f"Release {tag_name}",
                "body": summary,
                "draft": True,
                "prerelease": "alpha" in ver or "beta" in ver,
            },
            semantic_impact=message.semantic_impact,
        )

    def _suggest_version(self, impact: str) -> str:
        # Placeholder — real bump would read current tags
        base = "1.0.0"
        parts = base.split(".")
        if impact == "major":
            return f"{int(parts[0]) + 1}.0.0"
        if impact == "minor":
            return f"{parts[0]}.{int(parts[1]) + 1}.0"
        return f"{parts[0]}.{parts[1]}.{int(parts[2]) + 1}"

    def _changelog_entries(self, instance_root: Path | None, project_id: str | None) -> list[str]:
        if not instance_root or not project_id:
            return []
        try:
            from knowledge.git_hooks.extension import GitKnowledgeExtension

            ext = GitKnowledgeExtension()
            notes = ext.release_notes(Path(instance_root), project_id)
            return [f"- {n.get('title', '')}: {n.get('content', '')[:100]}" for n in notes[:10]]
        except Exception:
            return []

    def _build_summary(
        self, repo_ctx: RepositoryContext, version: str, entries: list[str]
    ) -> str:
        lines = [
            f"# Release {version}",
            "",
            f"Project: {repo_ctx.project_id or '—'}",
            f"Workspace: {repo_ctx.workspace_id or '—'}",
            "",
        ]
        if entries:
            lines.append("## Changes")
            lines.extend(entries)
        else:
            lines.append("## Changes")
            lines.append("- See commit history for details")
        return "\n".join(lines)
