"""Source control platform tests."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from source_control.errors import ApprovalRequiredError, RepositoryNotFoundError
from source_control.factory import create_source_control_platform
from source_control.providers.git import GitProvider
from source_control.repository.discovery import find_repo_root
from source_control.types import ApprovalAction


@pytest.fixture
def company_with_repo(tmp_path: Path) -> Path:
    (tmp_path / "company.yaml").write_text(
        "company:\n  instance_id: sc-co\n  instance_version: '1.0.0'\n"
        "  schema_version: '1.0.0'\n  framework:\n    version: '2.0.0'\n"
        "  configuration:\n    workspaces_root: workspaces/\n    default_workspace: dev\n",
        encoding="utf-8",
    )
    project = tmp_path / "workspaces" / "dev" / "projects" / "my-app"
    project.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=project, check=True, capture_output=True)
    (project / ".gitignore").write_text("*.pyc\n", encoding="utf-8")
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=project,
        check=True,
        capture_output=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=project,
        check=True,
        capture_output=True,
    )
    (project / "README.md").write_text("# App\n", encoding="utf-8")
    # Session
    from workspace_execution.context.types import SessionContext
    from workspace_execution.session.store import save_session

    save_session(tmp_path, SessionContext(company_id="sc-co", workspace_id="dev", project_id="my-app"))
    return tmp_path


def test_find_repo_root(company_with_repo: Path) -> None:
    project = company_with_repo / "workspaces" / "dev" / "projects" / "my-app"
    assert find_repo_root(project) == project.resolve()


def test_repository_discovery_from_context(company_with_repo: Path) -> None:
    platform = create_source_control_platform()
    repo = platform.resolve(company_with_repo)
    assert repo.project_id == "my-app"
    assert repo.workspace_id == "dev"
    assert (Path(repo.repo_root) / ".git").is_dir()


def test_repository_validation(company_with_repo: Path) -> None:
    platform = create_source_control_platform()
    repo = platform.resolve(company_with_repo)
    report = platform.validate(company_with_repo)
    assert report["valid"] is True


def test_status_and_diff(company_with_repo: Path) -> None:
    platform = create_source_control_platform()
    status = platform.status(company_with_repo)
    assert status["clean"] is False
    assert status.get("untracked") or status.get("unstaged")


def test_commit_generation(company_with_repo: Path) -> None:
    platform = create_source_control_platform()
    msg = platform.generate_commit(company_with_repo, phase_id="implementation")
    assert msg.title
    assert msg.commit_type in {"docs", "chore", "feat", "fix"}


def test_stage_and_commit_requires_approval(company_with_repo: Path) -> None:
    platform = create_source_control_platform()
    platform.stage(company_with_repo)
    with pytest.raises(ApprovalRequiredError):
        platform.commit(company_with_repo)


def test_commit_with_approval(company_with_repo: Path) -> None:
    platform = create_source_control_platform()
    platform.approve(company_with_repo, ApprovalAction.COMMIT.value)
    platform.stage(company_with_repo)
    result = platform.commit(company_with_repo)
    assert result.sha
    assert len(result.sha) == 40


def test_push_requires_approval(company_with_repo: Path) -> None:
    platform = create_source_control_platform()
    with pytest.raises(ApprovalRequiredError):
        platform.push(company_with_repo)


def test_release_planning(company_with_repo: Path) -> None:
    platform = create_source_control_platform()
    plan = platform.release(company_with_repo)
    assert plan.tag_name.startswith("v")
    assert plan.summary


def test_provider_abstraction() -> None:
    platform = create_source_control_platform()
    providers = platform.providers.list_providers()
    assert any(p["id"] == "git" and p["implemented"] for p in providers)
    assert any(p["id"] == "github" and not p["implemented"] for p in providers)


def test_no_repo_raises(company_with_repo: Path) -> None:
    platform = create_source_control_platform()
    from workspace_execution.session.store import load_session, save_session

    session = load_session(company_with_repo)
    session.project_id = "nonexistent"
    save_session(company_with_repo, session)
    with pytest.raises(RepositoryNotFoundError):
        platform.resolve(company_with_repo)


def test_git_provider_log(company_with_repo: Path) -> None:
    platform = create_source_control_platform()
    platform.approve(company_with_repo, ApprovalAction.COMMIT.value)
    platform.stage(company_with_repo)
    platform.commit(company_with_repo, message="test: initial commit")
    entries = platform.log(company_with_repo)
    assert entries
