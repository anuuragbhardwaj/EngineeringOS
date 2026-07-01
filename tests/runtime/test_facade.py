"""Pipeline execution and facade tests."""

from pathlib import Path

import pytest

from runtime_engine.factory import create_runtime
from runtime_engine.types import PhaseStatus, ProjectStatus

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def runtime():
    return create_runtime(framework_root=REPO_ROOT)


def test_init_project(runtime, tmp_path: Path) -> None:
    project_dir = tmp_path / "my-project"
    state = runtime.init_project("my-project", artifact_root=str(project_dir))
    assert state.current_phase_id == "idea"
    assert state.status == ProjectStatus.ACTIVE
    assert project_dir.is_dir()


def test_planning_pipeline_completes(runtime, tmp_path: Path) -> None:
    project_dir = tmp_path / "pipeline-demo"
    runtime.init_project(
        "pipeline-demo",
        artifact_root=str(project_dir),
        metadata={
            "name": "Pipeline Demo",
            "description": "Test project",
            "platform": "web",
            "mode": "production",
            "technology_stack": "Python",
        },
    )
    final = runtime.execute_planning_pipeline("pipeline-demo")
    assert final.current_phase_id == "architecture"
    assert final.execution.pipeline_completed
    for artifact in (
        "idea.md",
        "requirements.md",
        "spec.md",
        "tasks.md",
        "architecture.md",
        "pipeline-status.md",
    ):
        assert (project_dir / artifact).is_file()


def test_em_only_direct_invocation(runtime, tmp_path: Path) -> None:
    project_dir = tmp_path / "em-test"
    runtime.init_project(
        "em-test",
        artifact_root=str(project_dir),
        metadata={"name": "EM", "description": "d", "platform": "x", "mode": "production"},
    )
    result = runtime.invoke_agent("em-test")
    assert result.agent_id == "engineering-manager"
    runtime.execute_planning_pipeline("em-test")
    history = runtime.history("em-test")
    specialists = {entry["specialist"] for entry in history["execution"]}
    assert "senior-product-manager" in specialists
    assert "senior-software-architect" in specialists
    # Runtime invoke_agent only targets orchestrator; specialists appear via EM delegation
    assert result.agent_id == "engineering-manager"


def test_resume_after_pause(runtime, tmp_path: Path) -> None:
    project_dir = tmp_path / "resume-demo"
    runtime.init_project("resume-demo", artifact_root=str(project_dir))
    runtime.pause("resume-demo")
    state = runtime.resume("resume-demo")
    assert state.status == ProjectStatus.ACTIVE


def test_illegal_advance_without_gate(runtime, tmp_path: Path) -> None:
    project_dir = tmp_path / "illegal"
    runtime.init_project("illegal", artifact_root=str(project_dir))
    from runtime_engine.errors import TransitionError

    with pytest.raises(TransitionError):
        runtime.advance("illegal")


def test_agent_registry_resolution(runtime) -> None:
    phase = runtime.workflow.phase_by_id("requirements")
    assert phase is not None
    agent = runtime._registry.resolve_primary("requirements", runtime.workflow)  # noqa: SLF001
    assert agent is not None
    assert agent.agent_id == "senior-product-manager"
    assert agent.primary_artifact == "requirements.md"
