"""Active company/workspace session context."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

SESSION_REL = Path(".company") / "instance" / "session.yaml"


@dataclass
class SessionContext:
    instance_root: Path
    active_workspace: str | None = None
    active_project: str | None = None
    opened_at: str | None = None


def session_path(instance_root: Path) -> Path:
    return instance_root / SESSION_REL


def load_session(instance_root: Path) -> SessionContext:
    path = session_path(instance_root)
    if not path.is_file():
        return SessionContext(instance_root=instance_root)
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return SessionContext(
        instance_root=instance_root,
        active_workspace=data.get("active_workspace"),
        active_project=data.get("active_project"),
        opened_at=data.get("opened_at"),
    )


def save_session(ctx: SessionContext) -> Path:
    path = session_path(ctx.instance_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "active_workspace": ctx.active_workspace,
        "active_project": ctx.active_project,
        "opened_at": ctx.opened_at or datetime.utcnow().isoformat(),
    }
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(payload, handle, sort_keys=False, default_flow_style=False)
    return path
