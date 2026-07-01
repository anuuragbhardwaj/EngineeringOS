"""workspace commands."""

from __future__ import annotations

import typer

from company_cli.context import get_api
from company_cli.placeholders import handle_api_not_implemented, not_yet_implemented
from company_core.models.errors import NotImplementedFeatureError

workspace_app = typer.Typer(help="Manage workspaces.")


@workspace_app.command("create")
def workspace_create(workspace_id: str = typer.Argument(..., help="Workspace ID.")) -> None:
    """Create a new workspace under the company instance."""
    api = get_api()
    try:
        api.workspace.create(workspace_id)
    except NotImplementedFeatureError as exc:
        handle_api_not_implemented(exc)


@workspace_app.command("list")
def workspace_list() -> None:
    """List workspaces with project counts."""
    api = get_api()
    try:
        api.workspace.list()
    except NotImplementedFeatureError as exc:
        handle_api_not_implemented(exc)


def register(app: typer.Typer) -> None:
    app.add_typer(workspace_app, name="workspace")
