# EngineeringOS Architecture Compliance Matrix

**Date:** 2026-07-02  
**Authority documents:**
- `runtime/interfaces.md` (Frozen v1.0.0)
- `docs/framework/framework-architecture.md`
- `docs/framework/package-architecture.md`
- `docs/framework/dependency-map.md`
- `docs/framework/cli-architecture.md`
- `docs/framework/framework-api.md`
- `docs/framework/integration-architecture.md`
- `docs/framework/plugin-architecture.md`

**Legend:** ✅ Compliant | ⚠️ Partial | ❌ Non-compliant | ➕ Extension (approved direction, not in frozen doc)

---

## Overall Architecture Compliance Score

# 7.2 / 10

Implementation follows **approved architectural direction** more closely than frozen documents currently describe. Primary gap is **documentation-contract lag**, not fundamental structural violation.

---

## Layer Compliance

| Layer | Documented | Implemented | Status |
|-------|------------|-------------|--------|
| L6 CLI | `company_cli` thin facade | `engineeringos` via Typer | ⚠️ Name differs (`company` vs `engineeringos`) |
| L5 Framework API | `company_core` zero runtime deps | `FrameworkAPI` + Runtime in `ProjectAPI` | ❌ Dependency violation |
| L3 Runtime Kernel | Lifecycle only | Mostly lifecycle; factory composes stack | ⚠️ |
| L3b Orchestrator | **Not in frozen docs** | Full package | ➕ Extension |
| L4 AI Execution | **Not in frozen docs** | Full package | ➕ Extension |
| L2 MCP Platform | `mcp_platform` | Root-level module | ⚠️ Placement |
| L1 Workflow/Employees | Content authority | `workflow.yaml`, `.cursor/agents/` | ✅ |
| L0 Contracts | `company.yaml`, interfaces.md | Present | ⚠️ interfaces.md stale |

---

## Dependency Rules Compliance

| Rule | Source | Status |
|------|--------|--------|
| CLI → Framework API only | cli-architecture.md | ✅ |
| Framework API → Runtime (not providers) | framework-api.md | ⚠️ Also imports Runtime concretely |
| Runtime → Orchestrator → AI Execution | Mission spec | ✅ |
| No provider SDKs in Runtime/Orchestrator | interfaces.md §3 | ✅ |
| `company_core` zero `runtime_engine` deps | package-architecture.md | ❌ |
| `mcp_platform` no `runtime_engine` | dependency-map.md | ✅ |
| Dependencies upward only | dependency-map.md | ❌ orchestrator → runtime_engine types |

---

## Runtime Responsibilities (`IRuntime` / interfaces.md §8)

| Responsibility | Owner | Status |
|----------------|-------|--------|
| Project lifecycle | Runtime | ✅ |
| State persistence | Runtime | ✅ |
| Gate evaluation | Runtime | ✅ |
| Phase advance | Runtime | ✅ |
| Artifact validation | Runtime | ✅ |
| Event bus | Runtime | ✅ |
| Workflow loading | Runtime | ✅ |
| Agent registry | Runtime | ✅ |
| Prompt assembly | Orchestrator | ✅ Moved correctly |
| Execution sequencing | Orchestrator | ✅ Moved correctly |
| Conversation routing | Orchestrator (+ AI Execution persist) | ⚠️ Dual |
| Provider execution | AI Execution | ✅ |
| `execute_planning_pipeline` | Runtime facade delegates | ➕ Not in §8.2 |
| `pause` / `resume` / `history` | Runtime facade | ➕ Not in §8.2 |
| `register_plugin` | Specified | ❌ NotImplementedError |

---

## Orchestrator Responsibilities (Mission Spec)

