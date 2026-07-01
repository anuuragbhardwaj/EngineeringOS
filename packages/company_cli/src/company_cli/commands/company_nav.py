"""Company navigation commands."""

from __future__ import annotations

import typer
from rich.console import Console

from company_cli.context import get_api

console = Console()
company_app = typer.Typer(help="Company context navigation.")


@company_app.command("current")
def company_current() -> None:
    """Show active company."""
    api = get_api()
    ctx = api.context.current()
    console.print(f"Active company: [cyan]{ctx.company_id or '—'}[/cyan]")
    if ctx.instance_root:
        console.print(f"  Root: {ctx.instance_root}")


def register(app: typer.Typer) -> None:
    app.add_typer(company_app, name="company")
