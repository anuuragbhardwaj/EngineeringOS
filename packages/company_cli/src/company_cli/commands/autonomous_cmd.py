"""Autonomous company CLI commands."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from company_cli.context import get_api
from company_core.models.errors import ManifestNotFoundError

console = Console()


def register(app: typer.Typer) -> None:
    def _handle(exc: Exception) -> None:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    @app.command("work")
    def work_cmd(
        goal: str = typer.Argument(..., help="High-level engineering goal."),
        project_id: str | None = typer.Option(None, "--project", "-p"),
        as_json: bool = typer.Option(False, "--json"),
    ) -> None:
        """Start autonomous execution from a CEO goal."""
        api = get_api()
        try:
            result = api.autonomous.work(goal, project_id=project_id)
        except ManifestNotFoundError as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(result, indent=2, default=str))
            return
        console.print(f"[green]Working[/green] on: {goal}")
        if result.get("goal"):
            console.print(f"  Goal ID: {result['goal'].get('goal_id')}")

    @app.command("stop")
    def stop_cmd() -> None:
        """Stop autonomous execution."""
        api = get_api()
        try:
            result = api.autonomous.stop()
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print(f"[red]Stopped[/red] — {result.get('status')}")

    @app.command("goals")
    def goals_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """List engineering goals."""
        api = get_api()
        try:
            goals = api.autonomous.goals()
        except ManifestNotFoundError as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps([g.to_dict() for g in goals], indent=2))
            return
        for goal in goals:
            console.print(f"  {goal.goal_id}: {goal.title} [{goal.status}]")

    @app.command("blockers")
    def blockers_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Show active blockers."""
        api = get_api()
        try:
            blockers = api.autonomous.blockers()
        except ManifestNotFoundError as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(blockers, indent=2))
            return
        for b in blockers:
            console.print(f"  [{b.get('blocker_type')}] {b.get('message')}")

    @app.command("supervise")
    def supervise_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Run one supervision cycle."""
        api = get_api()
        try:
            result = api.autonomous.supervise()
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print(json.dumps(result, indent=2, default=str) if as_json else f"Decision: {result.get('decision', {}).get('action')}")

    @app.command("monitor")
    def monitor_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Show execution monitor snapshot."""
        api = get_api()
        try:
            data = api.autonomous.monitor()
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print(json.dumps(data, indent=2, default=str) if as_json else str(data))

    @app.command("heartbeat")
    def heartbeat_cmd() -> None:
        """Send runner heartbeat."""
        api = get_api()
        try:
            data = api.autonomous.heartbeat()
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print(f"[green]Alive[/green] — {data.get('heartbeat')}")

    @app.command("recover")
    def recover_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Recover session and context after interruption."""
        api = get_api()
        try:
            data = api.autonomous.recover()
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print(json.dumps(data, indent=2) if as_json else f"[green]Recovered[/green] project {data.get('project_id')}")

    @app.command("explain")
    def explain_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Explain current autonomous state and latest decision."""
        api = get_api()
        try:
            data = api.autonomous.explain()
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print(json.dumps(data, indent=2, default=str) if as_json else str(data))

    @app.command("decisions")
    def decisions_cmd(
        limit: int = typer.Option(20, "--limit"),
        as_json: bool = typer.Option(False, "--json"),
    ) -> None:
        """Show recorded autonomous decisions."""
        api = get_api()
        try:
            decisions = api.autonomous.decisions(limit=limit)
        except ManifestNotFoundError as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(decisions, indent=2))
            return
        table = Table(title="Decisions")
        table.add_column("Time")
        table.add_column("Action")
        table.add_column("Reason")
        for d in decisions:
            table.add_row(d.get("timestamp", ""), d.get("action", ""), d.get("reason", "")[:60])
        console.print(table)

    # Approvals subcommand group
    approvals_app = typer.Typer(help="Engineering Manager approvals.")
    app.add_typer(approvals_app, name="approvals")

    @approvals_app.command("list")
    def approvals_list(as_json: bool = typer.Option(False, "--json")) -> None:
        api = get_api()
        try:
            pending = api.autonomous.approvals_pending()
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print(json.dumps(pending, indent=2) if as_json else str(pending))

    @approvals_app.command("approve")
    def approvals_approve(
        gate: str = typer.Argument(..., help="Gate: architecture, implementation, review, commit, push, release."),
        reason: str = typer.Option("", "--reason"),
    ) -> None:
        api = get_api()
        try:
            result = api.autonomous.approve(gate, reason=reason)
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print(f"[green]Approved[/green] {gate} for {result.get('project_id')}")

    # Autonomy status subcommand group
    autonomy_app = typer.Typer(help="Autonomous company status.")
    app.add_typer(autonomy_app, name="autonomy")

    @autonomy_app.command("status")
    def autonomy_status_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Show autonomous company status."""
        api = get_api()
        try:
            status = api.autonomous.status()
        except ManifestNotFoundError as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(status.to_dict(), indent=2, default=str))
            return
        console.print(f"[bold]Autonomous Company[/bold]")
        console.print(f"  Runner: {status.runner.status}")
        console.print(f"  Project: {status.runner.project_id or '—'}")
        console.print(f"  Goal: {status.active_goal.title if status.active_goal else '—'}")
        console.print(f"  Blockers: {len(status.blockers)}")
        console.print(f"  Pending approvals: {len(status.pending_approvals)}")
