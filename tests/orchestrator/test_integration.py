"""Runtime and AI platform integration tests."""

from pathlib import Path

from runtime_engine.factory import create_runtime

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_runtime_delegates_to_orchestrator(tmp_path: Path) -> None:
    runtime = create_runtime(framework_root=REPO_ROOT)
    assert hasattr(runtime, "_orchestrator")
    project_dir = tmp_path / "orch-int"
    runtime.init_project(
        "orch-int",
        artifact_root=str(project_dir),
        metadata={"name": "Orch", "description": "d", "platform": "web", "mode": "production"},
    )
    final = runtime.execute_planning_pipeline("orch-int")
    assert final.execution.pipeline_completed
    history = runtime.history("orch-int")
    assert "checkpoints" in history
    assert any(e.get("source") == "orchestrator" for e in history["execution"])
