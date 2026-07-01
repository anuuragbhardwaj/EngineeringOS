"""State store persistence tests."""

from datetime import datetime
from pathlib import Path

from runtime_engine.version import SCHEMA_VERSION
from runtime_engine.state.serialize import load_state, save_state
from runtime_engine.state.store import JsonStateStore
from runtime_engine.types import (
    ExecutionState,
    PhaseStatus,
    PipelineState,
    ProjectStatus,
)


def _sample_state(project_id: str, root: Path) -> PipelineState:
    return PipelineState(
        project_id=project_id,
        status=ProjectStatus.ACTIVE,
        artifact_root=str(root),
        workflow_version="1.1",
        workflow_path="workflow.yaml",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        metadata={"name": "test"},
        current_phase_id="idea",
        phase_status={"idea": PhaseStatus.IN_PROGRESS},
        skip_risk_accepted={},
        gate_strikes={},
        artifact_index={},
        rework_history=[],
        gate_history=[],
        transition_history=[],
        execution=ExecutionState(),
        schema_version=SCHEMA_VERSION,
    )


def test_state_round_trip(tmp_path: Path) -> None:
    state = _sample_state("demo", tmp_path)
    path = tmp_path / ".runtime" / "state.json"
    save_state(path, state)
    loaded = load_state(path)
    assert loaded.project_id == "demo"
    assert loaded.current_phase_id == "idea"


def test_json_state_store(tmp_path: Path) -> None:
    store = JsonStateStore()
    store.register_project_path("demo", tmp_path)
    state = _sample_state("demo", tmp_path)
    store.save("demo", state)
    assert store.exists("demo")
    loaded = store.load("demo")
    assert loaded.metadata["name"] == "test"
