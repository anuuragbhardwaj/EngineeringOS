"""Knowledge CLI integration tests."""

from pathlib import Path

from typer.testing import CliRunner

from company_cli.main import app


def test_knowledge_status_command(tmp_path: Path, monkeypatch) -> None:
    (tmp_path / "company.yaml").write_text(
        "company:\n  instance_id: co\n  instance_version: '1.0.0'\n"
        "  schema_version: '1.0.0'\n  framework:\n    version: '2.0.0'\n"
        "  configuration:\n    workspaces_root: workspaces/\n    default_workspace: default\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    runner = CliRunner()
    result = runner.invoke(app, ["knowledge", "status", "--json"])
    assert result.exit_code == 0
    assert "total" in result.stdout
