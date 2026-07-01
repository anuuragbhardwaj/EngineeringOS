# Architecture Compliance Report

**Date:** 2026-07-02  
**References:** `runtime/interfaces.md`, `framework-api.md`, `package-architecture.md`, `dependency-map.md`, `system-context.md`

---

## Compliance Matrix

| Requirement | Document | Before | After |
|-------------|----------|--------|-------|
| Framework API depends on contracts only | `package-architecture.md` | ❌ `company_core → runtime_engine` | ✓ `IRuntimePort` + bridge |
| Runtime owns `PipelineState` | `runtime/interfaces.md` | ❌ Orchestrator direct mutation | ✓ `PipelineStateMutator` |
| CLI → Framework → Runtime chain | `system-context.md` | ✓ (with coupling) | ✓ (clean) |
| Orchestrator → Runtime types | `dependency-map.md` | ✓ | ✓ |
| Orchestrator → AI Execution | `dependency-map.md` | ✓ | ✓ |
| No layer bypass | `dependency-map.md` | Partial violation at L6→L3 | ✓ |
| Checkpoint durability | `workspace-model.md` | ❌ Ephemeral | ✓ `.company/checkpoints/` |
| `AgentInvocationFailed` on failure | `runtime/interfaces.md` | ❌ Orchestrator path | ✓ Orchestrator path |

---

## Dependency Chain Validation

```
CLI (company_cli)
  → runtime_bootstrap wires factory
  → company_core (Framework API, IRuntimePort)
  → runtime_engine (via injection, not import)
  → orchestrator
  → parallel_execution (policy-gated)
  → ai_execution
  → providers
```

Verified: no package bypasses an intermediate layer for its primary execution flow.

---

## Forbidden Dependencies (Re-checked)

| From | Rule | Status |
|------|------|--------|
| `company_core` | Must NOT import `runtime_engine` | ✓ Compliant |
| `mcp_platform` | Must NOT import `runtime_engine` | ✓ Unchanged |
| `orchestrator` | No direct provider SDKs | ✓ Unchanged |
| `ai_execution` | No orchestrator internals | ✓ Unchanged |

---

## Workspace State Consolidation

| Path | Owner | Status |
|------|-------|--------|
| `.company/state/` | Runtime/session | Existing |
| `.company/history/` | Execution log | Existing |
| `.company/knowledge/` | Knowledge platform | Existing |
| `.company/session/` | Session execution | Existing |
| `.company/checkpoints/orchestrator/` | Orchestrator | **New** |

No duplicate persistence systems introduced.

---

## Documentation Sync

Updated in this project:

- `docs/framework/dependency-map.md` — remove `CC --> RT` exception
- `README.md` — resolved limitations, test count
- `docs/kernel-hardening/*` — full hardening deliverables

Architecture documents were **not redesigned** — only clarified where implementation now matches published rules.

---

## Verdict

Implementation now obeys published constitutional architecture for the three primary debt items. Kernel is suitable for long-term evolution through packages, providers, and plugins without further kernel redesign.
