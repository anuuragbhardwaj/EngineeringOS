"""CLI startup tests."""

from typer.testing import CliRunner

from company_cli.main import app

runner = CliRunner()


def test_cli_invokes_without_error() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "EngineeringOS" in result.stdout


def test_cli_no_args_shows_help() -> None:
    result = runner.invoke(app, [])
    assert result.exit_code in (0, 2)
    assert "Usage" in result.stdout
