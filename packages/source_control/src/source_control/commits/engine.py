"""Commit message generation using knowledge and change analysis."""

from __future__ import annotations

import re
from pathlib import Path

from source_control.providers.git import GitProvider
from source_control.types import CommitMessage, CommitType, RepositoryContext


class CommitEngine:
    """Generate conventional commit messages from changes and knowledge."""

    TYPE_PATTERNS: list[tuple[str, tuple[str, ...]]] = [
        (CommitType.TEST.value, ("test", "spec", "pytest")),
        (CommitType.DOCS.value, ("docs", "readme", "changelog", ".md")),
        (CommitType.CI.value, (".github", "ci", "workflow")),
        (CommitType.BUILD.value, ("build", "pyproject", "package.json", "setup")),
        (CommitType.STYLE.value, ("format", "lint", "style")),
        (CommitType.PERF.value, ("perf", "performance", "optimize")),
        (CommitType.REFACTOR.value, ("refactor", "restructure")),
        (CommitType.FIX.value, ("fix", "bug", "patch")),
        (CommitType.FEAT.value, ("feat", "add", "implement", "new")),
    ]

    def __init__(self, git: GitProvider | None = None) -> None:
        self._git = git or GitProvider()

    def generate(
        self,
        repo_ctx: RepositoryContext,
        *,
        instance_root: Path | None = None,
        phase_id: str | None = None,
        artifacts: list[str] | None = None,
        mcp_available: bool = True,
    ) -> CommitMessage:
        repo_root = Path(repo_ctx.repo_root)
        changed = self._git.changed_files(repo_root)
        commit_type = self._infer_type(changed)
        subsystems = self._infer_subsystems(changed)
        referenced_artifacts = [f for f in changed if f.endswith((".md", ".yaml", ".yml"))]
        referenced_adrs = [f for f in changed if "architecture" in f.lower() or "adr" in f.lower()]

        knowledge_hints: list[str] = []
        semantic_impact = "patch"
        confidence = 0.7 if mcp_available else 0.55

        if instance_root and repo_ctx.project_id:
            try:
                from knowledge.git_hooks.extension import GitKnowledgeExtension

                ext = GitKnowledgeExtension()
                knowledge_hints = ext.commit_message_hints(Path(instance_root), repo_ctx.project_id)
                semantic_impact = ext.semantic_version_suggestion(Path(instance_root), repo_ctx.project_id)
                confidence = min(1.0, confidence + 0.1)
            except Exception:
                pass

        title = self._build_title(commit_type, changed, phase_id)
        body = self._build_body(
            changed=changed,
            subsystems=subsystems,
            artifacts=referenced_artifacts or artifacts or [],
            adrs=referenced_adrs,
            knowledge_hints=knowledge_hints,
            phase_id=phase_id,
            project_id=repo_ctx.project_id,
        )

        return CommitMessage(
            commit_type=commit_type,
            title=title,
            body=body,
            affected_subsystems=subsystems,
            referenced_artifacts=referenced_artifacts,
            referenced_adrs=referenced_adrs,
            semantic_impact=semantic_impact,
            confidence=confidence,
        )

    def _infer_type(self, files: list[str]) -> str:
        joined = " ".join(files).lower()
        for commit_type, patterns in self.TYPE_PATTERNS:
            if any(p in joined for p in patterns):
                return commit_type
        return CommitType.CHORE.value

    def _infer_subsystems(self, files: list[str]) -> list[str]:
        subsystems: set[str] = set()
        for path in files:
            parts = Path(path).parts
            if len(parts) >= 2:
                subsystems.add("/".join(parts[:2]))
            elif parts:
                subsystems.add(parts[0])
        return sorted(subsystems)[:8]

    def _build_title(self, commit_type: str, changed: list[str], phase_id: str | None) -> str:
        if not changed:
            return phase_id or "update repository state"
        primary = changed[0]
        name = Path(primary).stem.replace("_", " ").replace("-", " ")
        if phase_id:
            return f"{phase_id}: {name}"
        return f"update {name}"[:72]

    def _build_body(
        self,
        *,
        changed: list[str],
        subsystems: list[str],
        artifacts: list[str],
        adrs: list[str],
        knowledge_hints: list[str],
        phase_id: str | None,
        project_id: str | None,
    ) -> str:
        lines: list[str] = []
        if project_id:
            lines.append(f"Project: {project_id}")
        if phase_id:
            lines.append(f"Phase: {phase_id}")
        if subsystems:
            lines.append(f"Affected: {', '.join(subsystems)}")
        if artifacts:
            lines.append(f"Artifacts: {', '.join(artifacts[:5])}")
        if adrs:
            lines.append(f"ADRs: {', '.join(adrs)}")
        if knowledge_hints:
            lines.append("")
            lines.append("Knowledge context:")
            for hint in knowledge_hints[:3]:
                lines.append(f"- {hint}")
        if changed:
            lines.append("")
            lines.append("Changed files:")
            for f in changed[:15]:
                lines.append(f"- {f}")
            if len(changed) > 15:
                lines.append(f"- ... and {len(changed) - 15} more")
        return "\n".join(lines)
