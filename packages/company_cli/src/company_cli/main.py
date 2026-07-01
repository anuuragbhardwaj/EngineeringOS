"""EngineeringOS CLI entry point."""

from __future__ import annotations

import typer
from rich.console import Console

from company_cli.registry import register_commands
from company_cli.version import CLI_VERSION

console = Console()

app = typer.Typer(
    name="engineeringos",
    help="EngineeringOS — primary interface for the AI Company Framework.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=False,
    invoke_without_command=True,
)


def _register() -> None:
    register_commands(app)


_register()


@app.callback()
def main(
    version_flag: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version and exit.",
        is_eager=True,
    ),
) -> None:
    """EngineeringOS command-line interface."""
    if version_flag:
        from company_cli.commands.version import print_version

        print_version()
        raise typer.Exit()


def run() -> None:
    """Console script entry point."""
    app()


if __name__ == "__main__":
    run()
