"""Dynamic command registration for EngineeringOS CLI."""

from __future__ import annotations

import importlib
from collections.abc import Callable

import typer

COMMAND_MODULES = (
    "company_cli.commands.version",
    "company_cli.commands.doctor",
    "company_cli.commands.validate",
    "company_cli.commands.init",
    "company_cli.commands.open",
    "company_cli.commands.status",
    "company_cli.commands.config",
    "company_cli.commands.workspace",
    "company_cli.commands.project",
    "company_cli.commands.employees",
    "company_cli.commands.lifecycle",
    "company_cli.commands.context_cmd",
    "company_cli.commands.execution_cmd",
    "company_cli.commands.company_nav",
    "company_cli.commands.knowledge_cmd",
    "company_cli.commands.autonomous_cmd",
    "company_cli.commands.repo_cmd",
    "company_cli.commands.parallel_cmd",
    "company_cli.commands.mcp",
)


def register_commands(app: typer.Typer) -> None:
    """Load and attach command modules to the root Typer app."""
    for module_path in COMMAND_MODULES:
        module = importlib.import_module(module_path)
        register: Callable[[typer.Typer], None] | None = getattr(
            module, "register", None
        )
        if register is not None:
            register(app)


def discover_command_names(app: typer.Typer) -> list[str]:
    """Return registered top-level command names for tests."""
    names: list[str] = []
    for command in app.registered_commands:
        if command.name:
            names.append(command.name)
    for group in app.registered_groups:
        if group.name:
            names.append(group.name)
    return sorted(names)
