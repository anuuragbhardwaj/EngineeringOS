"""Persistent company runner."""

from __future__ import annotations

from pathlib import Path

from autonomous_company.approvals.engine import ApprovalEngine
from autonomous_company.errors import AutonomousStoppedError, BlockerError
from autonomous_company.goals.executor import GoalExecutor
from autonomous_company.policies.store import AutonomousStore
from autonomous_company.recovery.manager import RecoveryManager
from autonomous_company.supervisor.supervisor import Supervisor
from autonomous_company.types import RunnerState, RunnerStatus, utc_now


class CompanyRunner:
    """Persistent autonomous runner — continues until genuine blockers."""

    def __init__(self) -> None:
        self._store = AutonomousStore()
        self._supervisor = Supervisor()
        self._goals = GoalExecutor(self._store)
        self._recovery = RecoveryManager(self._store)
        self._approvals = ApprovalEngine(self._store)

    def start(self, instance_root: Path, *, goal_text: str | None = None, project_id: str | None = None) -> dict:
        self._recovery.recover(instance_root)
        runner = self._store.load_runner_state(instance_root)
        runner.status = RunnerStatus.RUNNING.value
        runner.stopped = False
        runner.started_at = utc_now()
        runner.retry_count = 0

        if goal_text:
            goal = self._goals.create_goal(instance_root, goal_text)
            runner.goal_id = goal.goal_id
            plan = self._goals.plan_from_goal(instance_root, goal)
            if project_id:
                self._goals.bind_goal_to_project(instance_root, goal.goal_id, project_id)
                runner.project_id = project_id
            return {"started": True, "goal": goal.to_dict(), "plan": plan, "runner": runner.to_dict()}

        if project_id:
            runner.project_id = project_id
            try:
                from workspace_execution.factory import create_execution_platform

                create_execution_platform().use_project(project_id, instance_root)
            except Exception:
                pass

        self._store.save_runner_state(instance_root, runner)
        return self.run_cycle(instance_root)

    def run_cycle(self, instance_root: Path, max_cycles: int = 1) -> dict:
        results = []
        for _ in range(max_cycles):
            runner = self._store.load_runner_state(instance_root)
            if runner.stopped:
                raise AutonomousStoppedError("Autonomous runner stopped")
            result = self._supervisor.supervise_cycle(instance_root)
            results.append(result)
            if result["decision"]["action"] in ("wait", "escalate", "pause", "terminate"):
                break
            runner = self._store.load_runner_state(instance_root)
            runner.current_phase = result.get("execution", {}).get("phase_id")
            if result.get("execution", {}).get("status") == "completed":
                runner.status = RunnerStatus.COMPLETED.value
                if runner.goal_id:
                    self._goals.complete_goal(instance_root, runner.goal_id)
                break
        return {"cycles": len(results), "results": results}

    def stop(self, instance_root: Path) -> dict:
        runner = self._store.load_runner_state(instance_root)
        runner.stopped = True
        runner.status = RunnerStatus.STOPPED.value
        self._store.save_runner_state(instance_root, runner)
        return {"stopped": True, "status": runner.status}

    def pause(self, instance_root: Path) -> dict:
        runner = self._store.load_runner_state(instance_root)
        runner.status = RunnerStatus.PAUSED.value
        self._store.save_runner_state(instance_root, runner)
        from workspace_execution.factory import create_execution_platform

        pid = runner.project_id
        if pid:
            create_execution_platform().pause(instance_root, pid)
        return {"paused": True}

    def resume(self, instance_root: Path) -> dict:
        runner = self._store.load_runner_state(instance_root)
        runner.stopped = False
        runner.status = RunnerStatus.RUNNING.value
        self._store.save_runner_state(instance_root, runner)
        return self.run_cycle(instance_root)

    def continue_work(self, instance_root: Path) -> dict:
        """OS-style continue — recover and run one cycle."""
        self._recovery.recover(instance_root)
        return self.run_cycle(instance_root)