| Responsibility | Implemented | Status |
|----------------|:-------------:|--------|
| Execution sequencing | `pipeline_executor`, `scheduler` | ✅ |
| Employee scheduling | `scheduler` | ✅ |
| Context assembly | `context/engine` | ✅ |
| Artifact injection | via context | ✅ |
| Prompt assembly | `prompt_builder` | ✅ |
| Execution policies | `policy/engine` | ⚠️ Partial enforcement |
| Conversation routing | `conversation/router` | ✅ |
| Execution checkpoints | `checkpoint/manager` | ⚠️ In-memory only |
| Retry decisions | `policy` + phase executor | ✅ |
| Failure routing | pipeline raises | ⚠️ No failure events |
| Pipeline continuation | `pipeline_executor` | ✅ |
| Human approval pauses | `approval/hooks` | ⚠️ Not persisted |
| Execution history | `history/recorder` | ✅ |
| Execution logs | history + runtime history | ⚠️ Duplicate |
| Context compression | `context/engine.compress` | ✅ |
| Prompt composition | `prompt_builder` | ✅ |
| Execution metadata | history records | ✅ |
| Workflow definition | Runtime | ✅ Not in Orchestrator |
| State persistence | Runtime | ✅ Not in Orchestrator |
| Provider execution | AI Execution | ✅ Not in Orchestrator |
| MCP execution | MCP Platform external | ✅ Not in Orchestrator |
| Filesystem (state) | Runtime store | ✅ |

---

## AI Execution Platform Compliance

| Requirement | Status |
|-------------|--------|
| Sole provider boundary | ✅ |
| `IExecutionProvider` abstraction | ✅ |
| Provider registry | ✅ |
| Capability-based routing | ✅ |
| Conversation manager | ✅ |
| Runtime adapter anti-corruption | ✅ |
| No Orchestrator imports | ✅ |
| Config-driven provider registration | ❌ Hardcoded in factory |
| Real AI providers | ⚠️ Scaffold + prompt-load Cursor only |

---

## Framework API Compliance (framework-api.md)

| API | Spec | Implementation | Status |
|-----|------|----------------|--------|
| `FrameworkAPI` aggregate | Required | Present | ✅ |
| `ManifestAPI` | Required | Implemented | ✅ |
| `CompanyAPI` | Required | Partial | ⚠️ |
| `ProjectAPI` | Required | Implemented via Runtime | ⚠️ Leaks Runtime type |
| `WorkspaceAPI` | Required | Stub | ⚠️ Expected v1 gap |
| `McpAPI` | Required | Implemented | ✅ |
| `EmployeeAPI` | Required | Stub | ⚠️ |
| `IntegrationAPI` | Required | Stub | ⚠️ |
| Single consumption path | Required | CLI uses it | ✅ |
| Doc status "not implemented" | — | Code exists | ❌ Doc stale |

---

## CLI Compliance (cli-architecture.md)

| Requirement | Status |
|-------------|--------|
| Thin wrapper | ✅ |
| No business logic in commands | ✅ |
| Dynamic command registry | ✅ |
| Maps to Framework API | ✅ |
| `company` binary name | ❌ Uses `engineeringos` |
| Project commands via `IRuntime` | ✅ Via ProjectAPI |
| Doctor/status/validate | ✅ |

---

## Integration Architecture Compliance

| Rule | Status |
|------|--------|
| Framework never imports IDE APIs | ✅ |
| Editors are adapters | ✅ (content in `.cursor/`) |
| Employee prompts editor-independent | ✅ Markdown in `.cursor/agents/` |

---

## Plugin Architecture Compliance

| Tier | Status |
|------|--------|
| Kernel `IPlugin` interface | ⚠️ Defined; host not implemented |
| Framework `IFrameworkPlugin` | ⚠️ Documented only |
| Plugins extend, never modify core | ✅ Design honored |
| Event-only plugin communication | ✅ No plugin code yet |

---

## State Model Compliance (interfaces.md §6)

| Element | Status |
|---------|--------|
| `PipelineState` structure | ✅ |
| `ExecutionState.history` | ✅ |
| `ExecutionState.parallel_tracks` | ➕ Field exists; unused |
| `ProjectStatus.PAUSED` | ➕ Extension beyond enum |
| `pipeline_completed` / `pipeline_stop_phase` | ➕ Extension |
| JSON persistence | ✅ |
| Schema version | ✅ `SCHEMA_VERSION` |

