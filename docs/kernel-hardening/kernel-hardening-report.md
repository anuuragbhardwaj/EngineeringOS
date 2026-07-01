# Kernel Hardening Report

**Date:** 2026-07-02  
**Project:** Final Kernel Hardening  
**Tests:** 142 passed (134 baseline + 8 new)

---

## Executive Summary

EngineeringOS completed its final kernel hardening pass. Three architectural debt items were resolved without redesigning the constitution:

1. **Dependency purity** — `company_core` no longer imports `runtime_engine`. Runtime is wired at the CLI composition root via `runtime_bridge`.
2. **Runtime ownership** — Orchestrator mutations flow through `PipelineStateMutator` exposed on `RuntimeLifecycleBridge`.
3. **Durable checkpoints** — Orchestrator checkpoints persist to `.company/checkpoints/orchestrator/{project_id}.yaml` with schema versioning.

Additional hardening: `AgentInvocationFailed` on orchestrator adapter failure; MCP health check test coverage.

---

## Objectives vs Outcomes

| Objective | Previous | New | Benefit |
|-----------|----------|-----|---------|
| Framework API purity | `ProjectAPI` imported `create_runtime` from `runtime_engine` | `IRuntimePort` + injected factory | L6 depends on contracts only |
| PipelineState ownership | Orchestrator mutated `state.*` directly | `PipelineStateMutator` API | Explicit Runtime boundary |
| Checkpoint durability | In-memory only | YAML under `.company/checkpoints/` | Survives process restart |
| Failure events | Gap in orchestrator path | `AgentInvocationFailed` published | Observability alignment |
| MCP diagnostics | Untested health paths | 4 health tests | Operational confidence |

---

## Compatibility Impact

- **Public APIs preserved:** `ProjectAPI`, `Runtime`, CLI commands unchanged in signature.
- **Behavior preserved:** Execution flows, artifact creation, planning pipeline semantics unchanged.
- **New requirement:** Non-CLI callers of `company_core` must call `configure_runtime_factory()` (tests use autouse fixture; CLI uses `runtime_bootstrap`).

---

## Non-Goals (Honored)

No marketplace, dashboard, cloud runtime, new platforms, package renames, or kernel redesign.

---

## References

- [dependency-purity-report.md](./dependency-purity-report.md)
- [runtime-boundary-report.md](./runtime-boundary-report.md)
- [checkpoint-design.md](./checkpoint-design.md)
- [architecture-compliance-report.md](./architecture-compliance-report.md)
