"""Company supervisor — monitors lifecycle above orchestrator."""

from __future__ import annotations

from pathlib import Path

from autonomous_company.approvals.engine import ApprovalEngine
from autonomous_company.blockers.detector import BlockerDetector
from autonomous_company.decision_engine.engine import DecisionEngine
from autonomous_company.policies.store import AutonomousStore
from autonomous_company.types import AutonomyStatus, DecisionAction, RunnerState, RunnerStatus, utc_now


class Supervisor:
    """Supervise complete engineering lifecycle."""

    def __init__(self) -> None:
        self._store = AutonomousStore()
        self._decisions = DecisionEngine(self._store)
        self._blockers = BlockerDetector(self._store)
        self._approvals = ApprovalEngine(self._store)

    def status(self, instance_root: Path) -> AutonomyStatus:
        runner = self._store.load_runner_state(instance_root)
        goal = self._store.get_goal(instance_root, runner.goal_id) if runner.goal_id else None
        return AutonomyStatus(
            runner=runner,
            active_goal=goal,
            blockers=self._blockers.detect(instance_root, runner),
            pending_approvals=self._approvals.pending(instance_root),
            recent_decisions=self._store.list_decisions(instance_root, limit=10),
            policy=self._store.load_policy(instance_root),
        )

    def supervise_cycle(self, instance_root: Path) -> dict:
        """One supervision cycle — decide and act."""
        runner = self._store.load_runner_state(instance_root)
        decision = self._decisions.decide(instance_root, runner)
        result = {"decision": decision.to_dict(), "action_taken": decision.action}

        if decision.action == DecisionAction.CONTINUE.value:
            result["execution"] = self._continue_pipeline(instance_root, runner)
        elif decision.action == DecisionAction.RESUME.value:
            result["execution"] = self._continue_pipeline(instance_root, runner)
        elif decision.action == DecisionAction.RETRY.value:
            runner.retry_count += 1
            result["execution"] = self._continue_pipeline(instance_root, runner)
        elif decision.action == DecisionAction.WAIT.value:
            runner.status = RunnerStatus.BLOCKED.value
        elif decision.action == DecisionAction.PAUSE.value:
            runner.status = RunnerStatus.PAUSED.value
        elif decision.action == DecisionAction.ESCALATE.value:
            runner.status = RunnerStatus.BLOCKED.value
            for blocker in self._blockers.detect(instance_root, runner):
                self._store.record_blocker(instance_root, blocker)

        runner.last_heartbeat = utc_now()
        self._store.save_runner_state(instance_root, runner)
        return result

    def _continue_pipeline(self, instance_root: Path, runner: RunnerState) -> dict:
        from workspace_execution.execution.resume import resume_execution

        if not runner.project_id:
            from workspace_execution.resolver.resolver import ContextResolver

            ctx = ContextResolver().resolve(instance_root)
            runner.project_id = ctx.session.project_id
        if not runner.project_id:
            return {"status": "idle", "message": "No project bound to goal"}
        return resume_execution(instance_root, runner.project_id)
