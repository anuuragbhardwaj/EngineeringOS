"""Autonomous Company Platform facade."""

from __future__ import annotations

from pathlib import Path

from autonomous_company.approvals.engine import ApprovalEngine
from autonomous_company.blockers.detector import BlockerDetector
from autonomous_company.decision_engine.engine import DecisionEngine
from autonomous_company.execution.sdlc import SdlcCompletion
from autonomous_company.goals.executor import GoalExecutor
from autonomous_company.monitor.monitor import Monitor
from autonomous_company.policies.store import AutonomousStore
from autonomous_company.recovery.manager import RecoveryManager
from autonomous_company.runner.runner import CompanyRunner
from autonomous_company.supervisor.supervisor import Supervisor
from autonomous_company.types import AutonomyStatus, ExecutionPolicy, Goal


class AutonomousCompanyPlatform:
    """Autonomous engineering company — CEO provides goals, EOS executes."""

    def __init__(self) -> None:
        self._store = AutonomousStore()
        self._runner = CompanyRunner()
        self._decisions = DecisionEngine(self._store)
        self._blockers = BlockerDetector(self._store)
        self._approvals = ApprovalEngine(self._store)
        self._goals = GoalExecutor(self._store)
        self._recovery = RecoveryManager(self._store)
        self._supervisor = Supervisor()
        self._monitor = Monitor(self._store)
        self._sdlc = SdlcCompletion()

    @property
    def runner(self) -> CompanyRunner:
        return self._runner

    @property
    def decision_engine(self) -> DecisionEngine:
        return self._decisions

    @property
    def blocker_detector(self) -> BlockerDetector:
        return self._blockers

    @property
    def approval_engine(self) -> ApprovalEngine:
        return self._approvals

    @property
    def goal_executor(self) -> GoalExecutor:
        return self._goals

    @property
    def recovery_manager(self) -> RecoveryManager:
        return self._recovery

    @property
    def supervisor(self) -> Supervisor:
        return self._supervisor

    def work(self, instance_root: Path, goal: str, project_id: str | None = None) -> dict:
        return self._runner.start(instance_root, goal_text=goal, project_id=project_id)

    def continue_execution(self, instance_root: Path) -> dict:
        return self._runner.continue_work(instance_root)

    def stop(self, instance_root: Path) -> dict:
        return self._runner.stop(instance_root)

    def pause(self, instance_root: Path) -> dict:
        return self._runner.pause(instance_root)

    def resume(self, instance_root: Path) -> dict:
        return self._runner.resume(instance_root)

    def status(self, instance_root: Path) -> AutonomyStatus:
        return self._supervisor.status(instance_root)

    def goals(self, instance_root: Path) -> list[Goal]:
        return self._store.list_goals(instance_root)

    def blockers(self, instance_root: Path) -> list:
        runner = self._store.load_runner_state(instance_root)
        return [b.to_dict() for b in self._blockers.detect(instance_root, runner)]

    def approvals_pending(self, instance_root: Path) -> list:
        return [a.to_dict() for a in self._approvals.pending(instance_root)]

    def approve(self, instance_root: Path, gate: str, project_id: str | None = None, reason: str = "") -> dict:
        from workspace_execution.resolver.resolver import ContextResolver

        pid = project_id or ContextResolver().resolve(instance_root).session.project_id or "company"
        return self._approvals.approve(instance_root, pid, gate, reason=reason).to_dict()

    def supervise(self, instance_root: Path) -> dict:
        return self._supervisor.supervise_cycle(instance_root)

    def monitor(self, instance_root: Path) -> dict:
        return self._monitor.snapshot(instance_root)

    def heartbeat(self, instance_root: Path) -> dict:
        return self._monitor.heartbeat(instance_root)

    def recover(self, instance_root: Path) -> dict:
        return self._recovery.recover(instance_root)

    def explain(self, instance_root: Path) -> dict:
        status = self.status(instance_root)
        return {
            "status": status.to_dict(),
            "latest_decision": status.recent_decisions[-1].to_dict() if status.recent_decisions else None,
        }

    def decisions(self, instance_root: Path, limit: int = 20) -> list:
        return [d.to_dict() for d in self._store.list_decisions(instance_root, limit)]

    def complete_sdlc(self, instance_root: Path, **kwargs) -> dict:
        return self._sdlc.run(instance_root, **kwargs)

    def policy(self, instance_root: Path) -> ExecutionPolicy:
        return self._store.load_policy(instance_root)

    def set_policy(self, instance_root: Path, policy: ExecutionPolicy) -> None:
        self._store.save_policy(instance_root, policy)
