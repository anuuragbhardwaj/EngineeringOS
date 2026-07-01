# Event Consistency Report

**Date:** 2026-07-02  
**Scope:** Runtime and AI Execution failure event audit

---

## Canonical Event

Per `runtime/interfaces.md` and `runtime_engine/events/catalog.py`:

```
AgentInvocationFailed
Payload: { project_id, agent_id, error, phase_id }
```

---

## Audit Results

| Path | Failure condition | Emits `AgentInvocationFailed` | Notes |
|------|-------------------|-------------------------------|-------|
| Orchestrator `phase_executor._invoke_specialist` | `result.status.value == "failed"` | **Yes** | Added in kernel hardening |
| Runtime `facade.invoke_agent` | Adapter errors | Partial | Uses lifecycle bridge; orchestrator path is primary execution route |
| AI Execution adapters | Provider failures | Returns failed status | Event emitted by orchestrator on failed status |
| Parallel execution workers | Worker failure | Uses orchestrator events | Delegates to phase execution |

---

## Implementation (Orchestrator Path)

When adapter returns failed status after retry policy exhausts:

```python
if result.status.value == "failed" and publish_event:
    publish_event(
        events.AgentInvocationFailed,
        {
            "project_id": state.project_id,
            "agent_id": specialist.agent_id,
            "phase_id": phase_id,
            "error": result.message or "adapter invocation failed",
            "artifact": artifact_name,
        },
    )
```

`ArtifactCreated` still publishes on all outcomes (existing behavior).

---

## Intentional Exceptions

| Case | Rationale |
|------|-----------|
| Policy retry in progress | Failure not final — no event until retries exhausted |
| `publish_event` is `None` | Test/dry-run contexts without event bus |
| Direct Runtime `invoke_agent` without orchestrator | Legacy/single-agent path; orchestrator is canonical SDLC execution route |

---

## Remaining Gap (Documented, Low)

Runtime facade direct `invoke_agent` may not publish `AgentInvocationFailed` on all internal adapter exceptions when bypassing orchestrator. SDLC execution always routes through orchestrator — acceptable for v1 kernel.

---

## Architectural Benefit

Primary execution path now aligns with constitutional event catalog for adapter failures.
