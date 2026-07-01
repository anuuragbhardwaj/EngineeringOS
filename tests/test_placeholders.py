"""Placeholder command tests."""

from typer.testing import CliRunner

from company_cli.main import app

runner = CliRunner()


PLACEHOLDER_COMMANDS = [
    ["config"],
    ["employees"],
]


def test_placeholder_commands_exit_zero() -> None:
    for args in PLACEHOLDER_COMMANDS:
        result = runner.invoke(app, args)
        assert result.exit_code == 0, f"Failed for: {args}"
        assert "Not Yet Implemented" in result.stdout


def test_open_accepts_workspace_option() -> None:
    result = runner.invoke(app, ["open", "--workspace", "default"])
    assert result.exit_code == 0
    assert "Opened" in result.stdout
