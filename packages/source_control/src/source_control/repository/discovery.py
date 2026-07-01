"""Repository discovery from execution context."""

from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path) -> Path | None:
    """Walk up from start looking for .git directory."""
    current = start.resolve()
    if (current / ".git").exists():
        return current
    for parent in current.parents:
        if (parent / ".git").exists():
            return parent
    return None


def discover_from_paths(*candidates: Path | None) -> Path | None:
    for candidate in candidates:
        if candidate is None:
            continue
        path = candidate if candidate.is_dir() else candidate.parent
        found = find_repo_root(path)
        if found:
            return found
    return None
