"""init command — interactive and non-interactive company generation."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from company_cli.context import get_api
from company_lifecycle.types import CompanyCreateRequest

console = Console()


def register(app: typer.Typer) -> None:
    @app.command("init")
    def init_cmd(
        path: Path = typer.Argument(Path("."), help="Target directory for the company."),
        instance_id: str | None = typer.Option(None, "--id", help="Company instance ID."),
        name: str | None = typer.Option(None, "--name", help="Company display name."),
        editor: str = typer.Option("cursor", "--editor", help="Default editor."),
        ai_provider: str = typer.Option("cursor", "--ai-provider", help="Preferred AI provider."),
        mcp_profile: str = typer.Option("default", "--mcp-profile", help="MCP profile name."),
        language: str = typer.Option("en", "--language", help="Default language."),
        template_profile: str = typer.Option("production", "--template", help="Template profile."),
        git: bool = typer.Option(False, "--git/--no-git", help="Initialize git repository."),
        github: bool = typer.Option(False, "--github/--no-github", help="Scaffold .github workflows."),
        yes: bool = typer.Option(False, "--yes", help="Non-interactive mode with defaults."),
    ) -> None:
        """Initialize a generated company that references the installed framework."""
        api = get_api()
        target = path.resolve()
        company_name = name or (instance_id if yes else typer.prompt("Company name", default=instance_id or "my-company"))
        iid = instance_id or company_name.lower().replace(" ", "-")

        if not yes:
            editor = typer.prompt("Default editor", default=editor)
            ai_provider = typer.prompt("Preferred AI provider", default=ai_provider)
            git = typer.confirm("Initialize git?", default=git)
            github = typer.confirm("Scaffold GitHub workflows?", default=github)

        request = CompanyCreateRequest(
            name=company_name,
            target=target,
            instance_id=iid,
            default_editor=editor,
            preferred_ai_provider=ai_provider,
            preferred_mcp_profile=mcp_profile,
            default_language=language,
            init_git=git,
            init_github=github,
            template_profile=template_profile,
        )
        try:
            instance = api.company.create(request)
        except FileExistsError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        except Exception as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc

        console.print(f"[green]Company created[/green] [cyan]{instance.instance_id}[/cyan] at {instance.root}")
        console.print("  User-owned assets only — framework is referenced, not copied.")
        console.print("  Next: [bold]engineeringos open[/bold] then [bold]engineeringos project create[/bold]")
