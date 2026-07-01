"""Relevance scoring for knowledge retrieval."""

from __future__ import annotations

from knowledge.types import KnowledgeObject, RetrievalContext


class KnowledgeReasoning:
    """Score knowledge relevance for contextual retrieval."""

    SCOPE_WEIGHTS = {
        "framework": 0.3,
        "company": 0.5,
        "workspace": 0.7,
        "project": 1.0,
        "employee": 0.9,
        "conversation": 0.4,
    }

    def score(self, knowledge: KnowledgeObject, context: RetrievalContext) -> tuple[float, str]:
        score = knowledge.confidence * self.SCOPE_WEIGHTS.get(knowledge.scope, 0.5)
        reasons: list[str] = [f"base confidence {knowledge.confidence:.2f}"]

        if context.project_id and knowledge.project_id == context.project_id:
            score += 0.3
            reasons.append("matches project")
        elif context.project_id and knowledge.project_id and knowledge.project_id != context.project_id:
            score -= 0.2

        if context.workspace_id and knowledge.workspace_id == context.workspace_id:
            score += 0.15
            reasons.append("matches workspace")

        if context.employee_id and knowledge.employee_id == context.employee_id:
            score += 0.2
            reasons.append("matches employee")

        if context.phase_id:
            phase_hint = context.phase_id.lower()
            if phase_hint in knowledge.title.lower() or phase_hint in knowledge.content.lower():
                score += 0.15
                reasons.append("matches phase")

        for artifact in context.artifacts:
            if artifact in knowledge.source_artifacts:
                score += 0.1
                reasons.append(f"references artifact {artifact}")

        for tech in context.technology_stack:
            if tech.lower() in knowledge.content.lower() or tech.lower() in knowledge.tags:
                score += 0.05
                reasons.append(f"matches tech {tech}")

        score += min(knowledge.usage_count * 0.01, 0.1)
        return min(score, 1.0), "; ".join(reasons)
