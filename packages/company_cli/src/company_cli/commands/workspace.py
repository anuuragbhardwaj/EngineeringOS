"""workspace commands."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from company_cli.context import get_api
from company_core.models.errors import ManifestNotFoundError

console = Console()
workspace_app = typer.Typer(help="Manage workspaces.")


@workspace_app.command("create")
def workspace_create(workspace_id: str = typer.Argument(..., help="Workspace ID.")) -> None:
    """Create a new workspace under the company instance."""
    api = get_api()
    try:
        ws = api.workspace.create(workspace_id)
    except Exception as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]Workspace created:[/green] {ws.workspace_id} at {ws.root}")


@workspace_app.command("list")
def workspace_list() -> None:
    """List workspaces with project counts."""
    api = get_api()
    workspaces = api.workspace.list()
    if not workspaces:
        console.print("No workspaces found. Run [bold]engineeringos workspace create default[/bold]")
        return
    table = Table(title="Workspaces", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Projects")
    for ws in workspaces:
        table.add_row(ws.workspace_id, str(ws.project_count))
    console.print(table)


@workspace_app.command("use")
def workspace_use(workspace_id: str = typer.Argument(..., help="Workspace ID.")) -> None:
    """Set active workspace in session."""
    api = get_api()
    ctx = api.context.use_workspace(workspace_id)
    api.context.platform.record_command(f"workspace use {workspace_id}")
    console.print(f"[green]Active workspace:[/green] {ctx.session.workspace_id}")


@workspace_app.command("current")
def workspace_current() -> None:
    """Show active workspace."""
    api = get_api()
    ws = api.context.active_workspace_id()
    console.print(f"Active workspace: [cyan]{ws or '—'}[/cyan]")


@workspace_app.command("recent")
def workspace_recent() -> None:
    """List recently used workspaces."""
    api = get_api()
    recent = api.context.recent_workspaces()
    if not recent:
        console.print("No recent workspaces.")
        return
    for ws in recent:
        console.print(f"  {ws}")


@workspace_app.command("archive")
def workspace_archive(workspace_id: str = typer.Argument(..., help="Workspace ID.")) -> None:
    """Archive a workspace."""
    api = get_api()
    ws = api.workspace.archive(workspace_id)
    console.print(f"[yellow]Archived[/yellow] workspace {ws.workspace_id}")


@workspace_app.command("remove")
def workspace_remove(
    workspace_id: str = typer.Argument(..., help="Workspace ID."),
    yes: bool = typer.Option(False, "--yes", help="Confirm removal."),
) -> None:
    """Remove a workspace and all projects within it."""
    if not yes and not typer.confirm(f"Remove workspace '{workspace_id}' and all projects?"):
        raise typer.Exit()
    api = get_api()
    api.workspace.remove(workspace_id)
    console.print(f"[red]Removed[/red] workspace {workspace_id}")


@workspace_app.command("validate")
def workspace_validate(workspace_id: str = typer.Argument(..., help="Workspace ID.")) -> None:
    """Validate workspace layout."""
    api = get_api()
    try:
        report = api.workspace.validate(workspace_id)
    except ManifestNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc
    table = Table(title=f"Validate workspace — {workspace_id}", show_header=True)
    table.add_column("Check")
    table.add_column("Status")
    table.add_column("Message")
    for check in report.checks:
        status = "[green]PASS[/green]" if check.passed else "[red]FAIL[/red]"
        table.add_row(check.name, status, check.message)
    console.print(table)
    if not report.passed:
        raise typer.Exit(code=1)


def register(app: typer.Typer) -> None:
    app.add_typer(workspace_app, name="workspace")
