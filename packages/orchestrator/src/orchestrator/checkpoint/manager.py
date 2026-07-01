"""Execution checkpoint management."""

from __future__ import annotations

import uuid
from datetime import datetime
from pathlib import Path

from orchestrator.checkpoint.store import (
    _deserialize_checkpoint,
    load_project_checkpoints,
    save_project_checkpoints,
)
from orchestrator.types import Checkpoint


class CheckpointManager:
    """Pause, resume, rollback — persisted under .company/checkpoints/orchestrator/."""

    def __init__(self, instance_root: Path | str | None = None) -> None:
        self._instance_root = Path(instance_root).resolve() if instance_root else None
        self._checkpoints: dict[str, Checkpoint] = {}
        self._history: list[Checkpoint] = []
        self._loaded_projects: set[str] = set()

    def create(
        self,
        project_id: str,
        phase_id: str,
        employee_id: str,
        metadata: dict | None = None,
    ) -> Checkpoint:
        self._ensure_loaded(project_id)
        checkpoint = Checkpoint(
            checkpoint_id=str(uuid.uuid4()),
            project_id=project_id,
            phase_id=phase_id,
            employee_id=employee_id,
            created_at=datetime.utcnow(),
            status="active",
            metadata=dict(metadata or {}),
        )
        self._checkpoints[checkpoint.checkpoint_id] = checkpoint
        self._history.append(checkpoint)
        self._persist(project_id)
        return checkpoint

    def pause(self, checkpoint_id: str) -> Checkpoint:
        cp = self._get(checkpoint_id)
        cp.status = "paused"
        self._persist(cp.project_id)
        return cp

    def complete(self, checkpoint_id: str) -> Checkpoint:
        cp = self._get(checkpoint_id)
        cp.status = "completed"
        self._persist(cp.project_id)
        return cp

    def rollback(self, checkpoint_id: str) -> Checkpoint:
        cp = self._get(checkpoint_id)
        cp.status = "rolled_back"
        self._persist(cp.project_id)
        return cp

    def get_active(self, project_id: str) -> Checkpoint | None:
        self._ensure_loaded(project_id)
        for cp in reversed(self._history):
            if cp.project_id == project_id and cp.status in ("active", "paused"):
                return cp
        return None

    def list_history(self, project_id: str) -> list[Checkpoint]:
        self._ensure_loaded(project_id)
        return [cp for cp in self._history if cp.project_id == project_id]

    def _get(self, checkpoint_id: str) -> Checkpoint:
        if checkpoint_id not in self._checkpoints:
            raise KeyError(f"Checkpoint not found: {checkpoint_id}")
        return self._checkpoints[checkpoint_id]

    def _ensure_loaded(self, project_id: str) -> None:
        if not self._instance_root or project_id in self._loaded_projects:
            return
        raw_by_id, raw_history = load_project_checkpoints(self._instance_root, project_id)
        for data in raw_by_id.values():
            cp = Checkpoint(**_deserialize_checkpoint(data))
            self._checkpoints[cp.checkpoint_id] = cp
        for data in raw_history:
            cp = Checkpoint(**_deserialize_checkpoint(data))
            if cp.checkpoint_id not in self._checkpoints:
                self._checkpoints[cp.checkpoint_id] = cp
            if not any(h.checkpoint_id == cp.checkpoint_id for h in self._history):
                self._history.append(cp)
        self._loaded_projects.add(project_id)

    def _persist(self, project_id: str) -> None:
        if not self._instance_root:
            return
        project_cps = {cid: cp for cid, cp in self._checkpoints.items() if cp.project_id == project_id}
        history = [cp for cp in self._history if cp.project_id == project_id]
        save_project_checkpoints(self._instance_root, project_id, project_cps, history)
