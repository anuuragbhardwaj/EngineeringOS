"""Source control CLI tests."""

from pathlib import Path

import subprocess

from typer.testing import CliRunner

from company_cli.main import app


def test_repo_status_command(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "company.yaml").write_text(
        "company:\n  instance_id: co\n  instance_version: '1.0.0'\n"
        "  schema_version: '1.0.0'\n  framework:\n    version: '2.0.0'\n"
        "  configuration:\n    workspaces_root: workspaces/\n    default_workspace: dev\n",
        encoding="utf-8",
    )
    project = tmp_path / "workspaces" / "dev" / "projects" / "app"
    project.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=project, check=True, capture_output=True)

    from workspace_execution.context.types import SessionContext
    from workspace_execution.session.store import save_session

    save_session(tmp_path, SessionContext(workspace_id="dev", project_id="app"))
    monkeypatch.chdir(tmp_path)

    runner = CliRunner()
    result = runner.invoke(app, ["repo", "status", "--json"])
    assert result.exit_code == 0
    assert "branch" in result.stdout
