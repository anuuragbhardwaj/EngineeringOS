"""Parallel Execution Platform facade."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from parallel_execution.engine.engine import ParallelExecutionEngine
from parallel_execution.types import ExecutionPlan, ExecutionStats, ExecutionSummary


class ParallelExecutionPlatform:
    """Scheduling layer for concurrent employee execution."""

    def __init__(self) -> None:
        self._engine = ParallelExecutionEngine()

    @property
    def engine(self) -> ParallelExecutionEngine:
        return self._engine

    @property
    def scheduler(self):
        return self._engine.scheduler

    def graph(self, phase_id: str, workflow: object | None = None) -> dict:
        return self._engine.scheduler.build_graph(phase_id, workflow=workflow).to_dict()

    def plan(self, project_id: str, phase_id: str, **kwargs) -> ExecutionPlan:
        return self._engine.plan(project_id, phase_id, **kwargs)

    def execute(
        self,
        plan: ExecutionPlan,
        invoke_fn: Callable,
        *,
        instance_root: Path | None = None,
        publish_event: Callable | None = None,
        **kwargs,
    ) -> ExecutionSummary:
        return self._engine.execute(
            plan, invoke_fn, instance_root=instance_root, publish_event=publish_event, **kwargs
        )

    def status(self, plan: ExecutionPlan | None = None) -> dict:
        stats = self._engine.scheduler.stats(plan)
        return stats.to_dict()

    def workers(self, plan: ExecutionPlan | None = None) -> list[dict]:
        plan = plan or self._engine.scheduler.active_plan
        if not plan:
            return []
        return [
            {
                "worker_id": w.worker_id,
                "employee_id": w.employee_id,
                "deliverable": w.deliverable,
                "status": w.status,
                "group_id": w.group_id,
            }
            for w in plan.workers
        ]

    def pause(self) -> None:
        self._engine.scheduler.pause()

    def resume(self) -> None:
        self._engine.scheduler.resume()

    def cancel(self) -> None:
        self._engine.scheduler.cancel()

    def explain(self, plan: ExecutionPlan) -> dict:
        return self._engine.scheduler.explain(plan)

    def stats(self, plan: ExecutionPlan | None = None) -> ExecutionStats:
        return self._engine.scheduler.stats(plan)

    def checkpoint(self, instance_root: Path) -> dict | None:
        return self._engine.scheduler.load_checkpoint(instance_root)

    def resolve_specialists(self, registry: Any, phase_id: str, workflow: Any) -> dict[str, Any]:
        return self._engine.resolve_specialists(registry, phase_id, workflow)
