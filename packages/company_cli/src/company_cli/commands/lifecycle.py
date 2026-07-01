"""Lifecycle commands — repair, upgrade, migrate, uninstall."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from company_cli.context import get_api
from company_core.models.errors import ManifestNotFoundError

console = Console()


def register(app: typer.Typer) -> None:
    @app.command("repair")
    def repair_cmd(
        apply: bool = typer.Option(True, "--apply/--dry-run", help="Apply repairs."),
    ) -> None:
        """Repair common company lifecycle issues."""
        api = get_api()
        try:
            report = api.company.repair(apply=apply)
        except ManifestNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        table = Table(title="Repair", show_header=True)
        table.add_column("Check")
        table.add_column("Action")
        table.add_column("Applied")
        table.add_column("Message")
        for action in report.actions:
            applied = "[green]yes[/green]" if action.applied else "no"
            table.add_row(action.check, action.action, applied, action.message)
        console.print(table)
        console.print(f"Applied {report.applied_count} repair action(s)")

    @app.command("upgrade")
    def upgrade_cmd(
        version: str | None = typer.Option(None, "--version", help="Target framework version."),
        plan_only: bool = typer.Option(False, "--plan", help="Show plan only."),
    ) -> None:
        """Upgrade company framework version pin."""
        api = get_api()
        try:
            plan = api.company.plan_upgrade(version) if plan_only else api.company.upgrade(version)
        except ManifestNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        console.print(f"[bold]Upgrade plan[/bold] {plan.framework_from} -> {plan.framework_to}")
        for action in plan.actions:
            console.print(f"  - {action}")
        for warning in plan.warnings:
            console.print(f"[yellow]Warning:[/yellow] {warning}")

    @app.command("migrate")
    def migrate_cmd(
        dry_run: bool = typer.Option(True, "--dry-run/--apply", help="Dry run by default."),
    ) -> None:
        """Plan or apply company schema migration."""
        api = get_api()
        try:
            plan = api.company.migrate(dry_run=dry_run)
        except ManifestNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        console.print(f"[bold]Migration[/bold] {plan.from_version} -> {plan.to_version}")
        for step in plan.steps:
            console.print(f"  - {step}")

    @app.command("uninstall")
    def uninstall_cmd(
        path: Path = typer.Argument(..., help="Company directory to remove."),
        yes: bool = typer.Option(False, "--yes", help="Confirm uninstall."),
    ) -> None:
        """Remove a generated company (never removes installed framework)."""
        if not yes and not typer.confirm(f"Remove company at {path}?"):
            raise typer.Exit()
        api = get_api()
        try:
            api.company.uninstall(path.resolve())
        except ValueError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        console.print(f"[red]Removed[/red] company at {path}")
