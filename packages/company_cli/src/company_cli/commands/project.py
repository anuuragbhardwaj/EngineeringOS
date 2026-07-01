"""project commands — Runtime integration."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from company_cli.context import get_api
from company_core.api.project import ProjectCreateRequest
from company_core.models.errors import ProjectNotFoundError

console = Console()
project_app = typer.Typer(help="Manage projects.")


def _slugify(name: str) -> str:
    import re

    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return slug or "project"


@project_app.command("create")
def project_create(
    name: str | None = typer.Option(None, "--name", help="Project name."),
    description: str | None = typer.Option(None, "--description", help="Project description."),
    platform: str | None = typer.Option(None, "--platform", help="Target platform."),
    production: bool | None = typer.Option(None, "--production/--prototype", help="Production mode."),
    technology_stack: str | None = typer.Option(None, "--stack", help="Preferred technology stack."),
    location: Path | None = typer.Option(None, "--location", help="Project directory."),
    non_interactive: bool = typer.Option(
        False,
        "--yes",
        help="Use defaults for missing options (non-interactive).",
    ),
) -> None:
    """Create a new project and run the planning pipeline (idea → architecture)."""
    api = get_api()

    if not name and non_interactive:
        name = "new-project"
    name = name or typer.prompt("Project name")
    description = description or (
        "EngineeringOS planning pipeline project" if non_interactive else typer.prompt("Description")
    )
    platform = platform or (
        "cross-platform" if non_interactive else typer.prompt("Target platform")
    )
    if production is None:
        production = (
            True
            if non_interactive
            else typer.confirm("Production project?", default=True)
        )
    technology_stack = technology_stack or (
        "Python" if non_interactive else typer.prompt("Preferred technology stack", default="Python")
    )
    default_location = Path.cwd() / "projects" / _slugify(name)
    if location is None and not non_interactive:
        location = Path(typer.prompt("Project location", default=str(default_location)))
    location = (location or default_location).resolve()

    request = ProjectCreateRequest(
        name=name,
        description=description,
        platform=platform,
        production=production,
        technology_stack=technology_stack,
        location=location,
    )

    console.print(f"[bold]Creating project[/bold] [cyan]{name}[/cyan] at {location}")
    project = api.project.create_from_request(request)
    view = api.project.status(project.project_id)

    console.print(f"[green]Project created:[/green] {project.project_id}")
    console.print(f"  Phase: {view.current_phase_id}")
    console.print(f"  Status: {view.status.value}")
    console.print("  Artifacts: idea.md through architecture.md")
    console.print("  Run [bold]engineeringos project status[/bold] for details")


@project_app.command("list")
def project_list() -> None:
    """List projects with runtime state."""
    api = get_api()
    projects = api.project.list()
    if not projects:
        console.print("No projects found.")
        return
    table = Table(title="Projects", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Status")
    for proj in projects:
        table.add_row(proj.project_id, proj.status)
    console.print(table)


@project_app.command("status")
def project_status(
    project_id: str | None = typer.Argument(None, help="Project ID."),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON."),
) -> None:
    """Show project pipeline status."""
    api = get_api()
    try:
        view = api.project.status(project_id)
    except ProjectNotFoundError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    if as_json:
        console.print(
            json.dumps(
                {
                    "project_id": view.project_id,
                    "status": view.status.value,
                    "current_phase_id": view.current_phase_id,
                    "current_gate_id": view.current_gate_id,
                    "blockers": view.blockers,
                    "metadata": view.metadata,
                },
                indent=2,
            )
        )
        return

    console.print(f"[bold]Project[/bold] {view.project_id}")
    console.print(f"  Status:  {view.status.value}")
    console.print(f"  Phase:   {view.current_phase_id}")
    console.print(f"  Gate:    {view.current_gate_id or '—'}")
    if view.blockers:
        console.print(f"  Blockers: {', '.join(view.blockers)}")


@project_app.command("resume")
def project_resume(project_id: str = typer.Argument(..., help="Project ID.")) -> None:
    """Resume an interrupted planning pipeline."""
    api = get_api()
    state = api.project.resume(project_id)
    console.print(
        f"[green]Resumed[/green] {project_id} at phase [cyan]{state.current_phase_id}[/cyan]"
    )


@project_app.command("history")
def project_history(
    project_id: str = typer.Argument(..., help="Project ID."),
    as_json: bool = typer.Option(False, "--json", help="Output as JSON."),
) -> None:
    """Show pipeline transition and gate history."""
    api = get_api()
    data = api.project.history(project_id)
    if as_json:
        console.print(json.dumps(data, indent=2))
        return

    console.print(f"[bold]History — {project_id}[/bold]")
    for entry in data.get("transitions", []):
        console.print(
            f"  {entry['timestamp']}: {entry['from']} -> {entry['to']} ({entry['trigger']})"
        )
    for gate in data.get("gates", []):
        status = "PASS" if gate["passed"] else "FAIL"
        console.print(
            f"  Gate {gate['gate_id']} ({gate['phase_id']}): {status} by {gate['evaluator']}"
        )


@project_app.command("validate")
def project_validate(project_id: str = typer.Argument(..., help="Project ID.")) -> None:
    """Validate current phase artifacts."""
    api = get_api()
    report = api.project.validate(project_id)
    table = Table(title=f"Validate — {project_id}", show_header=True)
    table.add_column("Check")
    table.add_column("Status")
    for result in report.results:
        status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
        checks = ", ".join(result.checks_run) or "validation"
        table.add_row(checks, status)
        for err in result.errors:
            table.add_row("", f"[red]{err.message}[/red]")
    console.print(table)
    if not report.passed:
        raise typer.Exit(code=1)


def register(app: typer.Typer) -> None:
    app.add_typer(project_app, name="project")
