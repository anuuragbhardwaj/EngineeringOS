"""mcp commands."""

from __future__ import annotations

import typer
from rich.console import Console
from rich.table import Table

from company_cli.context import get_api
from company_cli.placeholders import handle_api_not_implemented, not_yet_implemented
from company_core.models.errors import NotImplementedFeatureError

console = Console()
mcp_app = typer.Typer(help="MCP registry and capability operations.")


@mcp_app.callback(invoke_without_command=True)
def mcp_group(ctx: typer.Context) -> None:
    """MCP platform commands."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())
        raise typer.Exit()


@mcp_app.command("list")
def mcp_list() -> None:
    """List registry MCPs and capabilities."""
    api = get_api()
    tools = api.mcp.list_tools()
    if not tools:
        not_yet_implemented("engineeringos mcp list (framework root required)")
        return

    table = Table(title="MCP Registry", show_header=True)
    table.add_column("ID", style="cyan")
    table.add_column("Category")
    table.add_column("Status")
    for tool in tools[:20]:
        table.add_row(tool.mcp_id, tool.category, tool.installation_status)
    if len(tools) > 20:
        table.add_row("…", f"+{len(tools) - 20} more", "")
    console.print(table)


@mcp_app.command("validate")
def mcp_validate() -> None:
    """Run MCP registry validation."""
    api = get_api()
    report = api.mcp.validate()
    table = Table(title="MCP Validate", show_header=True)
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Message")
    for check in report.checks:
        status = "[green]PASS[/green]" if check.passed else "[red]FAIL[/red]"
        table.add_row(check.name, status, check.message)
    console.print(table)
    if not report.passed:
        raise typer.Exit(code=1)


@mcp_app.command("doctor")
def mcp_doctor() -> None:
    """Run MCP health checks."""
    api = get_api()
    try:
        report = api.mcp.doctor()
    except NotImplementedFeatureError as exc:
        handle_api_not_implemented(exc)
        return

    table = Table(title="MCP Doctor", show_header=True)
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    table.add_column("Message")
    for check in report.checks:
        status = "[green]PASS[/green]" if check.passed else "[red]FAIL[/red]"
        table.add_row(check.name, status, check.message)
    console.print(table)
    if not report.passed:
        raise typer.Exit(code=1)


def register(app: typer.Typer) -> None:
    app.add_typer(mcp_app, name="mcp")
