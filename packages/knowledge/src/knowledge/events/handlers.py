"""Event bus integration for knowledge capture."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from knowledge.engine.engine import KnowledgeEngine
from knowledge.types import KnowledgeScope


class KnowledgeEventHandler:
    """Subscribe to kernel events and capture engineering knowledge."""

    HANDLED_EVENTS = {
        "PhaseCompleted",
        "ReviewApproved",
        "QAFailed",
        "DocumentationGenerated",
        "ReleaseCreated",
        "ProjectClosed",
        "ArtifactValidated",
        "ProjectCreated",
    }

    def __init__(self, engine: KnowledgeEngine | None = None) -> None:
        self._engine = engine or KnowledgeEngine()

    def handle(self, instance_root: Path, event_type: str, payload: dict[str, Any]) -> KnowledgeEngine:
        if event_type not in self.HANDLED_EVENTS:
            return self._engine
        return self._dispatch(instance_root, event_type, payload)

    def subscribe_runtime(self, runtime: Any, instance_root: Path) -> list[str]:
        """Subscribe to runtime EventBus — returns subscription IDs."""
        ids: list[str] = []
        for event_type in self.HANDLED_EVENTS:
            sub_id = runtime.subscribe(
                event_type,
                lambda event, et=event_type: self.handle(
                    instance_root, et, dict(event.payload or {})
                ),
            )
            ids.append(sub_id)
        return ids

    def _dispatch(self, instance_root: Path, event_type: str, payload: dict[str, Any]) -> KnowledgeEngine:
        project_id = payload.get("project_id")
        phase_id = payload.get("phase_id")
        employee_id = payload.get("employee_id") or payload.get("agent_id")

        if event_type == "PhaseCompleted":
            self._engine.capture(
                instance_root,
                title=f"Phase completed: {phase_id}",
                content=f"Phase {phase_id} completed for project {project_id}.",
                origin=event_type,
                owner=employee_id or "orchestrator",
                reason="Automatic capture from phase completion",
                knowledge_type="implementation_note",
                scope=KnowledgeScope.PROJECT.value,
                project_id=project_id,
                employee_id=employee_id,
                confidence=0.6,
                auto_activate=True,
            )
        elif event_type == "QAFailed":
            self._engine.capture(
                instance_root,
                title=f"QA failure in {phase_id or project_id}",
                content=str(payload.get("detail") or payload.get("message") or "QA failed"),
                origin=event_type,
                owner=employee_id or "qa-engineer",
                reason="QA failure recorded for future prevention",
                knowledge_type="qa_finding",
                scope=KnowledgeScope.PROJECT.value,
                project_id=project_id,
                confidence=0.75,
            )
        elif event_type == "ReviewApproved":
            self._engine.capture(
                instance_root,
                title=f"Review approved: {phase_id or project_id}",
                content=str(payload.get("summary") or "Review gate passed"),
                origin=event_type,
                owner="engineering-manager",
                reason="Review approval captured",
                knowledge_type="review_finding",
                scope=KnowledgeScope.PROJECT.value,
                project_id=project_id,
                confidence=0.8,
                auto_activate=True,
            )
        elif event_type == "ProjectCreated":
            self._engine.capture(
                instance_root,
                title=f"Project created: {project_id}",
                content=str(payload.get("description") or f"Project {project_id} initialized"),
                origin=event_type,
                owner="engineering-manager",
                reason="Project initialization knowledge",
                knowledge_type="fact",
                scope=KnowledgeScope.PROJECT.value,
                project_id=project_id,
                confidence=0.7,
                auto_activate=True,
            )
        elif event_type in ("DocumentationGenerated", "ReleaseCreated", "ProjectClosed", "ArtifactValidated"):
            self._engine.capture(
                instance_root,
                title=f"{event_type}: {project_id or 'company'}",
                content=str(payload),
                origin=event_type,
                owner=employee_id or "system",
                reason=f"Captured from {event_type}",
                knowledge_type="fact",
                scope=KnowledgeScope.PROJECT.value if project_id else KnowledgeScope.COMPANY.value,
                project_id=project_id,
                confidence=0.55,
            )
        return self._engine

    def make_handler(self, instance_root: Path) -> Callable[[str, dict], None]:
        def handler(event_type: str, payload: dict) -> None:
            self.handle(instance_root, event_type, payload)

        return handler
