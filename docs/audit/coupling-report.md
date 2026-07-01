# EngineeringOS Coupling Report

**Date:** 2026-07-02  
**Method:** Import tracing, shared-type analysis, private API usage, state ownership review

---

## Coupling Severity Scale

| Rank | Definition |
|------|------------|
| **Critical** | Breaks layer rules; blocks independent package evolution |
| **High** | Shared mutable state or private APIs; likely regression source |
| **Medium** | Duplication or implicit contracts; manageable with discipline |
| **Low** | Cosmetic or documentation-only; low maintenance risk |

---

## Critical Coupling Issues

### C-01: Framework API ↔ Runtime Engine (Critical)

**Location:** `company_core/api/project.py`

```python
from runtime_engine.factory import create_runtime
from runtime_engine.runtime.facade import Runtime
```

**Impact:** `company_core` cannot ship standalone. Violates frozen `package-architecture.md` rule. Any Runtime internal change ripples into Framework API.

**Future risk:** SDK consumers, VS Code extension, or cloud worker importing `company_core` alone will fail or drag full kernel.

**Mitigation (documented, not implemented):** Composition root creates Runtime; inject `ProjectRuntimePort` protocol into `ProjectAPI`.

---

### C-02: Orchestrator ↔ Runtime Types (Critical)

**Location:** `orchestrator/execution/phase_executor.py`, `pipeline_executor.py`

**Imports:** `AdapterStatus`, `ArtifactRecord`, `InvocationContext`, `PhaseStatus`, `ProjectStatus`, `AdapterInvocationError`

**Impact:** Orchestrator is not a pure downstream layer — it compiles against Runtime dataclass internals. Extracting Orchestrator to separate repo or versioning independently requires duplicating or sharing types.

**Mitigation:** `kernel_contracts` or `runtime_interfaces` package containing shared types and protocols only.

---

## High Coupling Issues

### H-01: Shared Mutable PipelineState (High)

**Parties:** `runtime_engine.Runtime`, `orchestrator.PhaseExecutor`, `orchestrator.PipelineExecutor`

Orchestrator directly mutates:
- `state.phase_status`
- `state.execution.*` (history, active_agent_id, pipeline_completed)
- `state.artifact_index`
- `state.status` (PAUSED)

Runtime persists the same object after Orchestrator returns.

**Risk:** No single owner for state invariants. Gate/validation engines assume Runtime owns mutations. Race conditions if parallel execution added later.

---

### H-02: RuntimeLifecycleBridge Private API Access (High)

**Location:** `runtime_engine/lifecycle.py`

Bridge calls via `# noqa: SLF001`:
- `runtime._persist`
- `runtime._validation`
- `runtime._gate`
- `runtime._pipeline`
- `runtime._bus`
- `runtime._workflow`
- `runtime._orchestrator.approval_hooks`

**Risk:** Refactoring Runtime internals breaks Orchestrator pipeline without compile-time warning.

---

### H-03: Duplicate IAgentAdapter Protocol (High)

**Locations:**
- `orchestrator/types.py` — `IAgentAdapter` with `Any` agent types
- `ai_execution/types.py` — `IAgentAdapter` Protocol

**Risk:** Signature drift between layers. Adapter implements one; Orchestrator types against another.

---

### H-04: Dual Conversation Routing (High)

**Parties:**
- `orchestrator/conversation/router.py` — assigns conversation IDs for execution metadata
- `ai_execution/conversation/manager.py` — persists messages and session state

**Risk:** IDs may diverge; reset in one layer may not propagate to other.

---

### H-05: ProjectAPI Private Store Access (High)

**Location:** `company_core/api/project.py` — `runtime._store.list_projects()`, `runtime._store.exists()`

**Risk:** State store implementation change breaks Framework API.

---

## Medium Coupling Issues

### M-01: Factory as God Composition Root (Medium)

**Location:** `runtime_engine/factory.py`

Single function wires: workflow loader, all engines, event bus, agent registry, AI adapter, orchestrator, runtime facade.

**Risk:** Testing subsets requires full stack. Alternative compositions (headless worker, cloud) must duplicate factory logic.

