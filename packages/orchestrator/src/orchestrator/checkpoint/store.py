"""Persistent orchestrator checkpoint storage under .company/checkpoints/."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

CHECKPOINT_SCHEMA_VERSION = "1.0.0"
CHECKPOINT_SUBDIR = Path(".company") / "checkpoints" / "orchestrator"


def checkpoint_path(instance_root: Path, project_id: str) -> Path:
    return instance_root / CHECKPOINT_SUBDIR / f"{project_id}.yaml"


def ensure_checkpoint_dir(instance_root: Path) -> Path:
    directory = instance_root / CHECKPOINT_SUBDIR
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _serialize_checkpoint(cp: Any) -> dict:
    return {
        "checkpoint_id": cp.checkpoint_id,
        "project_id": cp.project_id,
        "phase_id": cp.phase_id,
        "employee_id": cp.employee_id,
        "created_at": cp.created_at.isoformat() if isinstance(cp.created_at, datetime) else cp.created_at,
        "status": cp.status,
        "metadata": dict(cp.metadata or {}),
    }


def _deserialize_checkpoint(data: dict) -> dict:
    created = data.get("created_at", "")
    if isinstance(created, str):
        try:
            created = datetime.fromisoformat(created)
        except ValueError:
            created = datetime.utcnow()
    return {
        "checkpoint_id": data["checkpoint_id"],
        "project_id": data["project_id"],
        "phase_id": data["phase_id"],
        "employee_id": data["employee_id"],
        "created_at": created,
        "status": data.get("status", "active"),
        "metadata": dict(data.get("metadata") or {}),
    }


def load_project_checkpoints(instance_root: Path, project_id: str) -> tuple[dict[str, dict], list[dict]]:
    path = checkpoint_path(instance_root, project_id)
    if not path.is_file():
        return {}, []
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    history_raw = data.get("history", data.get("checkpoints", []))
    history = [_deserialize_checkpoint(c) for c in history_raw]
    by_id = {c["checkpoint_id"]: c for c in history}
    return by_id, history


def save_project_checkpoints(
    instance_root: Path,
    project_id: str,
    checkpoints: dict[str, Any],
    history: list[Any],
) -> None:
    ensure_checkpoint_dir(instance_root)
    path = checkpoint_path(instance_root, project_id)
    payload = {
        "schema_version": CHECKPOINT_SCHEMA_VERSION,
        "project_id": project_id,
        "checkpoints": [_serialize_checkpoint(cp) for cp in checkpoints.values()],
        "history": [_serialize_checkpoint(cp) for cp in history],
    }
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
