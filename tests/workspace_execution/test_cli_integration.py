"""CLI integration for workspace execution."""

from pathlib import Path

from typer.testing import CliRunner

from company_cli.main import app

runner = CliRunner()


def test_current_after_init(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", ".", "--yes", "--name", "Ctx Co", "--id", "ctx", "--no-git"])
    runner.invoke(app, ["open"])
    result = runner.invoke(app, ["current"])
    assert result.exit_code == 0
    assert "ctx" in result.stdout or "Context" in result.stdout


def test_workspace_use_and_project_use(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", ".", "--yes", "--name", "Nav", "--id", "nav", "--no-git"])
    runner.invoke(app, ["workspace", "create", "eng"])
    runner.invoke(app, ["workspace", "use", "eng"])
    (tmp_path / "workspaces" / "eng" / "projects" / "memory-system").mkdir(parents=True)
    (tmp_path / "workspaces" / "eng" / "projects" / "memory-system" / ".company-project.yaml").write_text(
        "project:\n  name: memory-system\n", encoding="utf-8"
    )
    result = runner.invoke(app, ["project", "use", "memory-system"])
    assert result.exit_code == 0
    assert "memory-system" in result.stdout
