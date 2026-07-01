"""Runtime integration through AI Execution Platform."""

from pathlib import Path

from runtime_engine.factory import create_runtime

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_runtime_uses_execution_platform(tmp_path: Path) -> None:
    runtime = create_runtime(framework_root=REPO_ROOT)
    project_dir = tmp_path / "ai-boundary"
    runtime.init_project(
        "ai-boundary",
        artifact_root=str(project_dir),
        metadata={"name": "AI Boundary", "description": "test", "platform": "web"},
    )
    result = runtime.invoke_agent("ai-boundary")
    assert result.metadata.get("provider_id") in ("cursor", "scaffold")
    assert result.agent_id == "engineering-manager"


def test_full_pipeline_through_execution_platform(tmp_path: Path) -> None:
    runtime = create_runtime(framework_root=REPO_ROOT)
    project_dir = tmp_path / "pipeline-ai"
    runtime.init_project(
        "pipeline-ai",
        artifact_root=str(project_dir),
        metadata={
            "name": "Pipeline AI",
            "description": "AI platform test",
            "platform": "web",
            "mode": "production",
            "technology_stack": "Python",
        },
    )
    final = runtime.execute_planning_pipeline("pipeline-ai")
    assert final.execution.pipeline_completed
    assert (project_dir / "architecture.md").is_file()
