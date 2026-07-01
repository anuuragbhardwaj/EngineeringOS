"""Git Operations Engineer extension points — no Git functionality implemented."""

from __future__ import annotations

from pathlib import Path

from knowledge.store.store import KnowledgeStore
from knowledge.types import KnowledgeQuery, KnowledgeType


class GitKnowledgeExtension:
    """Prepare knowledge for future Git Operations Engineer."""

    def __init__(self, store: KnowledgeStore | None = None) -> None:
        self._store = store or KnowledgeStore()

    def commit_message_hints(self, instance_root: Path, project_id: str) -> list[str]:
        query = KnowledgeQuery(
            project_id=project_id,
            knowledge_type=KnowledgeType.IMPLEMENTATION_NOTE.value,
            limit=5,
        )
        return [f"{k.title}: {k.content[:120]}" for k in self._store.query(instance_root, query)]

    def release_notes(self, instance_root: Path, project_id: str) -> list[dict]:
        query = KnowledgeQuery(
            project_id=project_id,
            knowledge_type=KnowledgeType.RELEASE_NOTE.value,
            limit=20,
        )
        return [k.to_dict() for k in self._store.query(instance_root, query)]

    def change_summary(self, instance_root: Path, project_id: str) -> dict:
        notes = self.commit_message_hints(instance_root, project_id)
        releases = self.release_notes(instance_root, project_id)
        return {"commit_hints": notes, "release_notes": releases, "milestone_ready": bool(releases)}

    def semantic_version_suggestion(self, instance_root: Path, project_id: str) -> str:
        risks = self._store.query(
            instance_root,
            KnowledgeQuery(project_id=project_id, knowledge_type=KnowledgeType.RISK.value, limit=3),
        )
        breaking = self._store.query(
            instance_root,
            KnowledgeQuery(project_id=project_id, knowledge_type=KnowledgeType.MIGRATION_RULE.value, limit=3),
        )
        if breaking:
            return "major"
        if risks:
            return "minor"
        return "patch"
