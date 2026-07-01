"""Knowledge aging — deprecation, archival, retirement."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from knowledge.store.store import KnowledgeStore
from knowledge.types import KnowledgeObject, KnowledgeScope, KnowledgeStatus, utc_now


class KnowledgeAging:
    """Mature knowledge over time — retire stale low-value records."""

    CONVERSATION_TTL_DAYS = 30
    STALE_DAYS = 180

    def __init__(self, store: KnowledgeStore | None = None) -> None:
        self._store = store or KnowledgeStore()

    def deprecate(self, instance_root: Path, knowledge_id: str, reason: str = "") -> KnowledgeObject:
        knowledge = self._store.get(instance_root, knowledge_id)
        knowledge.status = KnowledgeStatus.DEPRECATED.value
        knowledge.metadata["deprecated_at"] = utc_now()
        if reason:
            knowledge.metadata["deprecation_reason"] = reason
        return self._store.save(instance_root, knowledge)

    def archive(self, instance_root: Path, knowledge_id: str) -> KnowledgeObject:
        knowledge = self._store.get(instance_root, knowledge_id)
        knowledge.status = KnowledgeStatus.ARCHIVED.value
        knowledge.metadata["archived_at"] = utc_now()
        return self._store.save(instance_root, knowledge)

    def retire(self, instance_root: Path, knowledge_id: str, reason: str = "") -> KnowledgeObject:
        knowledge = self._store.get(instance_root, knowledge_id)
        knowledge.status = KnowledgeStatus.RETIRED.value
        knowledge.metadata["retired_at"] = utc_now()
        if reason:
            knowledge.metadata["retirement_reason"] = reason
        return self._store.save(instance_root, knowledge)

    def apply_aging_policies(self, instance_root: Path) -> list[str]:
        """Auto-age conversation knowledge and stale drafts."""
        affected: list[str] = []
        now = datetime.utcnow()
        for item in self._store.list_all(instance_root):
            if item.status not in (KnowledgeStatus.ACTIVE.value, KnowledgeStatus.DRAFT.value):
                continue
            updated = self._parse_time(item.updated_at or item.created_at)
            if not updated:
                continue
            age = now - updated
            if item.scope == KnowledgeScope.CONVERSATION.value and age > timedelta(days=self.CONVERSATION_TTL_DAYS):
                self.archive(instance_root, item.id)
                affected.append(item.id)
            elif item.status == KnowledgeStatus.DRAFT.value and age > timedelta(days=self.STALE_DAYS):
                self.deprecate(instance_root, item.id, reason="stale draft")
                affected.append(item.id)
        return affected

    def _parse_time(self, value: str) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
