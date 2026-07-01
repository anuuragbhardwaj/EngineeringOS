"""Execution monitor and heartbeat."""

from __future__ import annotations

from pathlib import Path

from autonomous_company.policies.store import AutonomousStore
from autonomous_company.types import utc_now


class Monitor:
    """Monitor autonomous execution progress."""

    def __init__(self, store: AutonomousStore | None = None) -> None:
        self._store = store or AutonomousStore()

    def heartbeat(self, instance_root: Path) -> dict:
        runner = self._store.load_runner_state(instance_root)
        runner.last_heartbeat = utc_now()
        self._store.save_runner_state(instance_root, runner)
        return {
            "status": runner.status,
            "project_id": runner.project_id,
            "phase": runner.current_phase,
            "heartbeat": runner.last_heartbeat,
            "alive": not runner.stopped,
        }

    def snapshot(self, instance_root: Path) -> dict:
        from autonomous_company.supervisor.supervisor import Supervisor

        status = Supervisor().status(instance_root)
        return status.to_dict()
