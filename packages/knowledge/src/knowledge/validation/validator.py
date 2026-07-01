"""Knowledge validation — nothing becomes permanent without traceability."""

from __future__ import annotations

from pathlib import Path

from knowledge.errors import KnowledgeValidationError
from knowledge.store.store import KnowledgeStore
from knowledge.types import KnowledgeObject, KnowledgeScope, KnowledgeStatus, SCOPE_HIERARCHY, ValidationResult


class KnowledgeValidator:
    """Evaluate knowledge before acceptance or promotion."""

    MIN_PROMOTION_CONFIDENCE = 0.7

    def __init__(self, store: KnowledgeStore | None = None) -> None:
        self._store = store or KnowledgeStore()

    def validate(
        self,
        instance_root: Path,
        knowledge: KnowledgeObject,
        *,
        artifact_root: Path | None = None,
    ) -> ValidationResult:
        issues: list[str] = []
        warnings: list[str] = []
        confidence = knowledge.confidence

        if not knowledge.origin:
            issues.append("Missing origin")
        if not knowledge.owner:
            issues.append("Missing owner")
        if not knowledge.reason:
            warnings.append("Missing reason — knowledge should be explainable")
        if not knowledge.title.strip():
            issues.append("Missing title")
        if not knowledge.content.strip():
            issues.append("Missing content")

        for artifact in knowledge.source_artifacts:
            if artifact_root:
                path = artifact_root / artifact
                if not path.is_file():
                    warnings.append(f"Source artifact not found: {artifact}")
                    confidence = max(0.1, confidence - 0.1)

        duplicates = self._find_duplicates(instance_root, knowledge)
        if duplicates:
            warnings.append(f"Possible duplicates: {', '.join(duplicates[:3])}")
            confidence = max(0.1, confidence - 0.05 * len(duplicates))

        conflicts = self._find_conflicts(instance_root, knowledge)
        if conflicts:
            issues.append(f"Conflicts with: {', '.join(conflicts[:3])}")

        if knowledge.scope == KnowledgeScope.FRAMEWORK.value:
            issues.append("Framework knowledge is immutable and cannot be created via company store")

        return ValidationResult(
            valid=len(issues) == 0,
            knowledge_id=knowledge.id,
            issues=issues,
            warnings=warnings,
            adjusted_confidence=confidence,
        )

    def validate_for_promotion(
        self,
        instance_root: Path,
        knowledge_id: str,
        target_scope: str,
    ) -> ValidationResult:
        knowledge = self._store.get(instance_root, knowledge_id)
        result = self.validate(instance_root, knowledge)
        issues = list(result.issues)
        warnings = list(result.warnings)
        confidence = result.adjusted_confidence or knowledge.confidence

        if knowledge.status not in (KnowledgeStatus.ACTIVE.value, KnowledgeStatus.DRAFT.value):
            issues.append(f"Cannot promote knowledge in status {knowledge.status}")

        if confidence < self.MIN_PROMOTION_CONFIDENCE:
            issues.append(
                f"Confidence {confidence:.2f} below promotion threshold {self.MIN_PROMOTION_CONFIDENCE}"
            )

        if target_scope == KnowledgeScope.COMPANY.value and not knowledge.reviewer_approved:
            if knowledge.scope in (KnowledgeScope.CONVERSATION.value, KnowledgeScope.EMPLOYEE.value):
                issues.append("Low-confidence conversation/employee knowledge requires reviewer approval")

        scope_order = [s.value for s in SCOPE_HIERARCHY]
        if scope_order.index(target_scope) <= scope_order.index(knowledge.scope):
            issues.append(f"Cannot promote to same or lower scope ({knowledge.scope} -> {target_scope})")

        return ValidationResult(
            valid=len(issues) == 0,
            knowledge_id=knowledge_id,
            issues=issues,
            warnings=warnings,
            adjusted_confidence=confidence,
        )

    def assert_valid(self, result: ValidationResult) -> None:
        if not result.valid:
            raise KnowledgeValidationError("; ".join(result.issues))

    def _find_duplicates(self, instance_root: Path, knowledge: KnowledgeObject) -> list[str]:
        matches: list[str] = []
        for item in self._store.list_all(instance_root):
            if item.id == knowledge.id:
                continue
            if item.title.lower() == knowledge.title.lower() and item.content[:200] == knowledge.content[:200]:
                matches.append(item.id)
        return matches

    def _find_conflicts(self, instance_root: Path, knowledge: KnowledgeObject) -> list[str]:
        from knowledge.relationships.graph import KnowledgeGraph

        graph = KnowledgeGraph(self._store)
        return [r.target_id for r in graph.find_conflicts(instance_root, knowledge.id)]
