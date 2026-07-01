"""Parallel execution shared types."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class WorkerStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class BarrierType(str, Enum):
    WAIT_ALL = "wait_all"
    WAIT_ANY = "wait_any"
    MERGE = "merge"


@dataclass
class GraphNode:
    node_id: str
    employee_id: str
    phase_id: str
    deliverable: str
    artifact_owner: bool = True
    dependencies: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "node_id": self.node_id,
            "employee_id": self.employee_id,
            "phase_id": self.phase_id,
            "deliverable": self.deliverable,
            "dependencies": self.dependencies,
            "metadata": self.metadata,
        }


@dataclass
class DependencyGraph:
    nodes: list[GraphNode]
    phase_id: str
    parallel_groups: list[list[str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase_id": self.phase_id,
            "nodes": [n.to_dict() for n in self.nodes],
            "parallel_groups": self.parallel_groups,
        }


@dataclass
class WorkerTask:
    worker_id: str
    employee_id: str
    phase_id: str
    deliverable: str
    group_id: int
    dependencies: list[str] = field(default_factory=list)
    status: str = WorkerStatus.PENDING.value
    specialist: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParallelGroup:
    group_id: int
    worker_ids: list[str]
    barrier: str = BarrierType.WAIT_ALL.value


@dataclass
class ExecutionPlan:
    plan_id: str
    project_id: str
    phase_id: str
    groups: list[ParallelGroup]
    workers: list[WorkerTask]
    sequential_tail: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "project_id": self.project_id,
            "phase_id": self.phase_id,
            "groups": [g.__dict__ for g in self.groups],
            "workers": [
                {
                    "worker_id": w.worker_id,
                    "employee_id": w.employee_id,
                    "deliverable": w.deliverable,
                    "group_id": w.group_id,
                    "status": w.status,
                }
                for w in self.workers
            ],
            "sequential_tail": self.sequential_tail,
        }


@dataclass
class ConflictReport:
    conflict_type: str
    message: str
    workers: list[str] = field(default_factory=list)
    artifacts: list[str] = field(default_factory=list)
    escalated: bool = False

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__


@dataclass
class MergeResult:
    merged: bool
    artifacts: list[str] = field(default_factory=list)
    conflicts: list[ConflictReport] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "merged": self.merged,
            "artifacts": self.artifacts,
            "conflicts": [c.to_dict() for c in self.conflicts],
        }


@dataclass
class ExecutionSummary:
    plan_id: str
    completed: int
    failed: int
    cancelled: int
    duration_ms: float
    merge_result: MergeResult | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "completed": self.completed,
            "failed": self.failed,
            "cancelled": self.cancelled,
            "duration_ms": self.duration_ms,
            "merge_result": self.merge_result.to_dict() if self.merge_result else None,
        }


@dataclass
class ExecutionStats:
    total_workers: int = 0
    active_workers: int = 0
    completed_workers: int = 0
    failed_workers: int = 0
    parallel_groups: int = 0

    def to_dict(self) -> dict[str, Any]:
        return self.__dict__
