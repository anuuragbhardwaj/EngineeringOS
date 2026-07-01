"""AutonomousCompanyAPI — Framework API surface."""

from __future__ import annotations

from pathlib import Path

from company_core.config.loader import discover_instance_root
from company_core.models.errors import ManifestNotFoundError
from autonomous_company.types import AutonomyStatus, ExecutionPolicy, Goal


class AutonomousCompanyAPI:
    """Expose autonomous company through FrameworkAPI."""

    def __init__(self, instance_root: Path | None = None) -> None:
        self._instance_root = instance_root
        self._platform = None

    def _get_platform(self):
        if self._platform is None:
            from autonomous_company.factory import create_autonomous_company_platform

            self._platform = create_autonomous_company_platform()
        return self._platform

    def _root(self) -> Path:
        root = self._instance_root or discover_instance_root()
        if root is None:
            raise ManifestNotFoundError("company.yaml not found")
        return root.resolve()

    @property
    def platform(self):
        return self._get_platform()

    @property
    def runner(self):
        return self._get_platform().runner

    @property
    def decision_engine(self):
        return self._get_platform().decision_engine

    @property
    def blocker_detector(self):
        return self._get_platform().blocker_detector

    @property
    def approval_engine(self):
        return self._get_platform().approval_engine

    @property
    def goal_executor(self):
        return self._get_platform().goal_executor

    @property
    def recovery_manager(self):
        return self._get_platform().recovery_manager

    @property
    def supervisor(self):
        return self._get_platform().supervisor

    def work(self, goal: str, project_id: str | None = None) -> dict:
        return self._get_platform().work(self._root(), goal, project_id)

    def continue_execution(self) -> dict:
        return self._get_platform().continue_execution(self._root())

    def stop(self) -> dict:
        return self._get_platform().stop(self._root())

    def pause(self) -> dict:
        return self._get_platform().pause(self._root())

    def resume(self) -> dict:
        return self._get_platform().resume(self._root())

    def status(self) -> AutonomyStatus:
        return self._get_platform().status(self._root())

    def goals(self) -> list[Goal]:
        return self._get_platform().goals(self._root())

    def blockers(self) -> list:
        return self._get_platform().blockers(self._root())

    def approvals_pending(self) -> list:
        return self._get_platform().approvals_pending(self._root())

    def approve(self, gate: str, project_id: str | None = None, reason: str = "") -> dict:
        return self._get_platform().approve(self._root(), gate, project_id, reason)

    def supervise(self) -> dict:
        return self._get_platform().supervise(self._root())

    def monitor(self) -> dict:
        return self._get_platform().monitor(self._root())

    def heartbeat(self) -> dict:
        return self._get_platform().heartbeat(self._root())

    def recover(self) -> dict:
        return self._get_platform().recover(self._root())

    def explain(self) -> dict:
        return self._get_platform().explain(self._root())

    def decisions(self, limit: int = 20) -> list:
        return self._get_platform().decisions(self._root(), limit)

    def complete_sdlc(self, **kwargs) -> dict:
        return self._get_platform().complete_sdlc(self._root(), **kwargs)

    def policy(self) -> ExecutionPolicy:
        return self._get_platform().policy(self._root())
