"""Autonomous CLI integration tests."""

from pathlib import Path

from typer.testing import CliRunner

from company_cli.main import app


def test_autonomy_status_command(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "company.yaml").write_text(
        "company:\n  instance_id: co\n  instance_version: '1.0.0'\n"
        "  schema_version: '1.0.0'\n  framework:\n    version: '2.0.0'\n"
        "  configuration:\n    workspaces_root: workspaces/\n    default_workspace: default\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["autonomy", "status", "--json"])
    assert result.exit_code == 0
    assert "runner" in result.stdout


def test_work_command(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "company.yaml").write_text(
        "company:\n  instance_id: co\n  instance_version: '1.0.0'\n"
        "  schema_version: '1.0.0'\n  framework:\n    version: '2.0.0'\n"
        "  configuration:\n    workspaces_root: workspaces/\n    default_workspace: default\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["work", "Implement feature X", "--json"])
    assert result.exit_code == 0
