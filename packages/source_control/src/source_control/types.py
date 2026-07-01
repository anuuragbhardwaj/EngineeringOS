"""Source control shared types."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CommitType(str, Enum):
    FEAT = "feat"
    FIX = "fix"
    REFACTOR = "refactor"
    DOCS = "docs"
    TEST = "test"
    PERF = "perf"
    BUILD = "build"
    CI = "ci"
    STYLE = "style"
    CHORE = "chore"
    REVERT = "revert"


class ApprovalAction(str, Enum):
    COMMIT = "commit"
    PUSH = "push"
    RELEASE = "release"
    ROLLBACK = "rollback"


@dataclass
class RepositoryContext:
    """Resolved repository for active execution context."""

    repo_root: str
    instance_root: str
    workspace_id: str | None
    project_id: str | None
    provider_id: str = "git"
    remote_url: str | None = None
    current_branch: str | None = None
    is_detached: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_root": self.repo_root,
            "instance_root": self.instance_root,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "provider_id": self.provider_id,
            "remote_url": self.remote_url,
            "current_branch": self.current_branch,
            "is_detached": self.is_detached,
        }


@dataclass
class FileChange:
    path: str
    status: str  # modified, added, deleted, renamed, untracked


@dataclass
class RepositoryStatus:
    repo_root: str
    branch: str | None
    clean: bool
    ahead: int = 0
    behind: int = 0
    staged: list[FileChange] = field(default_factory=list)
    unstaged: list[FileChange] = field(default_factory=list)
    untracked: list[str] = field(default_factory=list)
    conflicts: list[str] = field(default_factory=list)
    detached_head: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "repo_root": self.repo_root,
            "branch": self.branch,
            "clean": self.clean,
            "ahead": self.ahead,
            "behind": self.behind,
            "staged": [c.__dict__ for c in self.staged],
            "unstaged": [c.__dict__ for c in self.unstaged],
            "untracked": self.untracked,
            "conflicts": self.conflicts,
            "detached_head": self.detached_head,
        }


@dataclass
class ValidationIssue:
    code: str
    message: str
    severity: str  # error | warning | info
    actionable: str = ""


@dataclass
class ValidationReport:
    valid: bool
    repo_root: str
    issues: list[ValidationIssue] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "valid": self.valid,
            "repo_root": self.repo_root,
            "issues": [i.__dict__ for i in self.issues],
        }


@dataclass
class CommitMessage:
    commit_type: str
    title: str
    body: str
    affected_subsystems: list[str] = field(default_factory=list)
    referenced_artifacts: list[str] = field(default_factory=list)
    referenced_adrs: list[str] = field(default_factory=list)
    semantic_impact: str = "patch"
    confidence: float = 0.8

    @property
    def full_message(self) -> str:
        header = f"{self.commit_type}: {self.title}"
        if self.body:
            return f"{header}\n\n{self.body}"
        return header

    def to_dict(self) -> dict[str, Any]:
        return {
            "commit_type": self.commit_type,
            "title": self.title,
            "body": self.body,
            "full_message": self.full_message,
            "affected_subsystems": self.affected_subsystems,
            "referenced_artifacts": self.referenced_artifacts,
            "referenced_adrs": self.referenced_adrs,
            "semantic_impact": self.semantic_impact,
            "confidence": self.confidence,
        }


@dataclass
class CommitResult:
    sha: str
    message: str
    branch: str | None
    files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"sha": self.sha, "message": self.message, "branch": self.branch, "files": self.files}


@dataclass
class ReleasePlan:
    version: str
    tag_name: str
    summary: str
    changelog_entries: list[str] = field(default_factory=list)
    manifest: dict[str, Any] = field(default_factory=dict)
    github_payload: dict[str, Any] = field(default_factory=dict)
    semantic_impact: str = "patch"

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "tag_name": self.tag_name,
            "summary": self.summary,
            "changelog_entries": self.changelog_entries,
            "manifest": self.manifest,
            "github_payload": self.github_payload,
            "semantic_impact": self.semantic_impact,
        }


@dataclass
class ApprovalRecord:
    action: str
    project_id: str
    approved: bool
    approved_by: str | None = None
    reason: str = ""
    timestamp: str = ""
