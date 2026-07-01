"""open command."""

from __future__ import annotations

import typer
from rich.console import Console

from company_cli.context import get_api
from company_core.models.errors import ManifestNotFoundError

console = Console()


def register(app: typer.Typer) -> None:
    @app.command("open")
    def open_cmd(
        workspace: str | None = typer.Option(None, "--workspace", "-w", help="Workspace ID."),
        instance_id: str | None = typer.Option(None, "--id", help="Company instance ID."),
    ) -> None:
        """Set active company and workspace context."""
        api = get_api()
        try:
            instance = api.company.open(instance_id=instance_id, workspace_id=workspace)
        except ManifestNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc

        status = api.company.status()
        console.print(f"[green]Opened[/green] company [cyan]{instance.instance_id}[/cyan]")
        if status.workspace_id:
            console.print(f"  Active workspace: {status.workspace_id}")
