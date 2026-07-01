"""Session and checkpoint recovery."""

from __future__ import annotations

from pathlib import Path

from autonomous_company.policies.store import AutonomousStore
from autonomous_company.types import RunnerState, RunnerStatus, utc_now


class RecoveryManager:
    """Recover sessions after interruption."""

    def __init__(self, store: AutonomousStore | None = None) -> None:
        self._store = store or AutonomousStore()

    def recover(self, instance_root: Path) -> dict:
        """Restore company, workspace, project, and execution context."""
        from workspace_execution.resolver.resolver import ContextResolver

        resolver = ContextResolver()
        ctx = resolver.sync_runtime(instance_root)
        runner = self._store.load_runner_state(instance_root)

        if runner.stopped:
            runner.stopped = False
            runner.status = RunnerStatus.IDLE.value

        runner.project_id = runner.project_id or ctx.session.project_id
        runner.current_phase = ctx.session.current_phase
        runner.last_heartbeat = utc_now()
        self._store.save_runner_state(instance_root, runner)

        parallel_checkpoint = None
        try:
            from parallel_execution.factory import create_parallel_execution_platform

            parallel_checkpoint = create_parallel_execution_platform().checkpoint(instance_root)
        except Exception:
            pass

        return {
            "company_id": ctx.company_id,
            "workspace_id": ctx.session.workspace_id,
            "project_id": runner.project_id,
            "phase": runner.current_phase,
            "execution_status": ctx.session.execution_status,
            "parallel_checkpoint": parallel_checkpoint,
            "recovered": True,
        }
