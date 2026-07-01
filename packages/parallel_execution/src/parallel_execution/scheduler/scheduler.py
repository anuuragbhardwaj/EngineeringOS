"""Parallel execution scheduler."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

from parallel_execution.dependency_graph.builder import DependencyGraphBuilder
from parallel_execution.execution_plan.builder import ExecutionPlanBuilder
from parallel_execution.types import ExecutionPlan, ExecutionStats, ExecutionSummary, WorkerStatus
from parallel_execution.workers.pool import WorkerPool

CHECKPOINT_DIR = Path(".company") / "parallel_execution"
CHECKPOINT_FILE = CHECKPOINT_DIR / "checkpoint.json"


class ExecutionScheduler:
    """Build plans, spawn workers, track dependencies, pause/resume/cancel."""

    def __init__(self) -> None:
        self._graph_builder = DependencyGraphBuilder()
        self._plan_builder = ExecutionPlanBuilder(self._graph_builder)
        self._pool = WorkerPool()
        self._active_plan: ExecutionPlan | None = None
        self._instance_root: Path | None = None

    @property
    def pool(self) -> WorkerPool:
        return self._pool

    @property
    def active_plan(self) -> ExecutionPlan | None:
        return self._active_plan

    def build_plan(
        self,
        project_id: str,
        phase_id: str,
        *,
        workflow: object | None = None,
        specialists: dict[str, object] | None = None,
    ) -> ExecutionPlan:
        return self._plan_builder.build(
            project_id, phase_id, workflow=workflow, specialists=specialists
        )

    def build_graph(self, phase_id: str, workflow: object | None = None):
        return self._graph_builder.build_phase_graph(phase_id, workflow=workflow)

    def execute(
        self,
        plan: ExecutionPlan,
        invoke_fn: Callable[..., Any],
        *,
        publish_event: Callable[[str, dict], None] | None = None,
        instance_root: Path | None = None,
        **invoke_kwargs,
    ) -> ExecutionSummary:
        self._active_plan = plan
        self._instance_root = instance_root
        if instance_root:
            self._save_checkpoint(instance_root, plan)
        summary = self._pool.execute_plan(plan, invoke_fn, publish_event=publish_event, **invoke_kwargs)
        if instance_root:
            self._clear_checkpoint(instance_root)
        return summary

    def pause(self) -> None:
        self._pool.pause()

    def resume(self) -> None:
        self._pool.resume()

    def cancel(self) -> None:
        self._pool.cancel()
        if self._instance_root and self._active_plan:
            self._save_checkpoint(self._instance_root, self._active_plan, cancelled=True)

    def stats(self, plan: ExecutionPlan | None = None) -> ExecutionStats:
        plan = plan or self._active_plan
        if not plan:
            return ExecutionStats()
        active = sum(1 for w in plan.workers if w.status == WorkerStatus.RUNNING.value)
        completed = sum(1 for w in plan.workers if w.status == WorkerStatus.COMPLETED.value)
        failed = sum(1 for w in plan.workers if w.status == WorkerStatus.FAILED.value)
        return ExecutionStats(
            total_workers=len(plan.workers),
            active_workers=active,
            completed_workers=completed,
            failed_workers=failed,
            parallel_groups=len(plan.groups),
        )

    def explain(self, plan: ExecutionPlan) -> dict:
        graph = self._graph_builder.build_phase_graph(plan.phase_id)
        return {
            "plan": plan.to_dict(),
            "graph": graph.to_dict(),
            "stats": self.stats(plan).to_dict(),
        }

    def _save_checkpoint(self, instance_root: Path, plan: ExecutionPlan, cancelled: bool = False) -> None:
        path = instance_root / CHECKPOINT_FILE
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "plan_id": plan.plan_id,
            "phase_id": plan.phase_id,
            "project_id": plan.project_id,
            "cancelled": cancelled,
            "workers": [
                {"worker_id": w.worker_id, "status": w.status, "employee_id": w.employee_id}
                for w in plan.workers
            ],
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _clear_checkpoint(self, instance_root: Path) -> None:
        path = instance_root / CHECKPOINT_FILE
        if path.is_file():
            path.unlink()

    def load_checkpoint(self, instance_root: Path) -> dict | None:
        path = instance_root / CHECKPOINT_FILE
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
