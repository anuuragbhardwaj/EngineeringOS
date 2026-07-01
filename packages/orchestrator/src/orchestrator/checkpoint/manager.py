"""Execution checkpoint management."""

from __future__ import annotations

import uuid
from datetime import datetime

from orchestrator.types import Checkpoint


class CheckpointManager:
    """Pause, resume, rollback, and continue via checkpoints."""

    def __init__(self) -> None:
        self._checkpoints: dict[str, Checkpoint] = {}
        self._history: list[Checkpoint] = []

    def create(
        self,
        project_id: str,
        phase_id: str,
        employee_id: str,
        metadata: dict | None = None,
    ) -> Checkpoint:
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
        return checkpoint

    def pause(self, checkpoint_id: str) -> Checkpoint:
        cp = self._get(checkpoint_id)
        cp.status = "paused"
        return cp

    def complete(self, checkpoint_id: str) -> Checkpoint:
        cp = self._get(checkpoint_id)
        cp.status = "completed"
        return cp

    def rollback(self, checkpoint_id: str) -> Checkpoint:
        cp = self._get(checkpoint_id)
        cp.status = "rolled_back"
        return cp

    def get_active(self, project_id: str) -> Checkpoint | None:
        for cp in reversed(self._history):
            if cp.project_id == project_id and cp.status in ("active", "paused"):
                return cp
        return None

    def list_history(self, project_id: str) -> list[Checkpoint]:
        return [cp for cp in self._history if cp.project_id == project_id]

    def _get(self, checkpoint_id: str) -> Checkpoint:
        if checkpoint_id not in self._checkpoints:
            raise KeyError(f"Checkpoint not found: {checkpoint_id}")
        return self._checkpoints[checkpoint_id]
