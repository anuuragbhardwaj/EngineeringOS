"""Source control CLI commands."""

from __future__ import annotations

import json

import typer
from rich.console import Console
from rich.table import Table

from company_cli.context import get_api
from company_core.models.errors import ManifestNotFoundError
from source_control.errors import ApprovalRequiredError, RepositoryNotFoundError

console = Console()


def register(app: typer.Typer) -> None:
    repo_app = typer.Typer(help="Source control — repository management by Source Control Engineer.")
    app.add_typer(repo_app, name="repo")

    def _handle(exc: Exception) -> None:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from exc

    @repo_app.command("status")
    def status_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Show repository status for active context."""
        api = get_api()
        try:
            data = api.source_control.status()
        except (ManifestNotFoundError, RepositoryNotFoundError) as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(data, indent=2))
            return
        console.print(f"[bold]Repository[/bold] {data.get('repo_root', '—')}")
        console.print(f"  Branch: {data.get('branch', '—')}")
        console.print(f"  Clean: {data.get('clean')}")
        if data.get("conflicts"):
            console.print(f"  [red]Conflicts:[/red] {', '.join(data['conflicts'])}")

    @repo_app.command("validate")
    def validate_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Validate repository health."""
        api = get_api()
        try:
            data = api.source_control.validate()
        except (ManifestNotFoundError, RepositoryNotFoundError) as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(data, indent=2))
            return
        if data.get("valid"):
            console.print("[green]Repository valid[/green]")
        else:
            console.print("[red]Repository validation failed[/red]")
        for issue in data.get("issues", []):
            color = "red" if issue.get("severity") == "error" else "yellow"
            console.print(f"  [{color}]{issue.get('code')}[/{color}]: {issue.get('message')}")

    @repo_app.command("commit")
    def commit_cmd(
        message: str | None = typer.Option(None, "--message", "-m"),
        approve: bool = typer.Option(False, "--approve", help="Pre-approve commit (EM)."),
        no_approval: bool = typer.Option(False, "--no-approval", help="Skip approval check (tests)."),
    ) -> None:
        """Create commit (requires EM approval)."""
        api = get_api()
        try:
            if approve:
                api.source_control.approve("commit")
            result = api.source_control.commit(message=message, require_approval=not no_approval)
        except (ManifestNotFoundError, RepositoryNotFoundError, ApprovalRequiredError) as exc:
            _handle(exc)
        console.print(f"[green]Committed[/green] {result.sha[:8]} on {result.branch}")

    @repo_app.command("push")
    def push_cmd(
        approve: bool = typer.Option(False, "--approve"),
        no_approval: bool = typer.Option(False, "--no-approval"),
    ) -> None:
        """Push commits (requires EM approval)."""
        api = get_api()
        try:
            if approve:
                api.source_control.approve("push")
            result = api.source_control.push(require_approval=not no_approval)
        except (ManifestNotFoundError, RepositoryNotFoundError, ApprovalRequiredError) as exc:
            _handle(exc)
        console.print(f"[green]Pushed[/green] to {result.get('remote')} ({result.get('branch')})")

    @repo_app.command("history")
    def history_cmd(limit: int = typer.Option(20, "--limit"), as_json: bool = typer.Option(False, "--json")) -> None:
        """Show commit history."""
        api = get_api()
        try:
            data = api.source_control.log(limit=limit)
        except (ManifestNotFoundError, RepositoryNotFoundError) as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(data, indent=2))
            return
        table = Table(title="Commit History")
        table.add_column("SHA")
        table.add_column("Subject")
        table.add_column("Author")
        for entry in data:
            table.add_row(entry.get("sha", "")[:8], entry.get("subject", ""), entry.get("author", ""))
        console.print(table)

    @repo_app.command("branches")
    def branches_cmd() -> None:
        """List branches."""
        api = get_api()
        try:
            branches = api.source_control.branches()
        except (ManifestNotFoundError, RepositoryNotFoundError) as exc:
            _handle(exc)
        for branch in branches:
            console.print(f"  {branch}")

    @repo_app.command("checkout")
    def checkout_cmd(branch: str = typer.Argument(..., help="Branch name.")) -> None:
        """Checkout branch."""
        api = get_api()
        try:
            api.source_control.checkout(branch)
        except (ManifestNotFoundError, RepositoryNotFoundError) as exc:
            _handle(exc)
        console.print(f"[green]Checked out[/green] {branch}")

    @repo_app.command("tag")
    def tag_cmd(
        name: str = typer.Argument(..., help="Tag name."),
        message: str = typer.Option("", "--message", "-m"),
        approve: bool = typer.Option(False, "--approve"),
    ) -> None:
        """Create annotated tag (requires EM approval)."""
        api = get_api()
        try:
            if approve:
                api.source_control.approve("release")
            result = api.source_control.tag(name, message)
        except (ManifestNotFoundError, RepositoryNotFoundError, ApprovalRequiredError) as exc:
            _handle(exc)
        console.print(f"[green]Tagged[/green] {result.get('tag')}")

    @repo_app.command("release")
    def release_cmd(
        version: str | None = typer.Option(None, "--version"),
        as_json: bool = typer.Option(False, "--json"),
    ) -> None:
        """Prepare release plan (does not publish)."""
        api = get_api()
        try:
            plan = api.source_control.release(version=version)
        except (ManifestNotFoundError, RepositoryNotFoundError) as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(plan.to_dict(), indent=2))
            return
        console.print(f"[bold]Release Plan[/bold] {plan.tag_name}")
        console.print(plan.summary[:500])

    @repo_app.command("diff")
    def diff_cmd(staged: bool = typer.Option(False, "--staged")) -> None:
        """Show diff."""
        api = get_api()
        try:
            output = api.source_control.diff(staged=staged)
        except (ManifestNotFoundError, RepositoryNotFoundError) as exc:
            _handle(exc)
        console.print(output or "(no changes)")

    @repo_app.command("stage")
    def stage_cmd(paths: list[str] = typer.Argument(None)) -> None:
        """Stage files."""
        api = get_api()
        try:
            staged = api.source_control.stage(paths or None)
        except (ManifestNotFoundError, RepositoryNotFoundError) as exc:
            _handle(exc)
        console.print(f"[green]Staged[/green] {len(staged)} file(s)")

    @repo_app.command("unstage")
    def unstage_cmd(paths: list[str] = typer.Argument(None)) -> None:
        """Unstage files."""
        api = get_api()
        try:
            api.source_control.unstage(paths or None)
        except (ManifestNotFoundError, RepositoryNotFoundError) as exc:
            _handle(exc)
        console.print("[yellow]Unstaged[/yellow]")

    @repo_app.command("log")
    def log_cmd(limit: int = typer.Option(10, "--limit")) -> None:
        """Show recent commits."""
        api = get_api()
        try:
            entries = api.source_control.log(limit=limit)
        except (ManifestNotFoundError, RepositoryNotFoundError) as exc:
            _handle(exc)
        for entry in entries:
            console.print(f"{entry.get('sha', '')[:8]} {entry.get('subject', '')}")

    @repo_app.command("doctor")
    def doctor_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Repository health diagnostics."""
        api = get_api()
        try:
            data = api.source_control.doctor()
        except (ManifestNotFoundError, RepositoryNotFoundError) as exc:
            _handle(exc)
        if as_json:
            console.print(json.dumps(data, indent=2, default=str))
            return
        console.print("[bold]Repository Doctor[/bold]")
        console.print(f"  Valid: {data.get('validation', {}).get('valid')}")
        console.print(f"  Clean: {data.get('status', {}).get('clean')}")

    @repo_app.command("approve")
    def approve_cmd(
        action: str = typer.Argument(..., help="commit, push, or release."),
        reason: str = typer.Option("", "--reason"),
    ) -> None:
        """Engineering Manager approves source control action."""
        api = get_api()
        try:
            record = api.source_control.approve(action, reason=reason)
        except ManifestNotFoundError as exc:
            _handle(exc)
        console.print(f"[green]Approved[/green] {action} for {record.get('project_id')}")
