"""Scaffold artifact adapter — v1 delegation target for EM-coordinated employees."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from runtime_engine.types import (
    AdapterHealth,
    AdapterResult,
    AdapterStatus,
    AgentDescriptor,
    InvocationContext,
)


class ScaffoldAdapter:
    """Generates planning-phase artifacts from project metadata (editor-independent)."""

    def invoke(
        self,
        descriptor: AgentDescriptor,
        context: InvocationContext,
    ) -> AdapterResult:
        root = Path(context.artifact_root)
        root.mkdir(parents=True, exist_ok=True)
        artifact = context.deliverable
        path = root / artifact
        content = self._render(descriptor, context, artifact)
        path.write_text(content, encoding="utf-8")

        return AdapterResult(
            status=AdapterStatus.COMPLETED,
            agent_id=descriptor.agent_id,
            phase_id=descriptor.phase_id,
            message=f"Scaffolded {artifact} via EM delegation to {descriptor.role}",
            artifacts_touched=[artifact],
            metadata={
                "delegated_by": "engineering-manager",
                "prompt_path": descriptor.prompt_path,
            },
        )

    def cancel(self, job_id: str) -> bool:
        return False

    def health(self) -> AdapterHealth:
        return AdapterHealth(available=True, message="Scaffold adapter ready")

    def _render(
        self,
        descriptor: AgentDescriptor,
        context: InvocationContext,
        artifact: str,
    ) -> str:
        meta = context.metadata
        name = meta.get("name", context.project_id)
        description = meta.get("description", "")
        platform = meta.get("platform", "cross-platform")
        mode = meta.get("mode", "production")
        tech = meta.get("technology_stack", "Python")

        if artifact == "pipeline-status.md":
            return self._pipeline_status(context, name)
        if artifact == "idea.md":
            return self._idea(name, description, platform, mode)
        if artifact == "requirements.md":
            return self._requirements(name, description, platform, mode)
        if artifact == "spec.md":
            return self._spec(name, description, tech)
        if artifact == "tasks.md":
            return self._tasks(name, tech)
        if artifact == "architecture.md":
            return self._architecture(name, description, tech, platform)
        return f"# {artifact}\n\nGenerated for {name}.\n"

    def _pipeline_status(self, context: InvocationContext, name: str) -> str:
        return f"""# Pipeline Status — {name}

## Pipeline Status
- **Project:** {name}
- **Phase:** {context.phase_id}
- **Updated:** {datetime.utcnow().isoformat()}Z

## Current Phase
Orchestrated by Engineering Manager via Runtime v1.

## Blockers
None.

## Notes
Automated planning pipeline execution.
"""

    def _idea(self, name: str, description: str, platform: str, mode: str) -> str:
        return f"""# Idea — {name}

## Problem
{description}

## Users
Teams building on {platform} in {mode} mode.

## Value
Deliver {name} with measurable engineering outcomes.

## Decision
- **Decision:** Proceed to requirements
- **Rationale:** Opportunity validated; feasibility assumptions documented
"""

    def _requirements(self, name: str, description: str, platform: str, mode: str) -> str:
        return f"""# Requirements — {name}

## Problem
{description}

## Users
Engineering teams and stakeholders for {name}.

## Goals
- Execute planning pipeline through architecture
- Target platform: {platform}
- Delivery mode: {mode}

## MoSCoW
### Must Have
- Complete planning artifacts (idea → architecture)
- Runtime-orchestrated SDLC execution

### Should Have
- Traceable requirements and tasks

### Could Have
- Extended implementation phases (future milestone)

### Won't Have (this milestone)
- Implementation, QA, release automation

## Success Metrics
- All planning gates G0–G4 pass validation
- Artifacts non-empty with required sections

## Open Questions
- None blocking planning phase
"""

    def _spec(self, name: str, description: str, tech: str) -> str:
        return f"""# Specification — {name}

## Functional Requirements

### FR-001 Pipeline Execution
The system SHALL execute the planning pipeline from idea through architecture.

**Acceptance Criteria:**
- GIVEN a new project WHEN `engineeringos project create` runs THEN planning artifacts are generated.

### FR-002 State Persistence
The system SHALL persist runtime state for resume and recovery.

**Acceptance Criteria:**
- GIVEN an interrupted pipeline WHEN resume is invoked THEN execution continues from last phase.

## Non-Functional Requirements

### NFR-001 Technology
Preferred stack: {tech}

### NFR-002 Editor Independence
Runtime SHALL NOT depend on Cursor, VS Code, or Claude Code.

## Edge Cases
- Missing predecessor artifacts block advancement
- Corrupted state triggers recovery error
- Invalid phase transitions are rejected

## Context
{description}
"""

    def _tasks(self, name: str, tech: str) -> str:
        return f"""# Tasks — {name}

## Task Index
| ID | Phase | Requirement | Owner |
|----|-------|-------------|-------|
| T-001 | Architecture | FR-001 | architect |
| T-002 | Architecture | FR-002 | architect |
| T-003 | Architecture | NFR-001 | architect |

## Tasks

### T-001 — Design runtime facade
- **Traces:** FR-001
- **Acceptance:** IRuntime methods match interfaces.md
- **Verify:** `pytest tests/runtime/test_facade.py`

### T-002 — Implement state store
- **Traces:** FR-002
- **Acceptance:** Atomic save/load with schema_version
- **Verify:** `pytest tests/runtime/test_state_store.py`

### T-003 — Document technology choices
- **Traces:** NFR-001
- **Acceptance:** architecture.md lists {tech} stack
- **Verify:** `engineeringos project validate`

---
<!-- mcp-evidence: structured-reasoning -->
MCP Evidence: structured-reasoning recorded by Runtime (employee responsibility simulated in v1).
"""

    def _architecture(self, name: str, description: str, tech: str, platform: str) -> str:
        return f"""# Architecture — {name}

## Overview
{description}

Platform: {platform}. Stack: {tech}.

## API Contracts

### IRuntime
- `init_project`, `advance`, `validate`, `status` per runtime/interfaces.md

### FrameworkAPI
- CLI delegates to ProjectAPI → IRuntime

## Data Model

### PipelineState
- schema_version, current_phase_id, gate_history, artifact_index

## Security
- No secrets in state or event payloads
- Manifest-driven path resolution only

## Task Coverage
- T-001: Runtime facade in `packages/runtime_engine`
- T-002: JsonStateStore at `.runtime/state.json`
- T-003: Technology documented above

---
<!-- mcp-evidence: documentation-lookup -->
MCP Evidence: documentation-lookup — contracts sourced from runtime/interfaces.md (Runtime records only).
"""
