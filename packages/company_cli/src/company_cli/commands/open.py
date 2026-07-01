"""open command."""

from __future__ import annotations

import typer

from company_cli.placeholders import not_yet_implemented


def register(app: typer.Typer) -> None:
    @app.command("open")
    def open_cmd(
        workspace: str | None = typer.Option(
            None,
            "--workspace",
            help="Workspace ID to open.",
        ),
    ) -> None:
        """Set active company/workspace context."""
        not_yet_implemented("engineeringos open")
