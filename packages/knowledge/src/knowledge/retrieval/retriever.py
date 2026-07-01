"""Context-aware knowledge retrieval."""

from __future__ import annotations

from pathlib import Path

from knowledge.reasoning.reasoning import KnowledgeReasoning
from knowledge.store.store import KnowledgeStore
from knowledge.types import (
    KnowledgeObject,
    KnowledgeQuery,
    KnowledgeScope,
    KnowledgeStatus,
    RetrievalContext,
    RetrievalResult,
)


class KnowledgeRetriever:
    """Retrieve only relevant knowledge — never dump everything into prompts."""

    def __init__(
        self,
        store: KnowledgeStore | None = None,
        reasoning: KnowledgeReasoning | None = None,
    ) -> None:
        self._store = store or KnowledgeStore()
        self._reasoning = reasoning or KnowledgeReasoning()

    def retrieve(self, instance_root: Path, context: RetrievalContext) -> list[RetrievalResult]:
        candidates = self._eligible(instance_root, context)
        scored: list[RetrievalResult] = []
        for item in candidates:
            relevance, explanation = self._reasoning.score(item, context)
            if relevance >= context.min_confidence:
                scored.append(RetrievalResult(knowledge=item, relevance=relevance, explanation=explanation))
        scored.sort(key=lambda r: r.relevance, reverse=True)
        return scored[: context.max_items]

    def retrieve_for_prompt(self, instance_root: Path, context: RetrievalContext) -> dict[str, str]:
        """Return knowledge snippets keyed by type for prompt injection."""
        results = self.retrieve(instance_root, context)
        snippets: dict[str, str] = {}
        for result in results:
            key = f"{result.knowledge.knowledge_type}:{result.knowledge.id}"
            snippets[key] = (
                f"[{result.knowledge.knowledge_type}] {result.knowledge.title}\n"
                f"{result.knowledge.content}\n"
                f"(relevance: {result.relevance:.2f} — {result.explanation})"
            )
            result.knowledge.usage_count += 1
            self._store.save(instance_root, result.knowledge)
        return snippets

    def search(self, instance_root: Path, query: KnowledgeQuery) -> list[KnowledgeObject]:
        return self._store.query(instance_root, query)

    def explain(self, instance_root: Path, knowledge_id: str) -> dict:
        knowledge = self._store.get(instance_root, knowledge_id)
        from knowledge.relationships.graph import KnowledgeGraph

        graph = KnowledgeGraph(self._store)
        return {
            "knowledge": knowledge.to_dict(),
            "relations": graph.neighbors(instance_root, knowledge_id),
            "promotions": [
                r.__dict__
                for r in self._store.promotion_history(instance_root, knowledge_id)
            ],
        }

    def _eligible(self, instance_root: Path, context: RetrievalContext) -> list[KnowledgeObject]:
        items = self._store.list_all(instance_root)
        eligible: list[KnowledgeObject] = []
        for item in items:
            if item.status not in (KnowledgeStatus.ACTIVE.value, KnowledgeStatus.DRAFT.value):
                continue
            if item.scope == KnowledgeScope.CONVERSATION.value:
                continue
            if item.confidence < context.min_confidence:
                continue
            eligible.append(item)
        return eligible
