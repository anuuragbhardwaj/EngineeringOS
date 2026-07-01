"""ParallelExecutionAPI — Framework API surface."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from company_core.config.loader import discover_instance_root
from company_core.models.errors import ManifestNotFoundError
from parallel_execution.types import ExecutionPlan, ExecutionStats, ExecutionSummary


class ParallelExecutionAPI:
    """Expose parallel execution through FrameworkAPI."""

    def __init__(self, instance_root: Path | None = None) -> None:
        self._instance_root = instance_root
        self._platform = None

    def _get_platform(self):
        if self._platform is None:
            from parallel_execution.factory import create_parallel_execution_platform

            self._platform = create_parallel_execution_platform()
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
    def engine(self):
        return self._get_platform().engine

    @property
    def scheduler(self):
        return self._get_platform().scheduler

    def graph(self, phase_id: str, workflow: object | None = None) -> dict:
        return self._get_platform().graph(phase_id, workflow)

    def plan(self, project_id: str, phase_id: str, **kwargs) -> ExecutionPlan:
        return self._get_platform().plan(project_id, phase_id, **kwargs)

    def execute(self, plan: ExecutionPlan, invoke_fn: Callable, **kwargs) -> ExecutionSummary:
        return self._get_platform().execute(plan, invoke_fn, instance_root=self._root(), **kwargs)

    def status(self, plan: ExecutionPlan | None = None) -> dict:
        return self._get_platform().status(plan)

    def workers(self, plan: ExecutionPlan | None = None) -> list[dict]:
        return self._get_platform().workers(plan)

    def pause(self) -> None:
        self._get_platform().pause()

    def resume(self) -> None:
        self._get_platform().resume()

    def cancel(self) -> None:
        self._get_platform().cancel()

    def explain(self, plan: ExecutionPlan) -> dict:
        return self._get_platform().explain(plan)

    def stats(self, plan: ExecutionPlan | None = None) -> ExecutionStats:
        return self._get_platform().stats(plan)

    def checkpoint(self) -> dict | None:
        return self._get_platform().checkpoint(self._root())
