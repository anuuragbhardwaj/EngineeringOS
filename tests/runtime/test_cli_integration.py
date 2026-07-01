"""CLI project command integration tests."""

from pathlib import Path

from typer.testing import CliRunner

from company_cli.main import app

runner = CliRunner()
REPO_ROOT = Path(__file__).resolve().parents[2]


def test_project_create_non_interactive(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(REPO_ROOT)
    target = tmp_path / "projects" / "cli-demo"
    result = runner.invoke(
        app,
        [
            "project",
            "create",
            "--name",
            "CLI Demo",
            "--description",
            "CLI integration test",
            "--platform",
            "web",
            "--production",
            "--stack",
            "Python",
            "--location",
            str(target),
            "--yes",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert (target / "architecture.md").is_file()
    assert "architecture" in result.stdout.lower() or "cli-demo" in result.stdout


def test_project_status_after_create(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(REPO_ROOT)
    target = tmp_path / "projects" / "status-demo"
    runner.invoke(
        app,
        [
            "project",
            "create",
            "--name",
            "Status Demo",
            "--location",
            str(target),
            "--yes",
        ],
    )
    result = runner.invoke(app, ["project", "status", "status-demo", "--json"])
    assert result.exit_code == 0
    assert "status-demo" in result.stdout
