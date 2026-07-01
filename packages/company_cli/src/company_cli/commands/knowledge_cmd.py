"""Knowledge Platform CLI commands."""

from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from company_cli.context import get_api
from company_core.models.errors import ManifestNotFoundError
from knowledge.errors import KnowledgeNotFoundError, KnowledgePromotionError, KnowledgeValidationError
from knowledge.types import KnowledgeQuery

console = Console()


def register(app: typer.Typer) -> None:
    knowledge_app = typer.Typer(help="Engineering knowledge — capture, retrieve, promote.")
    app.add_typer(knowledge_app, name="knowledge")

    @knowledge_app.command("status")
    def status_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Show knowledge platform status."""
        api = get_api()
        try:
            data = api.knowledge.status()
        except ManifestNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        if as_json:
            console.print(json.dumps(data, indent=2))
            return
        console.print("[bold]Knowledge Platform Status[/bold]")
        console.print(f"  Total: {data['total']}")
        console.print(f"  Avg confidence: {data['avg_confidence']}")
        console.print(f"  Promotions: {data['promotions']}")

    @knowledge_app.command("search")
    def search_cmd(
        query: str = typer.Argument(..., help="Search text."),
        scope: str | None = typer.Option(None, "--scope"),
        knowledge_type: str | None = typer.Option(None, "--type"),
        as_json: bool = typer.Option(False, "--json"),
    ) -> None:
        """Search engineering knowledge."""
        api = get_api()
        try:
            results = api.knowledge.search(
                KnowledgeQuery(text=query, scope=scope, knowledge_type=knowledge_type)
            )
        except ManifestNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        if as_json:
            console.print(json.dumps([r.to_dict() for r in results], indent=2))
            return
        table = Table(title=f"Knowledge Search: {query}")
        table.add_column("ID")
        table.add_column("Type")
        table.add_column("Scope")
        table.add_column("Title")
        table.add_column("Confidence")
        for item in results:
            table.add_row(item.id, item.knowledge_type, item.scope, item.title[:40], f"{item.confidence:.2f}")
        console.print(table)

    @knowledge_app.command("explain")
    def explain_cmd(
        knowledge_id: str = typer.Argument(..., help="Knowledge ID."),
        as_json: bool = typer.Option(False, "--json"),
    ) -> None:
        """Explain knowledge origin, relations, and promotions."""
        api = get_api()
        try:
            data = api.knowledge.explain(knowledge_id)
        except (ManifestNotFoundError, KnowledgeNotFoundError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        if as_json:
            console.print(json.dumps(data, indent=2, default=str))
            return
        k = data["knowledge"]
        console.print(f"[bold]{k['title']}[/bold] ({k['id']})")
        console.print(f"  Type: {k['knowledge_type']} | Scope: {k['scope']} | Confidence: {k['confidence']}")
        console.print(f"  Origin: {k['origin']} | Owner: {k['owner']}")
        console.print(f"  Reason: {k['reason']}")
        console.print(f"\n{k['content']}")

    @knowledge_app.command("graph")
    def graph_cmd(
        knowledge_id: str = typer.Argument(..., help="Root knowledge ID."),
        depth: int = typer.Option(2, "--depth"),
        as_json: bool = typer.Option(False, "--json"),
    ) -> None:
        """Show knowledge relationship graph."""
        api = get_api()
        try:
            data = api.knowledge.graph_view(knowledge_id, depth=depth)
        except (ManifestNotFoundError, KnowledgeNotFoundError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        console.print(json.dumps(data, indent=2) if as_json else str(data))

    @knowledge_app.command("validate")
    def validate_cmd(knowledge_id: str = typer.Argument(..., help="Knowledge ID.")) -> None:
        """Validate knowledge before promotion."""
        api = get_api()
        try:
            result = api.knowledge.validate(knowledge_id)
        except (ManifestNotFoundError, KnowledgeNotFoundError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        if result.valid:
            console.print(f"[green]Valid[/green] — confidence {result.adjusted_confidence:.2f}")
        else:
            console.print(f"[red]Invalid[/red]: {'; '.join(result.issues)}")
        for warning in result.warnings:
            console.print(f"[yellow]Warning:[/yellow] {warning}")

    @knowledge_app.command("promote")
    def promote_cmd(
        knowledge_id: str = typer.Argument(..., help="Knowledge ID."),
        target_scope: str | None = typer.Option(None, "--to", help="Target scope."),
        reason: str = typer.Option("", "--reason"),
    ) -> None:
        """Promote knowledge (Engineering Manager approval)."""
        api = get_api()
        try:
            promoted = api.knowledge.promote(
                knowledge_id, target_scope=target_scope, reason=reason, reviewer_approved=True
            )
        except (ManifestNotFoundError, KnowledgeNotFoundError, KnowledgePromotionError) as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        console.print(f"[green]Promoted[/green] {knowledge_id} -> {promoted.scope} (v{promoted.version})")

    @knowledge_app.command("history")
    def history_cmd(
        knowledge_id: str | None = typer.Argument(None, help="Filter by knowledge ID."),
        as_json: bool = typer.Option(False, "--json"),
    ) -> None:
        """Show promotion history."""
        api = get_api()
        try:
            records = api.knowledge.history(knowledge_id)
        except ManifestNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        if as_json:
            console.print(json.dumps([r.__dict__ for r in records], indent=2, default=str))
            return
        table = Table(title="Promotion History")
        table.add_column("Knowledge")
        table.add_column("From")
        table.add_column("To")
        table.add_column("By")
        table.add_column("Rejected")
        for record in records:
            table.add_row(
                record.knowledge_id,
                record.from_scope,
                record.to_scope,
                record.approved_by,
                str(record.rejected),
            )
        console.print(table)

    @knowledge_app.command("stats")
    def stats_cmd(as_json: bool = typer.Option(False, "--json")) -> None:
        """Show knowledge statistics."""
        api = get_api()
        try:
            stats = api.knowledge.stats()
        except ManifestNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        if as_json:
            console.print(json.dumps(stats.__dict__, indent=2))
            return
        console.print(f"Total: {stats.total} | Avg confidence: {stats.avg_confidence:.2f}")

    @knowledge_app.command("export")
    def export_cmd(
        output: Path = typer.Argument(..., help="Output JSON file."),
    ) -> None:
        """Export knowledge bundle."""
        api = get_api()
        try:
            bundle = api.knowledge.export_bundle()
            output.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        except ManifestNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        console.print(f"[green]Exported[/green] to {output}")

    @knowledge_app.command("import")
    def import_cmd(
        input_path: Path = typer.Argument(..., help="Input JSON file."),
    ) -> None:
        """Import knowledge bundle."""
        api = get_api()
        try:
            bundle = json.loads(input_path.read_text(encoding="utf-8"))
            count = api.knowledge.import_bundle(bundle)
        except ManifestNotFoundError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from exc
        console.print(f"[green]Imported[/green] {count} knowledge objects")
