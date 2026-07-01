"""CLI lifecycle integration tests."""

from pathlib import Path

from typer.testing import CliRunner

from company_cli.main import app


runner = CliRunner()


def test_init_and_open(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        app,
        [
            "init",
            str(tmp_path / "my-co"),
            "--yes",
            "--name",
            "My Co",
            "--id",
            "my-co",
            "--no-git",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / "my-co" / "company.yaml").is_file()

    monkeypatch.chdir(tmp_path / "my-co")
    result = runner.invoke(app, ["open"])
    assert result.exit_code == 0, result.stdout


def test_workspace_create_list(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["init", ".", "--yes", "--name", "WS Co", "--id", "ws-co", "--no-git"])
    result = runner.invoke(app, ["workspace", "create", "team-a"])
    assert result.exit_code == 0, result.stdout
    result = runner.invoke(app, ["workspace", "list"])
    assert "team-a" in result.stdout
