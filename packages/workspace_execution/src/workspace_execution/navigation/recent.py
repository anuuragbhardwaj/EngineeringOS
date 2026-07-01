"""Recent workspaces and projects navigation."""

from __future__ import annotations

from pathlib import Path

import yaml

from workspace_execution.context.types import SessionContext
from workspace_execution.session.store import company_paths, ensure_company_dirs, load_session, save_session


def touch_workspace(instance_root: Path, workspace_id: str) -> None:
    session = load_session(instance_root)
    recent = [w for w in session.recent_workspaces if w != workspace_id]
    recent.insert(0, workspace_id)
    session.recent_workspaces = recent[:20]
    save_session(instance_root, session)
    _append_recent(instance_root, "workspaces", workspace_id)


def touch_project(instance_root: Path, project_id: str) -> None:
    session = load_session(instance_root)
    recent = [p for p in session.recent_projects if p != project_id]
    recent.insert(0, project_id)
    session.recent_projects = recent[:20]
    save_session(instance_root, session)
    _append_recent(instance_root, "projects", project_id)


def recent_workspaces(instance_root: Path) -> list[str]:
    return load_session(instance_root).recent_workspaces


def recent_projects(instance_root: Path) -> list[str]:
    return load_session(instance_root).recent_projects


def pin_workspace(instance_root: Path, workspace_id: str) -> SessionContext:
    session = load_session(instance_root)
    if workspace_id not in session.pinned_workspaces:
        session.pinned_workspaces.append(workspace_id)
    return _persist(instance_root, session)


def pin_project(instance_root: Path, project_id: str) -> SessionContext:
    session = load_session(instance_root)
    if project_id not in session.pinned_projects:
        session.pinned_projects.append(project_id)
    return _persist(instance_root, session)


def favorite_workspace(instance_root: Path, workspace_id: str) -> SessionContext:
    session = load_session(instance_root)
    if workspace_id not in session.favorite_workspaces:
        session.favorite_workspaces.append(workspace_id)
    return _persist(instance_root, session)


def favorite_project(instance_root: Path, project_id: str) -> SessionContext:
    session = load_session(instance_root)
    if project_id not in session.favorite_projects:
        session.favorite_projects.append(project_id)
    return _persist(instance_root, session)


def _persist(instance_root: Path, session: SessionContext) -> SessionContext:
    save_session(instance_root, session)
    return session


def _append_recent(instance_root: Path, kind: str, item_id: str) -> None:
    ensure_company_dirs(instance_root)
    path = company_paths(instance_root)["recent"] / f"{kind}.yaml"
    data: dict = {}
    if path.is_file():
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    items = [i for i in data.get("items", []) if i != item_id]
    items.insert(0, item_id)
    data["items"] = items[:20]
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)
