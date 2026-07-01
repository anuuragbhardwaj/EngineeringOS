"""Kernel hardening validation tests."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from orchestrator.checkpoint.manager import CheckpointManager
from orchestrator.checkpoint.store import checkpoint_path
from runtime_engine.state.mutator import PipelineStateMutator


def test_company_core_has_no_runtime_engine_imports() -> None:
    root = Path(__file__).resolve().parents[2] / "packages" / "company_core" / "src" / "company_core"
    violations: list[str] = []
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("runtime_engine"):
                        violations.append(f"{path}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("runtime_engine"):
                violations.append(f"{path}: from {node.module}")
    assert violations == [], violations


def test_pipeline_state_mutator_owns_mutations(tmp_path: Path) -> None:
    from datetime import datetime

    from runtime_engine.types import ExecutionState, PhaseStatus, PipelineState, ProjectStatus
    from runtime_engine.version import SCHEMA_VERSION

    state = PipelineState(
        project_id="p1",
        status=ProjectStatus.ACTIVE,
        artifact_root=str(tmp_path),
        workflow_version="1.1",
        workflow_path="workflow.yaml",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        metadata={},
        current_phase_id="implementation",
        phase_status={},
        skip_risk_accepted={},
        gate_strikes={},
        artifact_index={},
        rework_history=[],
        gate_history=[],
        transition_history=[],
        execution=ExecutionState(),
        schema_version=SCHEMA_VERSION,
    )
    mutator = PipelineStateMutator(state)
    mutator.begin_phase_execution("implementation", "engineering-manager")
    assert state.phase_status["implementation"] == PhaseStatus.IN_PROGRESS
    mutator.set_project_paused()
    assert state.status == ProjectStatus.PAUSED


def test_checkpoints_persist_across_manager_instances(tmp_path: Path) -> None:
    mgr1 = CheckpointManager(instance_root=tmp_path)
    cp = mgr1.create("proj-a", "architecture", "software-architect", {"step": 1})
    mgr1.pause(cp.checkpoint_id)

    mgr2 = CheckpointManager(instance_root=tmp_path)
    history = mgr2.list_history("proj-a")
    assert len(history) >= 1
    assert history[-1].status == "paused"
    assert checkpoint_path(tmp_path, "proj-a").is_file()


def test_runtime_bridge_requires_configuration() -> None:
    from company_core.runtime_bridge import create_runtime, reset_runtime_factory

    reset_runtime_factory()
    with pytest.raises(RuntimeError, match="not configured"):
        create_runtime()
    from runtime_engine.factory import create_runtime as rt_factory
    from company_core.runtime_bridge import configure_runtime_factory

    configure_runtime_factory(rt_factory)
