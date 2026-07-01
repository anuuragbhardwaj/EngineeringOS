"""status command — unified status engine."""

from __future__ import annotations

import json

import typer
from rich.console import Console

from company_cli.context import get_api

console = Console()


def register(app: typer.Typer) -> None:
    @app.command("status")
    def status_cmd(
        as_json: bool = typer.Option(False, "--json", help="Output as JSON."),
    ) -> None:
        """Show unified company, workspace, project, and execution status."""
        api = get_api()
        unified = api.context.status()
        api.context.platform.record_command("status")

        if as_json:
            console.print(
                json.dumps(
                    {
                        "company_id": unified.company_id,
                        "workspace_id": unified.workspace_id,
                        "project_id": unified.project_id,
                        "current_phase": unified.current_phase,
                        "current_employee": unified.current_employee,
                        "pipeline_progress": unified.pipeline_progress,
                        "execution_status": unified.execution_status,
                        "runtime_healthy": unified.runtime_healthy,
                        "mcp_healthy": unified.mcp_healthy,
                        "pending_actions": unified.pending_actions,
                        "pending_approvals": unified.pending_approvals,
                        "resume_points": unified.resume_points,
                        "recent_activity": unified.recent_activity,
                        "message": unified.message,
                    },
                    indent=2,
                )
            )
            return

        console.print("[bold]EngineeringOS Status[/bold]")
        console.print(f"  Company:    {unified.company_id or '—'}")
        console.print(f"  Workspace:  {unified.workspace_id or '—'}")
        console.print(f"  Project:    {unified.project_id or '—'}")
        console.print(f"  Phase:      {unified.current_phase or '—'}")
        console.print(f"  Employee:   {unified.current_employee or '—'}")
        console.print(f"  Pipeline:   {unified.pipeline_progress or '—'}")
        console.print(f"  Execution:  {unified.execution_status}")
        console.print(f"  Runtime:    {'healthy' if unified.runtime_healthy else 'issues'}")
        console.print(f"  MCP:        {'healthy' if unified.mcp_healthy else 'issues'}")
        if unified.pending_actions:
            console.print(f"  Pending:    {', '.join(unified.pending_actions)}")
        if unified.resume_points:
            console.print(f"  Resume:     {', '.join(unified.resume_points)}")
        if unified.recent_activity:
            console.print(f"  Recent:     {', '.join(unified.recent_activity)}")
        console.print(f"  {unified.message}")
