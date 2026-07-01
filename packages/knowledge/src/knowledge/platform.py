"""Knowledge Platform facade."""

from __future__ import annotations

import json
from pathlib import Path

from knowledge.aging.aging import KnowledgeAging
from knowledge.engine.engine import KnowledgeEngine
from knowledge.events.handlers import KnowledgeEventHandler
from knowledge.git_hooks.extension import GitKnowledgeExtension
from knowledge.promotion.promoter import KnowledgePromoter
from knowledge.relationships.graph import KnowledgeGraph
from knowledge.resolver.resolver import KnowledgeResolver
from knowledge.retrieval.retriever import KnowledgeRetriever
from knowledge.store.paths import ensure_knowledge_dirs
from knowledge.store.store import KnowledgeStore
from knowledge.types import KnowledgeObject, KnowledgeQuery, KnowledgeStats, RetrievalContext
from knowledge.validation.validator import KnowledgeValidator


class KnowledgePlatform:
    """Permanent intelligence layer for EngineeringOS."""

    def __init__(self) -> None:
        self._store = KnowledgeStore()
        self._engine = KnowledgeEngine(self._store)
        self._retriever = KnowledgeRetriever(self._store)
        self._validator = KnowledgeValidator(self._store)
        self._promoter = KnowledgePromoter(self._store, self._validator)
        self._graph = KnowledgeGraph(self._store)
        self._resolver = KnowledgeResolver()
        self._aging = KnowledgeAging(self._store)
        self._events = KnowledgeEventHandler(self._engine)
        self._git = GitKnowledgeExtension(self._store)

    @property
    def store(self) -> KnowledgeStore:
        return self._store

    @property
    def engine(self) -> KnowledgeEngine:
        return self._engine

    @property
    def retriever(self) -> KnowledgeRetriever:
        return self._retriever

    @property
    def validator(self) -> KnowledgeValidator:
        return self._validator

    @property
    def promoter(self) -> KnowledgePromoter:
        return self._promoter

    @property
    def graph(self) -> KnowledgeGraph:
        return self._graph

    @property
    def resolver(self) -> KnowledgeResolver:
        return self._resolver

    def ensure_dirs(self, instance_root: Path) -> None:
        ensure_knowledge_dirs(instance_root)

    def capture(self, instance_root: Path, **kwargs) -> KnowledgeObject:
        self.ensure_dirs(instance_root)
        return self._engine.capture(instance_root, **kwargs)

    def get(self, instance_root: Path, knowledge_id: str, scope: str | None = None) -> KnowledgeObject:
        return self._store.get(instance_root, knowledge_id, scope)

    def search(self, instance_root: Path, query: KnowledgeQuery) -> list[KnowledgeObject]:
        return self._retriever.search(instance_root, query)

    def retrieve(self, instance_root: Path, context: RetrievalContext | None = None, **kwargs):
        ctx = context or self._resolver.resolve(instance_root, **kwargs)
        return self._retriever.retrieve(instance_root, ctx)

    def retrieve_for_prompt(self, instance_root: Path, **kwargs) -> dict[str, str]:
        ctx = self._resolver.resolve(instance_root, **kwargs)
        return self._retriever.retrieve_for_prompt(instance_root, ctx)

    def explain(self, instance_root: Path, knowledge_id: str) -> dict:
        return self._retriever.explain(instance_root, knowledge_id)

    def validate(self, instance_root: Path, knowledge_id: str):
        knowledge = self._store.get(instance_root, knowledge_id)
        return self._validator.validate(instance_root, knowledge)

    def promote(self, instance_root: Path, knowledge_id: str, **kwargs) -> KnowledgeObject:
        return self._promoter.promote(instance_root, knowledge_id, **kwargs)

    def graph_view(self, instance_root: Path, knowledge_id: str, depth: int = 2) -> dict:
        return self._graph.explain_path(instance_root, knowledge_id, depth)

    def add_relation(self, instance_root: Path, source_id: str, target_id: str, relation_type: str):
        return self._graph.add_relation(instance_root, source_id, target_id, relation_type)

    def stats(self, instance_root: Path) -> KnowledgeStats:
        return self._engine.stats(instance_root)

    def status(self, instance_root: Path) -> dict:
        stats = self.stats(instance_root)
        return {
            "total": stats.total,
            "by_scope": stats.by_scope,
            "by_type": stats.by_type,
            "by_status": stats.by_status,
            "avg_confidence": round(stats.avg_confidence, 3),
            "promotions": stats.promotion_count,
        }

    def history(self, instance_root: Path, knowledge_id: str | None = None):
        return self._store.promotion_history(instance_root, knowledge_id)

    def export_bundle(self, instance_root: Path) -> dict:
        return self._store.export_all(instance_root)

    def import_bundle(self, instance_root: Path, bundle: dict) -> int:
        self.ensure_dirs(instance_root)
        return self._store.import_bundle(instance_root, bundle)

    def export_file(self, instance_root: Path, output: Path) -> Path:
        bundle = self.export_bundle(instance_root)
        output.write_text(json.dumps(bundle, indent=2), encoding="utf-8")
        return output

    def import_file(self, instance_root: Path, input_path: Path) -> int:
        bundle = json.loads(input_path.read_text(encoding="utf-8"))
        return self.import_bundle(instance_root, bundle)

    def handle_event(self, instance_root: Path, event_type: str, payload: dict) -> None:
        self._events.handle(instance_root, event_type, payload)

    def git_extension(self) -> GitKnowledgeExtension:
        return self._git

    def apply_aging(self, instance_root: Path) -> list[str]:
        return self._aging.apply_aging_policies(instance_root)
