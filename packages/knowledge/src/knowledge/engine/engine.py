"""Knowledge engine — capture, classify, validate, store."""

from __future__ import annotations

from pathlib import Path

from knowledge.classification.classifier import KnowledgeClassifier
from knowledge.store.store import KnowledgeStore
from knowledge.types import (
    KnowledgeObject,
    KnowledgeScope,
    KnowledgeStatus,
    KnowledgeStats,
    utc_now,
)
from knowledge.validation.validator import KnowledgeValidator


class KnowledgeEngine:
    """Core knowledge lifecycle orchestration."""

    def __init__(
        self,
        store: KnowledgeStore | None = None,
        classifier: KnowledgeClassifier | None = None,
        validator: KnowledgeValidator | None = None,
    ) -> None:
        self._store = store or KnowledgeStore()
        self._classifier = classifier or KnowledgeClassifier()
        self._validator = validator or KnowledgeValidator(self._store)

    def capture(
        self,
        instance_root: Path,
        *,
        title: str,
        content: str,
        origin: str,
        owner: str,
        reason: str,
        knowledge_type: str | None = None,
        scope: str | None = None,
        confidence: float = 0.5,
        source_artifacts: list[str] | None = None,
        workspace_id: str | None = None,
        project_id: str | None = None,
        employee_id: str | None = None,
        conversation_id: str | None = None,
        tags: list[str] | None = None,
        artifact_root: Path | None = None,
        auto_activate: bool = False,
    ) -> KnowledgeObject:
        knowledge = KnowledgeObject(
            id=self._store.new_id(),
            knowledge_type=knowledge_type or "fact",
            scope=scope or KnowledgeScope.PROJECT.value,
            title=title,
            content=content,
            origin=origin,
            owner=owner,
            reason=reason,
            confidence=confidence,
            status=KnowledgeStatus.DRAFT.value,
            source_artifacts=source_artifacts or [],
            workspace_id=workspace_id,
            project_id=project_id,
            employee_id=employee_id,
            conversation_id=conversation_id,
            tags=tags or [],
        )
        knowledge = self._classifier.enrich(knowledge)
        result = self._validator.validate(instance_root, knowledge, artifact_root=artifact_root)
        if result.adjusted_confidence is not None:
            knowledge.confidence = result.adjusted_confidence
        if auto_activate and result.valid:
            knowledge.status = KnowledgeStatus.ACTIVE.value
        return self._store.save(instance_root, knowledge)

    def activate(self, instance_root: Path, knowledge_id: str) -> KnowledgeObject:
        knowledge = self._store.get(instance_root, knowledge_id)
        result = self._validator.validate(instance_root, knowledge)
        self._validator.assert_valid(result)
        knowledge.status = KnowledgeStatus.ACTIVE.value
        knowledge.confidence = result.adjusted_confidence or knowledge.confidence
        return self._store.save(instance_root, knowledge)

    def stats(self, instance_root: Path) -> KnowledgeStats:
        items = self._store.list_all(instance_root)
        stats = KnowledgeStats(total=len(items))
        confidences: list[float] = []
        for item in items:
            stats.by_scope[item.scope] = stats.by_scope.get(item.scope, 0) + 1
            stats.by_type[item.knowledge_type] = stats.by_type.get(item.knowledge_type, 0) + 1
            stats.by_status[item.status] = stats.by_status.get(item.status, 0) + 1
            confidences.append(item.confidence)
        stats.avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        stats.promotion_count = len(self._store.promotion_history(instance_root))
        return stats

    def version_bump(self, instance_root: Path, knowledge_id: str, content: str, reason: str) -> KnowledgeObject:
        knowledge = self._store.get(instance_root, knowledge_id)
        knowledge.version += 1
        knowledge.content = content
        knowledge.reason = reason
        knowledge.updated_at = utc_now()
        knowledge.metadata.setdefault("version_history", []).append(
            {"version": knowledge.version, "updated_at": knowledge.updated_at, "reason": reason}
        )
        return self._store.save(instance_root, knowledge)
