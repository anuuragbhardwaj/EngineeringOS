"""Parallel execution CLI commands."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from company_cli.context import get_api
from company_core.models.errors import ManifestNotFoundError

console = Console()


def register(app: typer.Typer) -> None:
    parallel_app = typer.Typer(help="Parallel execution — concurrent employee scheduling.")
    app.add_typer(parallel_app, name="parallel")

    def _handle(exc: Exception) -> None:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    @parallel_app.command("status")
    def status_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Show parallel execution status."""
        api = get_api()
        try:
            data = api.parallel_execution.status()
        except ManifestNotFoundError as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(data, indent=2))
            return
        console.print(f"[bold]Parallel Execution[/bold]")
        console.print(f"  Workers: {data.get('total_workers', 0)} active: {data.get('active_workers', 0)}")

    @parallel_app.command("graph")
    def graph_cmd(
        phase_id: str = typer.Argument("implementation", help="Phase ID."),
        as_json: bool = typer.Option(False, "--json"),
    ) -> None:
        """Show dependency graph for a phase."""
        api = get_api()
        try:
            data = api.parallel_execution.graph(phase_id)
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print(json.dumps(data, indent=2) if as_json else str(data))

    @parallel_app.command("workers")
    def workers_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """List active workers."""
        api = get_api()
        try:
            workers = api.parallel_execution.workers()
        except ManifestNotFoundError as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(workers, indent=2))
            return
        table = Table(title="Workers")
        table.add_column("ID")
        table.add_column("Employee")
        table.add_column("Deliverable")
        table.add_column("Status")
        for w in workers:
            table.add_row(w.get("worker_id", ""), w.get("employee_id", ""), w.get("deliverable", ""), w.get("status", ""))
        console.print(table)

    @parallel_app.command("execute")
    def execute_cmd(
        project_id: str = typer.Argument(..., help="Project ID."),
        phase_id: str = typer.Argument("implementation", help="Phase ID."),
        as_json: bool = typer.Option(False, "--json"),
    ) -> None:
        """Build and display execution plan (dry-run without adapter)."""
        api = get_api()
        try:
            plan = api.parallel_execution.plan(project_id, phase_id)
            explanation = api.parallel_execution.explain(plan)
        except ManifestNotFoundError as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(explanation, indent=2, default=str))
            return
        console.print(f"[bold]Plan[/bold] {plan.plan_id} — {len(plan.workers)} workers in {len(plan.groups)} groups")

    @parallel_app.command("pause")
    def pause_cmd() -> None:
        """Pause parallel execution."""
        api = get_api()
        try:
            api.parallel_execution.pause()
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print("[yellow]Paused[/yellow]")

    @parallel_app.command("resume")
    def resume_cmd() -> None:
        """Resume parallel execution."""
        api = get_api()
        try:
            api.parallel_execution.resume()
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print("[green]Resumed[/green]")

    @parallel_app.command("cancel")
    def cancel_cmd() -> None:
        """Cancel parallel execution."""
        api = get_api()
        try:
            api.parallel_execution.cancel()
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print("[red]Cancelled[/red]")

    @parallel_app.command("explain")
    def explain_cmd(
        project_id: str = typer.Argument(..., help="Project ID."),
        phase_id: str = typer.Argument("implementation", help="Phase ID."),
        as_json: bool = typer.Option(False, "--json"),
    ) -> None:
        """Explain execution plan and dependency graph."""
        api = get_api()
        try:
            plan = api.parallel_execution.plan(project_id, phase_id)
            data = api.parallel_execution.explain(plan)
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print(json.dumps(data, indent=2, default=str) if as_json else str(data))

    @parallel_app.command("stats")
    def stats_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Show execution statistics."""
        api = get_api()
        try:
            stats = api.parallel_execution.stats()
        except ManifestNotFoundError as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(stats.to_dict(), indent=2))
            return
        console.print(f"Workers: {stats.total_workers} | Groups: {stats.parallel_groups}")
