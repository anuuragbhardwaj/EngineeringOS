"""Persistent session storage inside generated companies."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import yaml

from workspace_execution.context.types import SessionContext

SESSION_DIR = Path(".company") / "session"
SESSION_FILE = SESSION_DIR / "execution.yaml"
LEGACY_SESSION = Path(".company") / "instance" / "session.yaml"


def company_paths(instance_root: Path) -> dict[str, Path]:
    base = instance_root / ".company"
    return {
        "session": base / "session",
        "history": base / "history",
        "recent": base / "recent",
        "favorites": base / "favorites",
        "checkpoints": base / "checkpoints",
        "knowledge": base / "knowledge",
    }


def ensure_company_dirs(instance_root: Path) -> None:
    for path in company_paths(instance_root).values():
        path.mkdir(parents=True, exist_ok=True)


def session_path(instance_root: Path) -> Path:
    return instance_root / SESSION_FILE


def load_session(instance_root: Path) -> SessionContext:
    instance_root = instance_root.resolve()
    path = session_path(instance_root)
    if path.is_file():
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return _from_dict(data, instance_root)

    legacy = instance_root / LEGACY_SESSION
    if legacy.is_file():
        with legacy.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        session = SessionContext(
            instance_root=str(instance_root),
            workspace_id=data.get("active_workspace"),
            project_id=data.get("active_project"),
            last_activity=data.get("opened_at"),
        )
        save_session(instance_root, session)
        return session

    return SessionContext(instance_root=str(instance_root))


def save_session(instance_root: Path, session: SessionContext) -> Path:
    instance_root = instance_root.resolve()
    ensure_company_dirs(instance_root)
    session.instance_root = str(instance_root)
    session.last_activity = datetime.utcnow().isoformat()
    path = session_path(instance_root)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(_to_dict(session), handle, sort_keys=False, default_flow_style=False)
    return path


def _to_dict(session: SessionContext) -> dict:
    return {
        "framework_version": session.framework_version,
        "company_id": session.company_id,
        "instance_root": session.instance_root,
        "workspace_id": session.workspace_id,
        "project_id": session.project_id,
        "pipeline": session.pipeline,
        "current_phase": session.current_phase,
        "current_gate": session.current_gate,
        "current_employee": session.current_employee,
        "execution_status": session.execution_status,
        "conversation_ids": session.conversation_ids,
        "runtime_state_location": session.runtime_state_location,
        "checkpoint_id": session.checkpoint_id,
        "last_activity": session.last_activity,
        "recent_commands": session.recent_commands[-50:],
        "recent_projects": session.recent_projects[:20],
        "recent_workspaces": session.recent_workspaces[:20],
        "provider_id": session.provider_id,
        "pinned_workspaces": session.pinned_workspaces,
        "pinned_projects": session.pinned_projects,
        "favorite_workspaces": session.favorite_workspaces,
        "favorite_projects": session.favorite_projects,
    }


def _from_dict(data: dict, instance_root: Path) -> SessionContext:
    return SessionContext(
        framework_version=str(data.get("framework_version", "2.0.0")),
        company_id=data.get("company_id"),
        instance_root=data.get("instance_root") or str(instance_root),
        workspace_id=data.get("workspace_id"),
        project_id=data.get("project_id"),
        pipeline=data.get("pipeline"),
        current_phase=data.get("current_phase"),
        current_gate=data.get("current_gate"),
        current_employee=data.get("current_employee"),
        execution_status=str(data.get("execution_status", "idle")),
        conversation_ids=dict(data.get("conversation_ids") or {}),
        runtime_state_location=data.get("runtime_state_location"),
        checkpoint_id=data.get("checkpoint_id"),
        last_activity=data.get("last_activity"),
        recent_commands=list(data.get("recent_commands") or []),
        recent_projects=list(data.get("recent_projects") or []),
        recent_workspaces=list(data.get("recent_workspaces") or []),
        provider_id=data.get("provider_id"),
        pinned_workspaces=list(data.get("pinned_workspaces") or []),
        pinned_projects=list(data.get("pinned_projects") or []),
        favorite_workspaces=list(data.get("favorite_workspaces") or []),
        favorite_projects=list(data.get("favorite_projects") or []),
    )
