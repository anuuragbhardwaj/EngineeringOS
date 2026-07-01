"""Repository validation with actionable diagnostics."""

from __future__ import annotations

from pathlib import Path

from source_control.providers.registry import ProviderRegistry
from source_control.types import RepositoryContext, ValidationIssue, ValidationReport


class RepositoryValidator:
    """Validate repository health before operations."""

    def validate(self, repo_ctx: RepositoryContext) -> ValidationReport:
        repo_root = Path(repo_ctx.repo_root)
        issues: list[ValidationIssue] = []

        if not (repo_root / ".git").is_dir():
            issues.append(
                ValidationIssue(
                    code="git_not_initialized",
                    message="Git is not initialized in this repository",
                    severity="error",
                    actionable="Run lifecycle init with --git or initialize manually",
                )
            )

        provider = ProviderRegistry().get(repo_ctx.provider_id)
        try:
            status = provider.status(repo_root)
        except Exception as exc:
            issues.append(
                ValidationIssue(
                    code="status_failed",
                    message=str(exc),
                    severity="error",
                    actionable="Verify git installation and repository integrity",
                )
            )
            return ValidationReport(valid=False, repo_root=str(repo_root), issues=issues)

        if status.detached_head:
            try:
                has_commits = bool(provider.log(repo_root, limit=1))
            except Exception:
                has_commits = False
            severity = "error" if has_commits else "warning"
            issues.append(
                ValidationIssue(
                    code="detached_head",
                    message="Repository is in detached HEAD state"
                    if has_commits
                    else "No commits yet — create initial commit",
                    severity=severity,
                    actionable="Checkout a branch and commit" if has_commits else "Stage files and create initial commit",
                )
            )

        if status.conflicts:
            issues.append(
                ValidationIssue(
                    code="merge_conflicts",
                    message=f"Unresolved conflicts: {', '.join(status.conflicts)}",
                    severity="error",
                    actionable="Resolve conflicts before committing",
                )
            )

        if not repo_ctx.remote_url:
            issues.append(
                ValidationIssue(
                    code="no_remote",
                    message="No remote origin configured",
                    severity="warning",
                    actionable="Add remote with: git remote add origin <url>",
                )
            )

        if repo_ctx.project_id and repo_ctx.workspace_id:
            expected = RepositoryResolver().project_root(
                Path(repo_ctx.instance_root), repo_ctx.workspace_id, repo_ctx.project_id
            )
            if not str(repo_root).startswith(str(expected.resolve())):
                issues.append(
                    ValidationIssue(
                        code="ownership_mismatch",
                        message="Repository is outside expected project directory",
                        severity="warning",
                        actionable=f"Expected repo under {expected}",
                    )
                )

        gitignore = repo_root / ".gitignore"
        if not gitignore.is_file():
            issues.append(
                ValidationIssue(
                    code="missing_gitignore",
                    message="No .gitignore file found",
                    severity="warning",
                    actionable="Add .gitignore to exclude build artifacts and secrets",
                )
            )

        valid = not any(i.severity == "error" for i in issues)
        return ValidationReport(valid=valid, repo_root=str(repo_root), issues=issues)


from source_control.repository.resolver import RepositoryResolver  # noqa: E402
