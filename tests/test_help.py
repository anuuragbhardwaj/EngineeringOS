"""Help output tests."""

from typer.testing import CliRunner

from company_cli.main import app

runner = CliRunner()


def test_root_help_lists_commands() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ("init", "doctor", "validate", "version", "workspace", "mcp"):
        assert command in result.stdout


def test_workspace_help() -> None:
    result = runner.invoke(app, ["workspace", "--help"])
    assert result.exit_code == 0
    assert "create" in result.stdout
    assert "list" in result.stdout


def test_mcp_help() -> None:
    result = runner.invoke(app, ["mcp", "--help"])
    assert result.exit_code == 0
    assert "list" in result.stdout
    assert "validate" in result.stdout
