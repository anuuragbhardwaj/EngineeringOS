"""Build standardized ExecutionContext from Runtime invocation."""

from __future__ import annotations

import uuid
from typing import Any

from ai_execution.types import ExecutionContext, PHASE_CAPABILITIES


def build_execution_context(
    descriptor: Any,
    invocation_context: Any,
    *,
    workflow_state: dict | None = None,
    execution_history: list | None = None,
    company_config: dict | None = None,
    mcp_evidence: dict | None = None,
) -> ExecutionContext:
    meta = getattr(invocation_context, "metadata", {}) or {}
    assembled = meta.get("assembled_prompt")
    required_inputs = [
        ref.name for ref in getattr(invocation_context, "required_inputs", [])
    ]
    phase_id = getattr(invocation_context, "phase_id", "")

    return ExecutionContext(
        project_id=getattr(invocation_context, "project_id", ""),
        phase_id=phase_id,
        employee_id=getattr(descriptor, "agent_id", ""),
        employee_role=getattr(descriptor, "role", ""),
        artifact_root=getattr(invocation_context, "artifact_root", "."),
        deliverable=getattr(invocation_context, "deliverable", ""),
        delegation_brief=assembled or getattr(invocation_context, "delegation_brief", ""),
        project_metadata=dict(meta),
        workflow_state=workflow_state or {},
        required_inputs=required_inputs,
        artifact_paths=required_inputs,
        employee_prompt_path=getattr(descriptor, "prompt_path", None),
        employee_prompt=assembled,
        mcp_evidence=mcp_evidence or {},
        execution_history=execution_history or [],
        company_config=company_config or {},
        capabilities_required=list(PHASE_CAPABILITIES.get(phase_id, ["reasoning"])),
    )


def new_request_id() -> str:
    return str(uuid.uuid4())
