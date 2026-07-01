"""Command discovery tests."""

from company_cli.main import app
from company_cli.registry import COMMAND_MODULES, discover_command_names


def test_all_command_modules_register() -> None:
    assert len(COMMAND_MODULES) >= 11


def test_top_level_commands_discovered() -> None:
    names = discover_command_names(app)
    expected = {
        "config",
        "doctor",
        "employees",
        "init",
        "mcp",
        "open",
        "project",
        "status",
        "validate",
        "version",
        "workspace",
    }
    assert expected.issubset(set(names))
