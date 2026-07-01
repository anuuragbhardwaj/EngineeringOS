"""init command."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from company_cli.context import get_api

console = Console()


def register(app: typer.Typer) -> None:
    @app.command("init")
    def init_cmd(
        path: Path = typer.Argument(
            Path("."),
            help="Target directory for the company instance.",
        ),
        instance_id: str = typer.Option(
            "default",
            "--id",
            help="Company instance identifier.",
        ),
    ) -> None:
        """Initialize a company instance in the target directory."""
        api = get_api()
        try:
            instance = api.company.init(path, template=instance_id)
        except FileExistsError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc

        console.print(
            f"[green]Initialized[/green] company instance "
            f"[cyan]{instance.instance_id}[/cyan] at {instance.root}"
        )
        console.print(f"  Manifest: {instance.manifest_path}")
        console.print("  Next: run [bold]engineeringos doctor[/bold]")
