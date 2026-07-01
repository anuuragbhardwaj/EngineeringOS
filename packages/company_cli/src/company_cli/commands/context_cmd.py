"""Context and current commands."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from company_cli.context import get_api
from company_core.models.errors import ManifestNotFoundError

console = Console()


def register(app: typer.Typer) -> None:
    @app.command("current")
    def current_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Show active company, workspace, project, and execution context."""
        api = get_api()
        try:
            ctx = api.context.current()
        except ManifestNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        api.context.platform.record_command("current")

        if as_json:
            console.print(
                json.dumps(
                    {
                        "company_id": ctx.company_id,
                        "workspace_id": ctx.session.workspace_id,
                        "project_id": ctx.session.project_id,
                        "phase": ctx.session.current_phase,
                        "employee": ctx.session.current_employee,
                        "execution_status": ctx.session.execution_status,
                        "pipeline": ctx.session.pipeline,
                    },
                    indent=2,
                )
            )
            return

        console.print("[bold]Current Context[/bold]")
        console.print(f"  Company:   {ctx.company_id or '—'}")
        console.print(f"  Workspace: {ctx.session.workspace_id or '—'}")
        console.print(f"  Project:   {ctx.session.project_id or '—'}")
        console.print(f"  Phase:     {ctx.session.current_phase or '—'}")
        console.print(f"  Employee:  {ctx.session.current_employee or '—'}")
        console.print(f"  Status:    {ctx.session.execution_status}")

    @app.command("context")
    def context_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Display full execution context."""
        api = get_api()
        ctx = api.context.current()
        if as_json:
            console.print(json.dumps({"session": ctx.session.__dict__}, indent=2, default=str))
            return
        current_cmd(as_json=False)

    @app.command("reset-context")
    def reset_context_cmd() -> None:
        """Reset session to default workspace without deleting data."""
        api = get_api()
        ctx = api.context.reset()
        console.print(f"[yellow]Context reset[/yellow] — workspace: {ctx.session.workspace_id}")
