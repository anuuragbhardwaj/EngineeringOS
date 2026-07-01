"""Knowledge relationship graph."""

from __future__ import annotations

import uuid
from pathlib import Path

from knowledge.store.store import KnowledgeStore
from knowledge.types import KnowledgeRelation, RelationType, utc_now


class KnowledgeGraph:
    """Navigable knowledge relationships."""

    def __init__(self, store: KnowledgeStore | None = None) -> None:
        self._store = store or KnowledgeStore()

    def add_relation(
        self,
        instance_root: Path,
        source_id: str,
        target_id: str,
        relation_type: str,
        *,
        metadata: dict | None = None,
    ) -> KnowledgeRelation:
        relation = KnowledgeRelation(
            id=f"rel-{uuid.uuid4().hex[:10]}",
            source_id=source_id,
            target_id=target_id,
            relation_type=relation_type,
            created_at=utc_now(),
            metadata=metadata or {},
        )
        return self._store.save_relation(instance_root, relation)

    def relations_for(self, instance_root: Path, knowledge_id: str) -> list[KnowledgeRelation]:
        return [
            r
            for r in self._store.load_relations(instance_root)
            if r.source_id == knowledge_id or r.target_id == knowledge_id
        ]

    def neighbors(self, instance_root: Path, knowledge_id: str) -> list[dict]:
        results: list[dict] = []
        for relation in self.relations_for(instance_root, knowledge_id):
            other_id = relation.target_id if relation.source_id == knowledge_id else relation.source_id
            try:
                other = self._store.get(instance_root, other_id)
                results.append(
                    {
                        "relation_type": relation.relation_type,
                        "direction": "outgoing" if relation.source_id == knowledge_id else "incoming",
                        "knowledge": other.to_dict(),
                    }
                )
            except Exception:
                results.append(
                    {
                        "relation_type": relation.relation_type,
                        "direction": "outgoing" if relation.source_id == knowledge_id else "incoming",
                        "knowledge_id": other_id,
                    }
                )
        return results

    def explain_path(self, instance_root: Path, knowledge_id: str, depth: int = 2) -> dict:
        visited: set[str] = set()
        return self._walk(instance_root, knowledge_id, depth, visited)

    def _walk(self, instance_root: Path, node_id: str, depth: int, visited: set[str]) -> dict:
        if node_id in visited or depth < 0:
            return {"id": node_id}
        visited.add(node_id)
        try:
            node = self._store.get(instance_root, node_id)
            data = node.to_dict()
        except Exception:
            data = {"id": node_id}
        if depth == 0:
            return data
        data["relations"] = []
        for neighbor in self.neighbors(instance_root, node_id):
            child_id = neighbor.get("knowledge", {}).get("id") or neighbor.get("knowledge_id")
            if child_id:
                data["relations"].append(
                    {
                        "relation_type": neighbor["relation_type"],
                        "node": self._walk(instance_root, child_id, depth - 1, visited),
                    }
                )
        return data

    def find_conflicts(self, instance_root: Path, knowledge_id: str) -> list[KnowledgeRelation]:
        return [
            r
            for r in self.relations_for(instance_root, knowledge_id)
            if r.relation_type in (RelationType.CONTRADICTS.value, RelationType.DUPLICATES.value)
        ]
