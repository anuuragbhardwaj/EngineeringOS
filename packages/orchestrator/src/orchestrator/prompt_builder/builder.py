"""Prompt Builder — deterministic prompt composition."""

from __future__ import annotations

from pathlib import Path

from orchestrator.types import AssembledContext


class PromptBuilder:
    """Loads employee prompt and injects context deterministically."""

    def __init__(self, framework_root: Path | None = None) -> None:
        self._framework_root = framework_root

    def build(
        self,
        context: AssembledContext,
        employee_prompt_path: str | None,
        delegation_brief: str,
    ) -> str:
        base_prompt = self._load_employee_prompt(
            context.employee_id, employee_prompt_path
        )
        sections = [
            "# Employee Role",
            base_prompt or f"Employee: {context.employee_role} ({context.employee_id})",
            "",
            "# Delegation Brief",
            delegation_brief,
            "",
            "# Project Context",
            f"Project: {context.project_metadata.get('name', context.project_id)}",
            f"Phase: {context.phase_id}",
            f"Deliverable: {context.deliverable}",
        ]

        if context.project_metadata.get("description"):
            sections.append(f"Description: {context.project_metadata['description']}")
        if context.workflow_state:
            sections.extend(["", "# Workflow State", self._format_dict(context.workflow_state)])

        if context.required_inputs:
            sections.extend(["", "# Required Inputs", ", ".join(context.required_inputs)])

        for name, content in context.artifacts.items():
            if name == context.deliverable:
                continue
            if content:
                sections.extend(["", f"# Artifact: {name}", content[:1500]])

        if context.execution_history:
            sections.extend(
                [
                    "",
                    "# Recent Execution History",
                    self._format_history(context.execution_history[-5:]),
                ]
            )

        if context.mcp_evidence:
            sections.extend(["", "# MCP Evidence Context", self._format_dict(context.mcp_evidence)])

        sections.extend(["", "# Instructions", f"Produce: {context.deliverable}"])
        return "\n".join(sections)

    def _load_employee_prompt(self, employee_id: str, prompt_path: str | None) -> str | None:
        if prompt_path and Path(prompt_path).is_file():
            return Path(prompt_path).read_text(encoding="utf-8")
        if self._framework_root:
            candidate = self._framework_root / ".cursor" / "agents" / f"{employee_id}.md"
            if candidate.is_file():
                return candidate.read_text(encoding="utf-8")
        return None

    def _format_dict(self, data: dict) -> str:
        return "\n".join(f"- {k}: {v}" for k, v in data.items())

    def _format_history(self, history: list[dict]) -> str:
        lines = []
        for entry in history:
            lines.append(
                f"- {entry.get('timestamp', '')} "
                f"{entry.get('specialist', entry.get('employee_id', ''))} "
                f"-> {entry.get('artifact', '')} [{entry.get('status', '')}]"
            )
        return "\n".join(lines) if lines else "None"
