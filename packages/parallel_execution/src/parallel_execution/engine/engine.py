"""Parallel execution engine."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from parallel_execution.scheduler.scheduler import ExecutionScheduler
from parallel_execution.types import ExecutionPlan, ExecutionSummary


class ParallelExecutionEngine:
    """Central parallel execution orchestration."""

    def __init__(self, scheduler: ExecutionScheduler | None = None) -> None:
        self._scheduler = scheduler or ExecutionScheduler()

    @property
    def scheduler(self) -> ExecutionScheduler:
        return self._scheduler

    def plan(self, project_id: str, phase_id: str, **kwargs) -> ExecutionPlan:
        return self._scheduler.build_plan(project_id, phase_id, **kwargs)

    def execute(
        self,
        plan: ExecutionPlan,
        invoke_fn: Callable[..., Any],
        *,
        instance_root: Path | None = None,
        publish_event: Callable | None = None,
        **kwargs,
    ) -> ExecutionSummary:
        return self._scheduler.execute(
            plan, invoke_fn, publish_event=publish_event, instance_root=instance_root, **kwargs
        )

    def resolve_specialists(self, registry: Any, phase_id: str, workflow: Any) -> dict[str, Any]:
        """Resolve all parallel specialists for a phase."""
        graph = self._scheduler.build_graph(phase_id, workflow=workflow)
        specialists: dict[str, Any] = {}
        for node in graph.nodes:
            if node.employee_id in specialists:
                continue
            desc = self._resolve_agent(registry, node.employee_id, phase_id, workflow)
            if desc:
                specialists[node.employee_id] = desc
        return specialists

    def _resolve_agent(self, registry: Any, agent_id: str, phase_id: str, workflow: Any):
        if hasattr(registry, "resolve_agent"):
            return registry.resolve_agent(agent_id, phase_id, workflow)
