"""status command."""

from __future__ import annotations

import json

import typer
from rich.console import Console

from company_cli.context import get_api

console = Console()


def register(app: typer.Typer) -> None:
    @app.command("status")
    def status_cmd(
        as_json: bool = typer.Option(False, "--json", help="Output as JSON."),
    ) -> None:
        """Show company, workspace, and project summary."""
        api = get_api()
        status = api.company.status()

        if as_json:
            console.print(
                json.dumps(
                    {
                        "instance_id": status.instance_id,
                        "workspace_id": status.workspace_id,
                        "project_id": status.project_id,
                        "phase": status.phase,
                        "message": status.message,
                    },
                    indent=2,
                )
            )
            return

        console.print("[bold]EngineeringOS Status[/bold]")
        console.print(f"  Instance:  {status.instance_id or '—'}")
        console.print(f"  Workspace: {status.workspace_id or '—'}")
        console.print(f"  Project:   {status.project_id or '—'}")
        console.print(f"  Phase:     {status.phase or '—'}")
        console.print(f"  {status.message}")
