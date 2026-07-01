"""employees command."""

from __future__ import annotations

import typer

from company_cli.context import get_api
from company_cli.placeholders import handle_api_not_implemented
from company_core.models.errors import NotImplementedFeatureError


def register(app: typer.Typer) -> None:
    @app.command("employees")
    def employees_cmd(
        phase: str | None = typer.Option(
            None,
            "--phase",
            help="Filter employees by SDLc phase.",
        ),
    ) -> None:
        """List employees, roles, and required capabilities."""
        api = get_api()
        try:
            if phase:
                api.employee.for_phase(phase)
            else:
                api.employee.list()
        except NotImplementedFeatureError as exc:
            handle_api_not_implemented(exc)
