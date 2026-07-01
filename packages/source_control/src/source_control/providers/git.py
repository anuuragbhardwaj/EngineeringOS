"""Git provider — default source control implementation."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from source_control.errors import GitCommandError
from source_control.types import CommitResult, FileChange, RepositoryStatus


class GitProvider:
    """Git implementation via subprocess — sole executor of git commands."""

    provider_id = "git"

    def is_available(self) -> bool:
        try:
            result = subprocess.run(
                ["git", "--version"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except OSError:
            return False

    def status(self, repo_root: Path) -> RepositoryStatus:
        repo_root = repo_root.resolve()
        branch = self.current_branch(repo_root)
        porcelain = self._run(["status", "--porcelain", "-b"], repo_root)
        staged: list[FileChange] = []
        unstaged: list[FileChange] = []
        untracked: list[str] = []
        conflicts: list[str] = []
        detached = branch is None or self._is_detached(repo_root)

        for line in porcelain.splitlines():
            if line.startswith("##"):
                continue
            if len(line) < 3:
                continue
            index_status, worktree_status = line[0], line[1]
            path = line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1]
            if index_status == "?" and worktree_status == "?":
                untracked.append(path)
            elif index_status == "U" or worktree_status == "U":
                conflicts.append(path)
            else:
                if index_status != " ":
                    staged.append(FileChange(path=path, status=self._status_char(index_status)))
                if worktree_status != " ":
                    unstaged.append(FileChange(path=path, status=self._status_char(worktree_status)))

        clean = not staged and not unstaged and not untracked and not conflicts
        return RepositoryStatus(
            repo_root=str(repo_root),
            branch=branch,
            clean=clean,
            staged=staged,
            unstaged=unstaged,
            untracked=untracked,
            conflicts=conflicts,
            detached_head=detached,
        )

    def diff(self, repo_root: Path, *, staged: bool = False, path: str | None = None) -> str:
        args = ["diff"]
        if staged:
            args.append("--cached")
        if path:
            args.extend(["--", path])
        return self._run(args, repo_root)

    def log(self, repo_root: Path, limit: int = 20) -> list[dict]:
        output = self._run(
            ["log", f"-{limit}", "--pretty=format:%H|%s|%an|%ai"],
            repo_root,
        )
        entries = []
        for line in output.splitlines():
            if "|" not in line:
                continue
            sha, subject, author, date = line.split("|", 3)
            entries.append({"sha": sha, "subject": subject, "author": author, "date": date})
        return entries

    def branches(self, repo_root: Path) -> list[str]:
        output = self._run(["branch", "--format=%(refname:short)"], repo_root)
        return [line.strip() for line in output.splitlines() if line.strip()]

    def current_branch(self, repo_root: Path) -> str | None:
        try:
            return self._run(["rev-parse", "--abbrev-ref", "HEAD"], repo_root).strip() or None
        except GitCommandError:
            return None

    def checkout(self, repo_root: Path, branch: str) -> None:
        self._run(["checkout", branch], repo_root)

    def stage(self, repo_root: Path, paths: list[str] | None = None) -> list[str]:
        if paths:
            self._run(["add", "--"] + paths, repo_root)
            return paths
        self._run(["add", "-A"], repo_root)
        return self.status(repo_root).staged and [c.path for c in self.status(repo_root).staged] or []

    def unstage(self, repo_root: Path, paths: list[str] | None = None) -> list[str]:
        if paths:
            self._run(["restore", "--staged", "--"] + paths, repo_root)
            return paths
        self._run(["restore", "--staged", "."], repo_root)
        return []

    def commit(self, repo_root: Path, message: str) -> CommitResult:
        self._run(["commit", "-m", message], repo_root)
        sha = self._run(["rev-parse", "HEAD"], repo_root).strip()
        branch = self.current_branch(repo_root)
        files = self._run(["diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"], repo_root)
        return CommitResult(
            sha=sha,
            message=message,
            branch=branch,
            files=[f for f in files.splitlines() if f],
        )

    def push(self, repo_root: Path, remote: str = "origin", branch: str | None = None) -> dict:
        branch = branch or self.current_branch(repo_root)
        output = self._run(["push", remote, branch or "HEAD"], repo_root)
        return {"remote": remote, "branch": branch, "output": output}

    def tag(self, repo_root: Path, name: str, message: str = "", annotated: bool = True) -> dict:
        if annotated:
            self._run(["tag", "-a", name, "-m", message or name], repo_root)
        else:
            self._run(["tag", name], repo_root)
        return {"tag": name, "annotated": annotated, "message": message}

    def remote_url(self, repo_root: Path) -> str | None:
        try:
            return self._run(["remote", "get-url", "origin"], repo_root).strip() or None
        except GitCommandError:
            return None

    def init_repo(self, repo_root: Path) -> None:
        repo_root.mkdir(parents=True, exist_ok=True)
        if not (repo_root / ".git").exists():
            self._run(["init"], repo_root)

    def changed_files(self, repo_root: Path) -> list[str]:
        status = self.status(repo_root)
        files = [c.path for c in status.staged + status.unstaged]
        files.extend(status.untracked)
        return sorted(set(files))

    def _is_detached(self, repo_root: Path) -> bool:
        try:
            symbolic = self._run(["symbolic-ref", "-q", "HEAD"], repo_root)
            return not bool(symbolic.strip())
        except GitCommandError:
            return True

    def _status_char(self, char: str) -> str:
        mapping = {"M": "modified", "A": "added", "D": "deleted", "R": "renamed", "?": "untracked"}
        return mapping.get(char, char)

    def _run(self, args: list[str], cwd: Path) -> str:
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=cwd,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            raise GitCommandError(f"Git not available: {exc}") from exc
        if result.returncode != 0:
            raise GitCommandError(result.stderr.strip() or result.stdout.strip() or "git command failed")
        return result.stdout
