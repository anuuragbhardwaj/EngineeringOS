"""Knowledge persistence layer."""

from __future__ import annotations

import json
import uuid
from pathlib import Path

import yaml

from knowledge.errors import KnowledgeNotFoundError
from knowledge.store.paths import (
    ensure_knowledge_dirs,
    framework_knowledge_dir,
    knowledge_file,
    promotions_file,
    relations_file,
    scope_dir,
)
from knowledge.types import (
    KnowledgeObject,
    KnowledgeQuery,
    KnowledgeRelation,
    KnowledgeScope,
    KnowledgeStatus,
    PromotionRecord,
    utc_now,
)


class KnowledgeStore:
    """Persist knowledge inside generated companies — framework remains stateless."""

    def save(self, instance_root: Path, knowledge: KnowledgeObject) -> KnowledgeObject:
        instance_root = instance_root.resolve()
        ensure_knowledge_dirs(instance_root)
        now = utc_now()
        if not knowledge.created_at:
            knowledge.created_at = now
        knowledge.updated_at = now
        path = knowledge_file(instance_root, knowledge.scope, knowledge.id)
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(knowledge.to_dict(), handle, sort_keys=False, default_flow_style=False)
        self._update_index(instance_root, knowledge)
        return knowledge

    def get(self, instance_root: Path, knowledge_id: str, scope: str | None = None) -> KnowledgeObject:
        instance_root = instance_root.resolve()
        if scope:
            path = knowledge_file(instance_root, scope, knowledge_id)
            if path.is_file():
                return self._load_file(path)
            raise KnowledgeNotFoundError(f"Knowledge {knowledge_id} not found in scope {scope}")

        for scope_name in KnowledgeScope:
            path = knowledge_file(instance_root, scope_name.value, knowledge_id)
            if path.is_file():
                return self._load_file(path)
        raise KnowledgeNotFoundError(f"Knowledge {knowledge_id} not found")

    def delete(self, instance_root: Path, knowledge_id: str, scope: str) -> None:
        path = knowledge_file(instance_root, scope, knowledge_id)
        if path.is_file():
            path.unlink()

    def list_scope(self, instance_root: Path, scope: str) -> list[KnowledgeObject]:
        directory = scope_dir(instance_root, scope)
        items: list[KnowledgeObject] = []
        for path in sorted(directory.glob("*.yaml")):
            items.append(self._load_file(path))
        return items

    def list_all(self, instance_root: Path) -> list[KnowledgeObject]:
        items: list[KnowledgeObject] = []
        for scope in KnowledgeScope:
            if scope == KnowledgeScope.FRAMEWORK:
                items.extend(self.load_framework_knowledge())
                continue
            items.extend(self.list_scope(instance_root, scope.value))
        return items

    def query(self, instance_root: Path, query: KnowledgeQuery) -> list[KnowledgeObject]:
        candidates = self.list_all(instance_root)
        results: list[KnowledgeObject] = []
        needle = (query.text or "").lower()

        for item in candidates:
            if query.scope and item.scope != query.scope:
                continue
            if query.knowledge_type and item.knowledge_type != query.knowledge_type:
                continue
            if query.project_id and item.project_id != query.project_id:
                continue
            if query.workspace_id and item.workspace_id != query.workspace_id:
                continue
            if query.employee_id and item.employee_id != query.employee_id:
                continue
            if query.status and item.status != query.status:
                continue
            if item.confidence < query.min_confidence:
                continue
            if query.tags and not any(tag in item.tags for tag in query.tags):
                continue
            if needle:
                haystack = f"{item.title} {item.content} {' '.join(item.tags)}".lower()
                if needle not in haystack:
                    continue
            results.append(item)

        results.sort(key=lambda k: (-k.confidence, k.updated_at), reverse=False)
        return results[: query.limit]

    def load_framework_knowledge(self) -> list[KnowledgeObject]:
        directory = framework_knowledge_dir()
        if not directory.is_dir():
            return []
        items: list[KnowledgeObject] = []
        for path in sorted(directory.glob("*.yaml")):
            obj = self._load_file(path)
            obj.scope = KnowledgeScope.FRAMEWORK.value
            items.append(obj)
        return items

    def save_relation(self, instance_root: Path, relation: KnowledgeRelation) -> KnowledgeRelation:
        ensure_knowledge_dirs(instance_root)
        if not relation.created_at:
            relation.created_at = utc_now()
        relations = self.load_relations(instance_root)
        relations = [r for r in relations if r.id != relation.id]
        relations.append(relation)
        path = relations_file(instance_root)
        data = [r.to_dict() for r in relations]
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(data, handle, sort_keys=False, default_flow_style=False)
        return relation

    def load_relations(self, instance_root: Path) -> list[KnowledgeRelation]:
        path = relations_file(instance_root)
        if not path.is_file():
            return []
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or []
        return [KnowledgeRelation.from_dict(entry) for entry in data]

    def record_promotion(self, instance_root: Path, record: PromotionRecord) -> None:
        ensure_knowledge_dirs(instance_root)
        path = promotions_file(instance_root)
        history: list[dict] = []
        if path.is_file():
            with path.open(encoding="utf-8") as handle:
                history = yaml.safe_load(handle) or []
        history.append(
            {
                "knowledge_id": record.knowledge_id,
                "from_scope": record.from_scope,
                "to_scope": record.to_scope,
                "approved_by": record.approved_by,
                "reason": record.reason,
                "timestamp": record.timestamp,
                "rejected": record.rejected,
                "rejection_reason": record.rejection_reason,
            }
        )
        with path.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(history, handle, sort_keys=False, default_flow_style=False)

    def promotion_history(self, instance_root: Path, knowledge_id: str | None = None) -> list[PromotionRecord]:
        path = promotions_file(instance_root)
        if not path.is_file():
            return []
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or []
        records = [
            PromotionRecord(
                knowledge_id=entry["knowledge_id"],
                from_scope=entry["from_scope"],
                to_scope=entry["to_scope"],
                approved_by=entry["approved_by"],
                reason=entry["reason"],
                timestamp=entry["timestamp"],
                rejected=bool(entry.get("rejected", False)),
                rejection_reason=entry.get("rejection_reason"),
            )
            for entry in data
        ]
        if knowledge_id:
            return [r for r in records if r.knowledge_id == knowledge_id]
        return records

    def export_all(self, instance_root: Path) -> dict:
        return {
            "knowledge": [k.to_dict() for k in self.list_all(instance_root)],
            "relations": [r.to_dict() for r in self.load_relations(instance_root)],
            "promotions": [
                r.__dict__ for r in self.promotion_history(instance_root)
            ],
        }

    def import_bundle(self, instance_root: Path, bundle: dict) -> int:
        count = 0
        for entry in bundle.get("knowledge", []):
            self.save(instance_root, KnowledgeObject.from_dict(entry))
            count += 1
        for entry in bundle.get("relations", []):
            self.save_relation(instance_root, KnowledgeRelation.from_dict(entry))
        return count

    def new_id(self, prefix: str = "kn") -> str:
        return f"{prefix}-{uuid.uuid4().hex[:12]}"

    def _load_file(self, path: Path) -> KnowledgeObject:
        with path.open(encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
        return KnowledgeObject.from_dict(data)

    def _update_index(self, instance_root: Path, knowledge: KnowledgeObject) -> None:
        index_path = scope_dir(instance_root, "indexes") / "by_scope.json"
        index: dict[str, list[str]] = {}
        if index_path.is_file():
            index = json.loads(index_path.read_text(encoding="utf-8"))
        scope_ids = index.setdefault(knowledge.scope, [])
        if knowledge.id not in scope_ids:
            scope_ids.append(knowledge.id)
        index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")