---

### M-02: Framework Root Discovery Duplication (Medium)

Four implementations with different heuristics:
- `company_core.config.loader`
- `runtime_engine.factory`
- `ai_execution.factory`
- `orchestrator.factory`

**Risk:** Package-relative config (`providers.yaml`, `policies.yaml`) resolves differently if heuristics diverge.

---

### M-03: History Aggregation in Runtime (Medium)

`Runtime.history()` merges:
- `state.transition_history`
- `state.gate_history`
- `state.execution.history` (runtime-appended by orchestrator)
- `orchestrator.get_execution_history()` (duplicate metadata)
- `orchestrator.get_checkpoints()`

**Risk:** Duplicate execution entries with different shapes (`employee_id` vs `specialist` alias added for compatibility).

---

### M-04: Scaffold Dual Implementation (Medium)

- `runtime_engine/adapters/scaffold.py` (dead)
- `ai_execution/providers/scaffold.py` (live)

**Risk:** Confusion for maintainers; accidental resurrection of wrong path.

---

### M-05: Event Catalog vs String Literals (Medium)

Orchestrator publishes events via callback with string literals; Runtime uses `events.catalog` constants.

**Risk:** Typo events; subscription mismatches.

---

### M-06: MCP Validation Dual Path (Medium)

`CompanyAPI.doctor()` and `FrameworkAPI.validate_all()` / `McpAPI.validate()` overlap.

---

## Low Coupling Issues

### L-01: CLI DTO Import from `api.project` (Low)

### L-02: `ExecutionPolicyName` enum unused (Low)

### L-03: History `specialist` compatibility alias (Low)

### L-04: `register_validator` write-only list (Low)

---

## Knowledge Duplication Matrix

| Knowledge | Locations | Severity |
|-----------|-----------|----------|
| Framework root discovery | 4 factories/loaders | Medium |
| Employee phase mapping | `employee-registry.yaml`, `PHASE_CAPABILITIES`, orchestrator scheduler | Medium |
| Artifact generation templates | `ai_execution/artifacts/generator.py`, provider classes | Low |
| Gate/event semantics | `workflow.yaml`, `gate/engine.py`, `lifecycle.py`, `facade.py` | Medium |
| Execution history shape | Runtime `execution.history`, `HistoryRecorder` | Medium |

---

## Hidden Assumptions

| Assumption | Where embedded | Risk if violated |
|------------|----------------|------------------|
| Monorepo single install | Root `pyproject.toml` only | Standalone packages break |
| Framework root = repo root | `company.yaml` `install_path: .` | Relocated framework fails |
| Planning pipeline only | `execute_planning_pipeline` stops at architecture | Full SDLC needs extension not rewrite |
| Single process | In-memory checkpoints/approval | Multi-process/cloud needs persistence |
| Scaffold/Cursor sufficient for CI | Tests use scaffold path | Production needs real providers |

---

## Coupling Risk Ranking (Top 10)

| Rank | ID | Issue | Severity |
|:----:|----|-------|----------|
| 1 | C-01 | `company_core → runtime_engine` | Critical |
| 2 | C-02 | Orchestrator imports Runtime types | Critical |
| 3 | H-01 | Shared mutable PipelineState | High |
| 4 | H-02 | LifecycleBridge private API | High |
| 5 | H-03 | Duplicate IAgentAdapter | High |
| 6 | H-04 | Dual conversation routing | High |
| 7 | H-05 | ProjectAPI `_store` access | High |
| 8 | M-02 | Four root discovery heuristics | Medium |
| 9 | M-01 | Monolithic factory | Medium |
| 10 | M-03 | Duplicate history records | Medium |

---

## Coupling Health Score

| Category | Score |
|----------|:-----:|
| Inter-package import discipline | 6.0/10 |
| State ownership clarity | 6.5/10 |
| Interface stability | 7.0/10 |
| Private API usage | 5.5/10 |
| **Overall coupling health** | **6.3/10** |

**Trend:** Improved vs pre-orchestrator (Runtime no longer invokes providers). Remaining coupling is **consolidatable** without architectural rewrite.
