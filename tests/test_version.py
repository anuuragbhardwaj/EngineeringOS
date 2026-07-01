"""Version output tests."""

from typer.testing import CliRunner

from company_cli.main import app
from company_core import FrameworkAPI

runner = CliRunner()


def test_version_command_output() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    for label in ("CLI", "Framework", "Framework API"):
        assert label in result.stdout


def test_framework_api_version_info() -> None:
    api = FrameworkAPI(cli_version="0.1.0")
    info = api.company.version()
    assert info.cli_version == "0.1.0"
    assert info.framework_version == "2.0.0"
    assert info.framework_api_version == "2.0.0"
