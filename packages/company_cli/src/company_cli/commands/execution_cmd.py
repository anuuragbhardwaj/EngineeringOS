"""Top-level execution commands."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from company_cli.context import get_api
from company_core.models.errors import ManifestNotFoundError, ProjectNotFoundError

console = Console()


def register(app: typer.Typer) -> None:
    @app.command("continue")
    def continue_cmd(autonomous: bool = typer.Option(True, "--autonomous/--manual", help="Use autonomous runner.")) -> None:
        """Continue execution from active context."""
        api = get_api()
        try:
            if autonomous:
                result = api.autonomous.continue_execution()
            else:
                result = api.context.continue_execution()
        except (ManifestNotFoundError, Exception) as exc:
            from company_core.models.errors import ProjectNotFoundError
            from workspace_execution.errors import NoActiveProjectError

            if isinstance(exc, (ManifestNotFoundError, ProjectNotFoundError, NoActiveProjectError)):
                console.print(f"[red]Error:[/red] {exc}")
                raise typer.Exit(code=1) from exc
            if autonomous:
                result = api.context.continue_execution()
            else:
                raise
        api.context.platform.record_command("continue")
        console.print(f"[green]Continue[/green] — {result.get('status', 'ok')}")
        if result.get("phase_id"):
            console.print(f"  Phase: {result['phase_id']}")
        elif result.get("results"):
            console.print(f"  Cycles: {result.get('cycles')}")

    @app.command("pause")
    def pause_cmd(
        project_id: str | None = typer.Argument(None, help="Project ID (defaults to active)."),
    ) -> None:
        """Pause active pipeline execution."""
        api = get_api()
        try:
            result = api.context.pause(project_id)
        except (ManifestNotFoundError, ProjectNotFoundError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        api.context.platform.record_command("pause")
        console.print(f"[yellow]Paused[/yellow] project {result.get('project_id')}")

    @app.command("resume")
    def resume_cmd(
        project_id: str | None = typer.Argument(None, help="Project ID (defaults to active)."),
    ) -> None:
        """Resume paused or interrupted execution."""
        api = get_api()
        try:
            result = api.context.resume(project_id)
        except (ManifestNotFoundError, ProjectNotFoundError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        api.context.platform.record_command("resume")
        console.print(f"[green]Resumed[/green] project {result.get('project_id')} at {result.get('phase_id', '—')}")

    @app.command("history")
    def history_cmd(
        project_id: str | None = typer.Argument(None, help="Project ID (defaults to active)."),
        event_type: str | None = typer.Option(None, "--event", help="Filter by event type."),
        as_json: bool = typer.Option(False, "--json"),
    ) -> None:
        """Show execution history for active context."""
        api = get_api()
        try:
            if project_id:
                data = api.project.history(project_id)
            else:
                pid = api.context.active_project_id()
                data = api.project.history(pid) if pid else {"execution_context": api.context.history(event_type=event_type)}
        except (ManifestNotFoundError, ProjectNotFoundError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc

        if as_json:
            console.print(json.dumps(data, indent=2, default=str))
            return

        entries = data.get("execution_context") or api.context.history(event_type=event_type)
        table = Table(title="Execution History", show_header=True)
        table.add_column("Time")
        table.add_column("Event")
        table.add_column("Project")
        table.add_column("Detail")
        for entry in entries:
            table.add_row(
                str(entry.get("timestamp", "")),
                str(entry.get("event_type", "")),
                str(entry.get("project_id", "")),
                str(entry.get("detail") or entry.get("command") or ""),
            )
        console.print(table)
