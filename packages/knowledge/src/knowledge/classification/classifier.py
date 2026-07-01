"""Knowledge classification."""

from __future__ import annotations

from knowledge.types import KnowledgeObject, KnowledgeScope, KnowledgeType


class KnowledgeClassifier:
    """Classify captured knowledge by type and scope."""

    TYPE_KEYWORDS: dict[str, tuple[str, ...]] = {
        KnowledgeType.DECISION.value: ("decided", "decision", "chose", "selected"),
        KnowledgeType.LESSON.value: ("learned", "lesson", "takeaway", "mistake"),
        KnowledgeType.CONVENTION.value: ("convention", "standard", "always", "never"),
        KnowledgeType.BUG_PATTERN.value: ("bug", "defect", "regression", "fix"),
        KnowledgeType.ARCHITECTURE_DECISION.value: ("architecture", "adr", "design"),
        KnowledgeType.REQUIREMENT.value: ("requirement", "must", "shall", "need"),
        KnowledgeType.RISK.value: ("risk", "danger", "caution", "warning"),
        KnowledgeType.QA_FINDING.value: ("qa", "test failed", "quality"),
        KnowledgeType.REVIEW_FINDING.value: ("review", "finding", "feedback"),
    }

    def classify_type(self, title: str, content: str, hint: str | None = None) -> str:
        if hint and hint in {t.value for t in KnowledgeType}:
            return hint
        text = f"{title} {content}".lower()
        for knowledge_type, keywords in self.TYPE_KEYWORDS.items():
            if any(word in text for word in keywords):
                return knowledge_type
        return KnowledgeType.FACT.value

    def classify_scope(
        self,
        *,
        conversation_id: str | None = None,
        employee_id: str | None = None,
        project_id: str | None = None,
        workspace_id: str | None = None,
        explicit_scope: str | None = None,
    ) -> str:
        if explicit_scope:
            return explicit_scope
        if conversation_id:
            return KnowledgeScope.CONVERSATION.value
        if employee_id and not project_id:
            return KnowledgeScope.EMPLOYEE.value
        if project_id:
            return KnowledgeScope.PROJECT.value
        if workspace_id:
            return KnowledgeScope.WORKSPACE.value
        return KnowledgeScope.COMPANY.value

    def enrich(self, knowledge: KnowledgeObject) -> KnowledgeObject:
        knowledge.knowledge_type = self.classify_type(
            knowledge.title, knowledge.content, knowledge.knowledge_type
        )
        knowledge.scope = self.classify_scope(
            conversation_id=knowledge.conversation_id,
            employee_id=knowledge.employee_id,
            project_id=knowledge.project_id,
            workspace_id=knowledge.workspace_id,
            explicit_scope=knowledge.scope,
        )
        return knowledge
