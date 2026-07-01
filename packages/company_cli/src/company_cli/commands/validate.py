"""validate command."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from company_cli.context import get_api

console = Console()


def register(app: typer.Typer) -> None:
    @app.command("validate")
    def validate_cmd() -> None:
        """Run full validation suite (manifest + MCP)."""
        api = get_api()
        report = api.validate_all()

        table = Table(title="EngineeringOS Validate", show_header=True)
        table.add_column("Check", style="cyan")
        table.add_column("Status")
        table.add_column("Message")

        for check in report.checks:
            status = "[green]PASS[/green]" if check.passed else "[red]FAIL[/red]"
            table.add_row(check.name, status, check.message)

        console.print(table)
        if not report.passed:
            raise typer.Exit(code=1)
