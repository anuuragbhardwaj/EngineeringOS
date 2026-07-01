"""Knowledge resolver — resolves active context for retrieval."""

from __future__ import annotations

from pathlib import Path

from knowledge.types import RetrievalContext


class KnowledgeResolver:
    """Build retrieval context from execution session."""

    def resolve(
        self,
        instance_root: Path,
        *,
        workspace_id: str | None = None,
        project_id: str | None = None,
        employee_id: str | None = None,
        phase_id: str | None = None,
        artifacts: list[str] | None = None,
        company_id: str | None = None,
        max_items: int = 10,
        min_confidence: float = 0.3,
    ) -> RetrievalContext:
        resolved_workspace = workspace_id
        resolved_project = project_id
        resolved_company = company_id

        try:
            from workspace_execution.session.store import load_session

            session = load_session(instance_root)
            resolved_workspace = resolved_workspace or session.workspace_id
            resolved_project = resolved_project or session.project_id
            resolved_company = resolved_company or session.company_id
            employee_id = employee_id or session.current_employee
            phase_id = phase_id or session.current_phase
        except Exception:
            pass

        return RetrievalContext(
            company_id=resolved_company,
            workspace_id=resolved_workspace,
            project_id=resolved_project,
            employee_id=employee_id,
            phase_id=phase_id,
            artifacts=artifacts or [],
            max_items=max_items,
            min_confidence=min_confidence,
        )