---

## Event Catalog Compliance (interfaces.md §19)

| Event | Required emitter | Status |
|-------|------------------|--------|
| `ProjectCreated` | IRuntime | ✅ |
| `PhaseEntered` / `PhaseCompleted` | IRuntime | ✅ |
| `GatePassed` / `GateRejected` | IRuntime | ✅ |
| `ArtifactCreated` | Orchestrator via callback | ⚠️ Path differs |
| `AgentInvoked` | IRuntime per table | ⚠️ Not consistently emitted |
| `AgentInvocationFailed` | IRuntime | ❌ Not emitted |
| `StateSaved` | IRuntime | ✅ |

---

## Workflow & Gate Compliance

| Requirement | Status |
|-------------|--------|
| `workflow.yaml` exclusive phase source | ✅ |
| Gate engine evaluates per workflow | ✅ |
| Planning stop at architecture | ✅ By design |
| G0–G4 in planning path | ✅ |
| User approval at G0 | ⚠️ Policy disabled for automation |

---

## Employee System Compliance

| Requirement | Status |
|-------------|--------|
| Registry in `runtime/employee-registry.yaml` | ✅ |
| 10 employee prompts | ✅ |
| EM as orchestrator employee | ✅ |
| Phase owner resolution | ✅ via `AgentRegistry` |
| Orchestrator schedules specialists | ✅ |

---

## MCP Platform Compliance

| Requirement | Status |
|-------------|--------|
| Registry load/validate | ✅ |
| Capability resolution | ✅ |
| Health checks | ✅ |
| No runtime coupling | ✅ |
| Under `packages/` per doc | ❌ Root placement |
| Tested | ❌ |

---

## Test Architecture Compliance

| Requirement | Status |
|-------------|--------|
| Runtime tests | ✅ |
| Orchestrator tests | ✅ |
| AI Execution tests | ✅ |
| CLI smoke tests | ✅ |
| Integration E2E | ✅ |
| MCP tests | ❌ |
| Framework API unit tests | ⚠️ Minimal |
| Contract conformance tests | ❌ No interfaces.md contract test suite |

---

## Compliance Summary by Document

| Document | Compliance | Primary gap |
|----------|:----------:|-------------|
| `runtime/interfaces.md` | **65%** | Missing orchestrator; extensions; events |
| `package-architecture.md` | **55%** | Status stale; missing packages; core dep rule |
| `dependency-map.md` | **60%** | DAG incomplete; core→runtime violation in code |
| `framework-api.md` | **70%** | Implemented but doc says otherwise; stubs |
| `cli-architecture.md` | **85%** | Binary naming |
| `integration-architecture.md` | **90%** | Aligned |
| `plugin-architecture.md` | **40%** | Not implemented |
| Mission orchestrator spec | **85%** | State mutation; policy enforcement gaps |

---

## Scoring Summary

| Dimension | Score |
|-----------|:-----:|
| **Overall Architecture Compliance** | **7.2** |
| **Overall Maintainability** | **7.5** |
| **Overall Extensibility** | **7.8** |
| **Overall Technical Debt** | **6.5** (inverse: lower debt = higher) |
| **Overall Release Readiness** | **7.0** |

---

## Compliance Verdict

The implementation is **substantially compliant with the approved EngineeringOS direction** established by the Orchestrator mission and the three-layer execution model. It is **partially compliant with frozen constitutional documents** that predate Orchestrator and AI Execution Platform shipping.

**For public release:** Treat compliance as **7.2/10 — good with documented exceptions**.

**For constitutional freeze:** Require contract version bump (v1.1 or v2.0) synchronizing `interfaces.md`, `package-architecture.md`, and `dependency-map.md` with implemented reality — **documentation action, not rewrite**.
