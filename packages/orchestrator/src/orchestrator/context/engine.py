"""Context Engine — assembles normalized execution context."""

from __future__ import annotations

from pathlib import Path

from orchestrator.errors import ContextAssemblyError
from orchestrator.types import AssembledContext

ARTIFACT_PREVIEW_CHARS = 2000


class ContextEngine:
    """Collects project, workflow, artifacts, history, and MCP evidence."""

    def assemble(
        self,
        *,
        project_id: str,
        phase_id: str,
        employee_id: str,
        employee_role: str,
        artifact_root: str,
        project_metadata: dict,
        workflow_state: dict,
        required_inputs: list[str],
        deliverable: str,
        execution_history: list[dict],
        company_config: dict | None = None,
        mcp_evidence: dict | None = None,
        conversation_id: str | None = None,
        knowledge_snippets: dict[str, str] | None = None,
    ) -> AssembledContext:
        root = Path(artifact_root)
        if not root.is_absolute():
            root = root.resolve()

        artifacts = self._collect_artifacts(root, required_inputs + [deliverable])
        if deliverable and deliverable not in artifacts:
            artifacts[deliverable] = ""

        return AssembledContext(
            project_id=project_id,
            phase_id=phase_id,
            employee_id=employee_id,
            employee_role=employee_role,
            artifact_root=str(root),
            project_metadata=dict(project_metadata),
            workflow_state=dict(workflow_state),
            artifacts=artifacts,
            execution_history=list(execution_history),
            company_config=dict(company_config or {}),
            mcp_evidence=dict(mcp_evidence or {}),
            conversation_id=conversation_id,
            deliverable=deliverable,
            required_inputs=list(required_inputs),
            knowledge_snippets=dict(knowledge_snippets or {}),
        )

    def _collect_artifacts(self, root: Path, names: list[str]) -> dict[str, str]:
        collected: dict[str, str] = {}
        for name in names:
            if not name or name in collected:
                continue
            path = root / name
            if path.is_file():
                try:
                    content = path.read_text(encoding="utf-8")
                    collected[name] = content[:ARTIFACT_PREVIEW_CHARS]
                except OSError as exc:
                    raise ContextAssemblyError(f"Cannot read artifact {name}: {exc}") from exc
        return collected

    def compress(self, context: AssembledContext, max_chars: int) -> AssembledContext:
        """Truncate artifact previews for context size policy."""
        compressed = dict(context.artifacts)
        for name, content in compressed.items():
            if len(content) > max_chars // max(len(compressed), 1):
                limit = max_chars // max(len(compressed), 1)
                compressed[name] = content[:limit] + "\n...[truncated]"
        return AssembledContext(
            project_id=context.project_id,
            phase_id=context.phase_id,
            employee_id=context.employee_id,
            employee_role=context.employee_role,
            artifact_root=context.artifact_root,
            project_metadata=context.project_metadata,
            workflow_state=context.workflow_state,
            artifacts=compressed,
            execution_history=context.execution_history[-20:],
            company_config=context.company_config,
            mcp_evidence=context.mcp_evidence,
            conversation_id=context.conversation_id,
            deliverable=context.deliverable,
            required_inputs=context.required_inputs,
            knowledge_snippets=dict(context.knowledge_snippets),
        )
