"""Autonomous company platform tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from autonomous_company.factory import create_autonomous_company_platform
from autonomous_company.types import DecisionAction, RunnerStatus


@pytest.fixture
def company_root(tmp_path: Path) -> Path:
    (tmp_path / "company.yaml").write_text(
        "company:\n  instance_id: auto-co\n  instance_version: '1.0.0'\n"
        "  schema_version: '1.0.0'\n  framework:\n    version: '2.0.0'\n"
        "  configuration:\n    workspaces_root: workspaces/\n    default_workspace: default\n",
        encoding="utf-8",
    )
    from workspace_execution.context.types import SessionContext
    from workspace_execution.session.store import save_session

    save_session(tmp_path, SessionContext(company_id="auto-co", workspace_id="dev", project_id="my-app"))
    return tmp_path


def test_create_goal(company_root: Path) -> None:
    platform = create_autonomous_company_platform()
    result = platform.work(company_root, "Implement user authentication")
    assert result.get("started") or result.get("goal")
    goals = platform.goals(company_root)
    assert len(goals) >= 1


def test_decision_engine_records(company_root: Path) -> None:
    platform = create_autonomous_company_platform()
    decision = platform.decision_engine.decide(
        company_root, platform.runner._store.load_runner_state(company_root)  # noqa: SLF001
    )
    assert decision.action
    assert decision.reason
    decisions = platform.decisions(company_root)
    assert len(decisions) >= 1


def test_approval_flow(company_root: Path) -> None:
    platform = create_autonomous_company_platform()
    platform.approval_engine.request(company_root, "my-app", "commit", reason="test")
    assert not platform.approval_engine.is_approved(company_root, "my-app", "commit")
    platform.approve(company_root, "commit", project_id="my-app")
    assert platform.approval_engine.is_approved(company_root, "my-app", "commit")


def test_blocker_detection_pending_approval(company_root: Path) -> None:
    from workspace_execution.session.store import load_session, save_session

    session = load_session(company_root)
    session.execution_status = "pending_approval"
    save_session(company_root, session)
    platform = create_autonomous_company_platform()
    runner = platform.runner._store.load_runner_state(company_root)  # noqa: SLF001
    blockers = platform.blocker_detector.detect(company_root, runner)
    assert any(b.blocker_type == "approval_required" for b in blockers)


def test_runner_stop(company_root: Path) -> None:
    platform = create_autonomous_company_platform()
    platform.work(company_root, "Build API")
    result = platform.stop(company_root)
    assert result.get("stopped")
    runner = platform.runner._store.load_runner_state(company_root)  # noqa: SLF001
    assert runner.stopped


def test_recovery(company_root: Path) -> None:
    platform = create_autonomous_company_platform()
    result = platform.recover(company_root)
    assert result.get("recovered")
    assert result.get("project_id") == "my-app"


def test_supervisor_status(company_root: Path) -> None:
    platform = create_autonomous_company_platform()
    status = platform.status(company_root)
    assert status.runner is not None
    assert status.policy is not None


def test_heartbeat(company_root: Path) -> None:
    platform = create_autonomous_company_platform()
    hb = platform.heartbeat(company_root)
    assert hb.get("alive") is not None


def test_goal_plan(company_root: Path) -> None:
    platform = create_autonomous_company_platform()
    goal = platform.goal_executor.create_goal(company_root, "Add payment processing")
    plan = platform.goal_executor.plan_from_goal(company_root, goal)
    assert "implementation" in plan["phases"]
    assert "senior-backend-engineer" in plan["employees"]
