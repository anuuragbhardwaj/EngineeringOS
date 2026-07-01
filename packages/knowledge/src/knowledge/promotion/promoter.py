"""Knowledge promotion — Engineering Manager controlled."""

from __future__ import annotations

from pathlib import Path

from knowledge.errors import KnowledgePromotionError
from knowledge.store.store import KnowledgeStore
from knowledge.types import (
    KnowledgeObject,
    KnowledgeScope,
    KnowledgeStatus,
    PromotionRecord,
    utc_now,
)
from knowledge.validation.validator import KnowledgeValidator


SCOPE_PROMOTION_CHAIN = {
    KnowledgeScope.CONVERSATION.value: KnowledgeScope.EMPLOYEE.value,
    KnowledgeScope.EMPLOYEE.value: KnowledgeScope.PROJECT.value,
    KnowledgeScope.PROJECT.value: KnowledgeScope.WORKSPACE.value,
    KnowledgeScope.WORKSPACE.value: KnowledgeScope.COMPANY.value,
    KnowledgeScope.COMPANY.value: KnowledgeScope.FRAMEWORK.value,
}


class KnowledgePromoter:
    """Promote validated knowledge upward through scope hierarchy."""

    def __init__(
        self,
        store: KnowledgeStore | None = None,
        validator: KnowledgeValidator | None = None,
    ) -> None:
        self._store = store or KnowledgeStore()
        self._validator = validator or KnowledgeValidator(self._store)

    def promote(
        self,
        instance_root: Path,
        knowledge_id: str,
        *,
        target_scope: str | None = None,
        approved_by: str = "engineering-manager",
        reason: str = "",
        reviewer_approved: bool = False,
    ) -> KnowledgeObject:
        knowledge = self._store.get(instance_root, knowledge_id)
        target = target_scope or SCOPE_PROMOTION_CHAIN.get(knowledge.scope)
        if not target:
            raise KnowledgePromotionError(f"No promotion path from scope {knowledge.scope}")

        if reviewer_approved:
            knowledge.reviewer_approved = True

        validation = self._validator.validate_for_promotion(instance_root, knowledge_id, target)
        if not validation.valid:
            self._store.record_promotion(
                instance_root,
                PromotionRecord(
                    knowledge_id=knowledge_id,
                    from_scope=knowledge.scope,
                    to_scope=target,
                    approved_by=approved_by,
                    reason=reason,
                    timestamp=utc_now(),
                    rejected=True,
                    rejection_reason="; ".join(validation.issues),
                ),
            )
            raise KnowledgePromotionError("; ".join(validation.issues))

        promoted = KnowledgeObject.from_dict(knowledge.to_dict())
        promoted.scope = target
        promoted.version = knowledge.version + 1
        promoted.status = KnowledgeStatus.ACTIVE.value
        promoted.confidence = validation.adjusted_confidence or knowledge.confidence
        promoted.metadata["promoted_from"] = knowledge.scope
        promoted.metadata["promoted_at"] = utc_now()

        self._store.save(instance_root, promoted)
        self._store.record_promotion(
            instance_root,
            PromotionRecord(
                knowledge_id=knowledge_id,
                from_scope=knowledge.scope,
                to_scope=target,
                approved_by=approved_by,
                reason=reason or f"Promoted to {target}",
                timestamp=utc_now(),
            ),
        )
        return promoted

    def reject_promotion(
        self,
        instance_root: Path,
        knowledge_id: str,
        *,
        rejected_by: str = "engineering-manager",
        reason: str,
    ) -> PromotionRecord:
        knowledge = self._store.get(instance_root, knowledge_id)
        record = PromotionRecord(
            knowledge_id=knowledge_id,
            from_scope=knowledge.scope,
            to_scope=knowledge.scope,
            approved_by=rejected_by,
            reason=reason,
            timestamp=utc_now(),
            rejected=True,
            rejection_reason=reason,
        )
        self._store.record_promotion(instance_root, record)
        return record
