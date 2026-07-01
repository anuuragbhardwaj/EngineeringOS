"""Execution plan builder from dependency graphs."""

from __future__ import annotations

import uuid

from parallel_execution.dependency_graph.builder import DependencyGraphBuilder
from parallel_execution.types import ExecutionPlan, ParallelGroup, WorkerTask


class ExecutionPlanBuilder:
    """Convert dependency graphs into executable plans."""

    def __init__(self, graph_builder: DependencyGraphBuilder | None = None) -> None:
        self._graphs = graph_builder or DependencyGraphBuilder()

    def build(
        self,
        project_id: str,
        phase_id: str,
        *,
        workflow: object | None = None,
        specialists: dict[str, object] | None = None,
    ) -> ExecutionPlan:
        graph = self._graphs.build_phase_graph(phase_id, workflow=workflow)
        self._graphs.validate_acyclic(graph)

        workers: list[WorkerTask] = []
        groups: list[ParallelGroup] = []

        if graph.parallel_groups:
            for group_idx, node_ids in enumerate(graph.parallel_groups):
                worker_ids: list[str] = []
                for node_id in sorted(node_ids):  # deterministic ordering
                    node = next(n for n in graph.nodes if n.node_id == node_id)
                    worker_id = f"worker-{node.employee_id}-{uuid.uuid4().hex[:6]}"
                    specialist = (specialists or {}).get(node.employee_id)
                    workers.append(
                        WorkerTask(
                            worker_id=worker_id,
                            employee_id=node.employee_id,
                            phase_id=phase_id,
                            deliverable=node.deliverable,
                            group_id=group_idx,
                            dependencies=list(node.dependencies),
                            specialist=specialist,
                            metadata=dict(node.metadata),
                        )
                    )
                    worker_ids.append(worker_id)
                groups.append(ParallelGroup(group_id=group_idx, worker_ids=sorted(worker_ids)))
        else:
            for node in graph.nodes:
                worker_id = f"worker-{node.employee_id}"
                workers.append(
                    WorkerTask(
                        worker_id=worker_id,
                        employee_id=node.employee_id,
                        phase_id=phase_id,
                        deliverable=node.deliverable,
                        group_id=0,
                        specialist=(specialists or {}).get(node.employee_id),
                    )
                )
            groups.append(ParallelGroup(group_id=0, worker_ids=[w.worker_id for w in workers]))

        # Source control always sequential tail
        sequential_tail = ["source-control-engineer"] if phase_id == "release" else []

        return ExecutionPlan(
            plan_id=f"plan-{uuid.uuid4().hex[:10]}",
            project_id=project_id,
            phase_id=phase_id,
            groups=groups,
            workers=workers,
            sequential_tail=sequential_tail,
        )
