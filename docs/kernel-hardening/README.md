# Kernel Hardening Project

**Date:** 2026-07-02  
**Status:** Complete  
**Scope:** Final kernel architecture hardening before framework-to-product transition

---

## Mission

Eliminate remaining architectural debt so implementation faithfully obeys published constitutional architecture. No new features, redesign, or platform expansion.

---

## Success Criteria

| Criterion | Status |
|-----------|--------|
| `company_core` does not import `runtime_engine` | ✓ |
| Runtime exclusively owns `PipelineState` mutations | ✓ |
| Orchestrator uses Runtime mutation APIs | ✓ |
| Checkpoints persist under `.company/checkpoints/` | ✓ |
| `AgentInvocationFailed` emitted on adapter failure (orchestrator path) | ✓ |
| MCP health diagnostics tested | ✓ |
| All tests pass (142) | ✓ |

---

## Deliverables

| Report | Description |
|--------|-------------|
| [kernel-hardening-report.md](./kernel-hardening-report.md) | Executive summary |
| [dependency-purity-report.md](./dependency-purity-report.md) | Project 1 — Framework API decoupling |
| [runtime-boundary-report.md](./runtime-boundary-report.md) | Project 2 — Runtime ownership |
| [checkpoint-design.md](./checkpoint-design.md) | Project 3 — Persistence design |
| [checkpoint-migration.md](./checkpoint-migration.md) | Schema versioning and migration |
| [event-consistency-report.md](./event-consistency-report.md) | Failure event audit |
| [coverage-report.md](./coverage-report.md) | Test and coverage delta |
| [architecture-compliance-report.md](./architecture-compliance-report.md) | Constitutional compliance |

SDLC artifacts: [sdlc/](./sdlc/)

---

## Key Code Changes

| Area | Files |
|------|-------|
| Dependency purity | `company_core/ports/runtime_port.py`, `runtime_bridge.py`, `company_cli/runtime_bootstrap.py` |
| Runtime ownership | `runtime_engine/state/mutator.py`, `lifecycle.py` |
| Checkpoints | `orchestrator/checkpoint/store.py`, `checkpoint/manager.py` |
| Events | `orchestrator/execution/phase_executor.py` |
| Tests | `tests/kernel_hardening/`, `tests/mcp_platform/test_health.py` |
