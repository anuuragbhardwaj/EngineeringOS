"""KnowledgeAPI — Framework API surface for the Knowledge Platform."""

from __future__ import annotations

from pathlib import Path

from company_core.config.loader import discover_instance_root
from company_core.models.errors import ManifestNotFoundError
from knowledge.factory import create_knowledge_platform
from knowledge.types import KnowledgeObject, KnowledgeQuery, KnowledgeStats, RetrievalContext


class KnowledgeAPI:
    """Expose knowledge through FrameworkAPI — no direct storage access."""

    def __init__(self, instance_root: Path | None = None) -> None:
        self._instance_root = instance_root
        self._platform = create_knowledge_platform()

    def _root(self) -> Path:
        root = self._instance_root or discover_instance_root()
        if root is None:
            raise ManifestNotFoundError("company.yaml not found")
        return root.resolve()

    @property
    def platform(self):
        return self._platform

    @property
    def engine(self):
        return self._platform.engine

    @property
    def store(self):
        return self._platform.store

    @property
    def retriever(self):
        return self._platform.retriever

    @property
    def validator(self):
        return self._platform.validator

    @property
    def promoter(self):
        return self._platform.promoter

    @property
    def graph(self):
        return self._platform.graph

    @property
    def resolver(self):
        return self._platform.resolver

    def capture(self, **kwargs) -> KnowledgeObject:
        return self._platform.capture(self._root(), **kwargs)

    def get(self, knowledge_id: str, scope: str | None = None) -> KnowledgeObject:
        return self._platform.get(self._root(), knowledge_id, scope)

    def search(self, query: KnowledgeQuery) -> list[KnowledgeObject]:
        return self._platform.search(self._root(), query)

    def retrieve(self, context: RetrievalContext | None = None, **kwargs):
        return self._platform.retrieve(self._root(), context, **kwargs)

    def retrieve_for_prompt(self, **kwargs) -> dict[str, str]:
        return self._platform.retrieve_for_prompt(self._root(), **kwargs)

    def explain(self, knowledge_id: str) -> dict:
        return self._platform.explain(self._root(), knowledge_id)

    def validate(self, knowledge_id: str):
        return self._platform.validate(self._root(), knowledge_id)

    def promote(self, knowledge_id: str, **kwargs) -> KnowledgeObject:
        return self._platform.promote(self._root(), knowledge_id, **kwargs)

    def status(self) -> dict:
        return self._platform.status(self._root())

    def stats(self) -> KnowledgeStats:
        return self._platform.stats(self._root())

    def history(self, knowledge_id: str | None = None):
        return self._platform.history(self._root(), knowledge_id)

    def graph_view(self, knowledge_id: str, depth: int = 2) -> dict:
        return self._platform.graph_view(self._root(), knowledge_id, depth)

    def export_bundle(self) -> dict:
        return self._platform.export_bundle(self._root())

    def import_bundle(self, bundle: dict) -> int:
        return self._platform.import_bundle(self._root(), bundle)

    def handle_event(self, event_type: str, payload: dict) -> None:
        self._platform.handle_event(self._root(), event_type, payload)
