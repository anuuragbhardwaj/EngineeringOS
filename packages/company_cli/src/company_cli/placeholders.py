"""Placeholder command helpers."""

from __future__ import annotations

import typer
from rich.console import Console

console = Console()


def not_yet_implemented(command: str) -> None:
    """Emit a clear placeholder message and exit successfully."""
    console.print(
        f"[yellow]Not Yet Implemented:[/yellow] `{command}` is planned but not "
        "available in this release.",
        highlight=False,
    )
    raise typer.Exit(code=0)


def handle_api_not_implemented(exc: Exception) -> None:
    message = str(exc).replace(" is not yet implemented", "")
    not_yet_implemented(message)
