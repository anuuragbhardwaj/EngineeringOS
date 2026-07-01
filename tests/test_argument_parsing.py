"""Argument parsing tests."""

from pathlib import Path

from typer.testing import CliRunner

from company_cli.main import app

runner = CliRunner()


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.stdout
    assert "2.0.0" in result.stdout


def test_version_flag() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "CLI" in result.stdout


def test_init_parses_path_and_id(tmp_path: Path) -> None:
    target = tmp_path / "new-company"
    result = runner.invoke(
        app,
        ["init", str(target), "--id", "acme", "--yes", "--name", "Acme"],
    )
    assert result.exit_code == 0
    assert (target / "company.yaml").is_file()
    assert "acme" in result.stdout


def test_status_json_flag() -> None:
    result = runner.invoke(app, ["status", "--json"])
    assert result.exit_code == 0
    assert "company_id" in result.stdout


def test_workspace_create_parses_id(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", ".", "--yes", "--name", "WS", "--id", "ws", "--no-git"])
    result = runner.invoke(app, ["workspace", "create", "team-b"])
    assert result.exit_code == 0
    assert "team-b" in result.stdout


def test_project_list_command() -> None:
    result = runner.invoke(app, ["project", "list"])
    assert result.exit_code == 0
