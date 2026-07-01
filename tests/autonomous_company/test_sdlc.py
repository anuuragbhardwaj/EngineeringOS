"""SDLC completion and policy tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from autonomous_company.factory import create_autonomous_company_platform
from autonomous_company.types import BlockerType, DecisionAction, ExecutionPolicy


@pytest.fixture
def company_root(tmp_path: Path) -> Path:
    (tmp_path / "company.yaml").write_text(
        "company:\n  instance_id: sdlc-co\n  instance_version: '1.0.0'\n"
        "  schema_version: '1.0.0'\n  framework:\n    version: '2.0.0'\n"
        "  configuration:\n    workspaces_root: workspaces/\n    default_workspace: default\n",
        encoding="utf-8",
    )
    from workspace_execution.context.types import SessionContext
    from workspace_execution.session.store import save_session

    save_session(tmp_path, SessionContext(company_id="sdlc-co", workspace_id="dev", project_id="my-app"))
    return tmp_path


def test_sdlc_blocked_without_commit_approval(company_root: Path) -> None:
    platform = create_autonomous_company_platform()
    with patch(
        "autonomous_company.execution.sdlc.SdlcCompletion._validate_repo",
        return_value={"valid": True},
    ):
        result = platform.complete_sdlc(company_root, run_tests=False)
    assert result["status"] == "blocked"
    assert "approval" in result["reason"].lower()


def test_sdlc_completes_after_commit_approval(company_root: Path) -> None:
    platform = create_autonomous_company_platform()
    platform.approve(company_root, "commit", project_id="my-app")

    with (
        patch(
            "autonomous_company.execution.sdlc.SdlcCompletion._validate_repo",
            return_value={"valid": True},
        ),
        patch(
            "autonomous_company.execution.sdlc.SdlcCompletion._auto_commit",
            return_value={"sha": "abc123", "message": "feat: autonomous company"},
        ),
        patch(
            "autonomous_company.execution.sdlc.SdlcCompletion._prepare_release",
            return_value={"version": "1.0.0"},
        ),
    ):
        result = platform.complete_sdlc(company_root, run_tests=False)

    assert result["status"] == "completed"
    assert result["commit_sha"] == "abc123"


def test_retry_policy_on_recoverable_blocker(company_root: Path) -> None:
    platform = create_autonomous_company_platform()
    policy = ExecutionPolicy(max_retries=3)
    platform.set_policy(company_root, policy)

    runner = platform.runner._store.load_runner_state(company_root)  # noqa: SLF001
    runner.project_id = "my-app"
    runner.retry_count = 0
    platform.runner._store.save_runner_state(company_root, runner)

    blocker = platform.blocker_detector._make(  # noqa: SLF001
        BlockerType.RUNTIME_FAILURE,
        "Transient provider error",
        recoverable=True,
        project_id="my-app",
    )

    with (
        patch.object(platform.decision_engine._blockers, "detect", return_value=[blocker]),
        patch.object(platform.decision_engine._blockers, "has_blocking", return_value=True),
    ):
        decision = platform.decision_engine.decide(company_root, runner)

    assert decision.action == DecisionAction.RETRY.value


def test_autonomous_continuation(company_root: Path) -> None:
    platform = create_autonomous_company_platform()
    platform.work(company_root, "Ship feature flags")
    with patch(
        "workspace_execution.execution.resume.resume_execution",
        return_value={"status": "running", "phase_id": "implementation"},
    ):
        result = platform.continue_execution(company_root)
    assert result.get("cycles", 0) >= 1
