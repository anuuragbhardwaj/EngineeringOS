"""Workflow loader tests."""

from pathlib import Path

from runtime_engine.workflow.loader import WorkflowLoader

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_load_workflow_yaml() -> None:
    loader = WorkflowLoader()
    workflow = loader.load(str(REPO_ROOT / "workflow.yaml"))
    assert workflow.version == "1.1"
    assert len(workflow.phases) >= 11
    ids = [p.id for p in workflow.ordered_phases()]
    assert ids[0] == "idea"
    assert "architecture" in ids


def test_planning_phases_scope() -> None:
    loader = WorkflowLoader()
    workflow = loader.load(str(REPO_ROOT / "workflow.yaml"))
    planning = workflow.planning_phases()
    assert [p.id for p in planning] == [
        "idea",
        "requirements",
        "specification",
        "planning",
        "architecture",
    ]
