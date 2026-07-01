"""Parallel execution platform tests."""

from __future__ import annotations

import time

import pytest

from parallel_execution.conflicts.detector import ConflictDetector
from parallel_execution.dependency_graph.builder import DependencyGraphBuilder
from parallel_execution.errors import ConflictDetectedError, DependencyCycleError
from parallel_execution.execution_plan.builder import ExecutionPlanBuilder
from parallel_execution.factory import create_parallel_execution_platform
from parallel_execution.types import WorkerStatus, WorkerTask
from parallel_execution.workers.pool import WorkerPool


def test_dependency_graph_implementation() -> None:
    builder = DependencyGraphBuilder()
    graph = builder.build_phase_graph("implementation")
    assert len(graph.nodes) == 3
    assert len(graph.parallel_groups) == 1
    assert len(graph.parallel_groups[0]) == 3
    builder.validate_acyclic(graph)


def test_sequential_phase_graph() -> None:
    builder = DependencyGraphBuilder()
    graph = builder.build_phase_graph("architecture")
    assert len(graph.nodes) == 1
    assert graph.parallel_groups == []


def test_execution_plan_build() -> None:
    platform = create_parallel_execution_platform()
    plan = platform.plan("proj-1", "implementation")
    assert plan.project_id == "proj-1"
    assert len(plan.workers) == 3
    assert len(plan.groups) == 1


def test_parallel_worker_execution() -> None:
    platform = create_parallel_execution_platform()
    plan = platform.plan("proj-1", "implementation")
    results: list[str] = []

    def invoke(**kwargs):
        time.sleep(0.01)
        results.append(kwargs["worker_id"])

    summary = platform.execute(plan, invoke)
    assert summary.completed == 3
    assert summary.failed == 0
    assert summary.merge_result and summary.merge_result.merged
    assert len(results) == 3


def test_worker_pool_completes_all() -> None:
    pool = WorkerPool()
    plan = create_parallel_execution_platform().plan("p", "implementation")
    completed: list[str] = []

    def invoke(**kwargs):
        completed.append(kwargs["worker_id"])

    pool.execute_plan(plan, invoke)
    assert len(completed) == 3


def test_conflict_detection_same_artifact() -> None:
    detector = ConflictDetector()
    workers = [
        WorkerTask("w1", "a", "impl", "artifact.md", 0, metadata={"subsystem": "a"}),
        WorkerTask("w2", "b", "impl", "artifact.md", 0, metadata={"subsystem": "a"}),
    ]
    conflicts = detector.detect_artifact_conflicts(workers)
    assert len(conflicts) == 1
    with pytest.raises(ConflictDetectedError):
        detector.check_and_escalate(workers)


def test_no_conflict_different_subsystems() -> None:
    detector = ConflictDetector()
    workers = [
        WorkerTask("w1", "backend", "impl", "source_code", 0, metadata={"subsystem": "backend"}),
        WorkerTask("w2", "frontend", "impl", "source_code", 0, metadata={"subsystem": "frontend"}),
    ]
    conflicts = detector.detect_artifact_conflicts(workers)
    assert len(conflicts) == 0


def test_pause_cancel() -> None:
    platform = create_parallel_execution_platform()
    platform.pause()
    platform.cancel()
    assert platform.scheduler.pool.cancelled


def test_checkpoint_roundtrip(tmp_path) -> None:
    platform = create_parallel_execution_platform()
    plan = platform.plan("proj", "implementation")
    platform.scheduler._save_checkpoint(tmp_path, plan)
    loaded = platform.checkpoint(tmp_path)
    assert loaded["plan_id"] == plan.plan_id


def test_explain_plan() -> None:
    platform = create_parallel_execution_platform()
    plan = platform.plan("proj", "implementation")
    explanation = platform.explain(plan)
    assert "plan" in explanation
    assert "graph" in explanation
