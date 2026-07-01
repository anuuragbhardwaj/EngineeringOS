"""version command."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from company_cli.context import get_api

console = Console()


def print_version() -> None:
    api = get_api()
    info = api.company.version()
    table = Table(title="EngineeringOS Version", show_header=True)
    table.add_column("Component", style="cyan")
    table.add_column("Version", style="green")
    table.add_row("CLI", info.cli_version)
    table.add_row("Framework", info.framework_version)
    table.add_row("Framework API", info.framework_api_version)
    if info.manifest_version:
        table.add_row("Manifest", info.manifest_version)
    if info.instance_id:
        table.add_row("Instance", info.instance_id)
    console.print(table)


def register(app: typer.Typer) -> None:
    @app.command("version")
    def version_cmd() -> None:
        """Show framework, API, manifest, and CLI versions."""
        print_version()
