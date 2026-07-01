"""config command."""

from __future__ import annotations

import typer

from company_cli.placeholders import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command("config")
    def config_cmd() -> None:
        """View and manage EngineeringOS configuration."""
        not_yet_implemented("engineeringos config")
