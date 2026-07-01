"""Command discovery tests."""

from company_cli.main import app
from company_cli.registry import COMMAND_MODULES, discover_command_names


def test_all_command_modules_register() -> None:
    assert len(COMMAND_MODULES) >= 16


def test_top_level_commands_discovered() -> None:
    names = discover_command_names(app)
    expected = {
        "approvals",
        "autonomy",
        "blockers",
        "company",
        "config",
        "continue",
        "context",
        "current",
        "decisions",
        "doctor",
        "employees",
        "explain",
        "goals",
        "heartbeat",
        "history",
        "init",
        "knowledge",
        "migrate",
        "monitor",
        "mcp",
        "open",
        "parallel",
        "pause",
        "project",
        "recover",
        "repo",
        "repair",
        "reset-context",
        "resume",
        "status",
        "stop",
        "supervise",
        "work",
        "uninstall",
        "upgrade",
        "validate",
        "version",
        "workspace",
    }
    assert expected.issubset(set(names))
