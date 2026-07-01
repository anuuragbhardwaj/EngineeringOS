# EngineeringOS Package Scorecard

**Date:** 2026-07-02  
**Scale:** 1 (poor) – 10 (excellent)  
**Verdict key:** Correct | Split | Merge | Simplify | Document

---

## Summary Table

| Package | SRP | Score | Verdict | Priority action |
|---------|:---:|:-----:|---------|-----------------|
| `company_core` | Partial | **6.5** | Simplify | Remove Runtime import; composition at CLI |
| `company_cli` | Yes | **8.5** | Correct | Minor DTO import cleanup |
| `runtime_engine` | Mostly | **7.5** | Simplify | Remove dead code; thin lifecycle only |
| `orchestrator` | Yes | **7.5** | Correct | Stop direct PipelineState mutation |
| `ai_execution` | Yes | **7.8** | Correct | Plugin registration from config |
| `mcp_platform` | Yes | **7.0** | Correct* | Move under `packages/`; add tests |
| Employees (content) | Yes | **8.0** | Correct | No change |
| Workflow (content) | Yes | **8.5** | Correct | No change |
| Handbook (content) | Yes | **8.0** | Correct | No change |
| Tests | Partial | **6.8** | Split | Add mcp_platform + company_core API suites |
| Documentation | Partial | **6.0** | Document | Sync constitutional docs with code |

\*Correct responsibility; placement anomaly only.

---

## `company_core` — Score: 6.5/10

### Single responsibility (intended)
Manifest loading, path resolution, domain models, Framework API aggregate.

### Hidden / leaked responsibilities
- **Runtime lifecycle owner** via `ProjectAPI._get_runtime()` and `create_runtime()`
- MCP validation duplicated in `CompanyAPI.doctor()` and `McpAPI.validate()`

### Duplicated responsibilities
- `discover_framework_root` (4 implementations across repo)
- Stub `ProjectAPI` in `stubs.py` vs real `project.py`

### Missing responsibilities
- Declared pip dependencies for actual imports
- Typed return models for `ProjectAPI.status()` / `resume()` (returns `object`)

### Recommendation: **Simplify**
Inject `IRuntime` factory at application composition root (`company_cli` or root factory). Keep `company_core` free of `runtime_engine` imports per frozen `package-architecture.md`.

---

## `company_cli` — Score: 8.5/10

### Single responsibility
Operator CLI; thin facade over Framework API.

### Strengths
- Dynamic command registry
- No bypass of Framework API
- Placeholder pattern for unimplemented commands
- `engineeringos` entry point wired correctly

### Issues
- Direct import of `ProjectCreateRequest` from `api.project` submodule
- No per-command unit tests (only shell/help/integration)
- Docs reference `company` binary; code uses `engineeringos`

### Recommendation: **Correct** — minor polish only.

---

## `runtime_engine` — Score: 7.5/10

### Single responsibility (intended)
Company Kernel — lifecycle, state, gates, validation, persistence, events.

### Correctly implemented
- `Runtime` facade with pipeline/gate/rework/validation engines
- `JsonStateStore`, event bus, workflow loader, agent registry
- Planning pipeline delegates to Orchestrator
- No live direct provider calls

### Leaked / residual
- `RuntimeLifecycleBridge` duplicates facade orchestration
- `history()` merges orchestrator data (aggregation OK; boundary blur)
- Factory composes Orchestrator + AI adapter (composition root — acceptable)

### Dead weight
- `agents/em_runner.py` — **unused**
- `adapters/scaffold.py` — **unused**
- `_validators_extra` — write-only list

### Recommendation: **Simplify** — delete dead modules; document factory as composition root.

---

## `orchestrator` — Score: 7.5/10

### Single responsibility
Operational intelligence — sequencing, context, prompts, policies, checkpoints, conversation, approval, history.

### Correctly implemented
- Full module structure per approved design
- Sole live `adapter.invoke()` path
- Deterministic prompt builder
- Config-driven policies (`policies.yaml`)
- No provider-specific imports

### Violations
- Direct `PipelineState` mutation (artifact_index, execution.history, phase_status)
- Imports `runtime_engine.types` / `errors` — couples to kernel implementation
- Checkpoint and approval state in-memory only
- Policy fields `timeout_seconds`, `mcp_evidence_required` not enforced

### Recommendation: **Correct** package split — harden boundaries via shared contracts and Runtime mutation callbacks.

---

## `ai_execution` — Score: 7.8/10

### Single responsibility
Provider execution boundary — registry, capabilities, conversation, platform.

### Correctly implemented
- `IExecutionProvider` protocol
- `ProviderRegistry` + `CapabilityResolver`
- `ExecutionPlatform` with retry/fallback
- `RuntimeAgentAdapter` as sole upward interface
- Placeholder providers for future expansion

### Gaps
- Hardcoded provider registration in `factory.py`
- `CursorProvider` is artifact scaffold + prompt load, not live Cursor API
- Dual fallback logic (resolver + platform)
- `providers.yaml` not at framework root

### Recommendation: **Correct** — evolve toward config-driven provider plugins without structural change.

---

## `mcp_platform` — Score: 7.0/10

### Single responsibility
MCP registry load, validate, resolve, health.

### Strengths
- Zero upstream package imports
- Lazy consumption from `company_core`
- CLI module entry (`python -m mcp_platform`)

### Issues
- Lives at **repo root**, not `packages/mcp_platform/`
- **Zero automated tests**
- `DEFAULT_ROOT` heuristic tied to root placement

### Recommendation: **Correct** responsibility — relocate for consistency OR document intentional root placement; add test suite.

---

## Content Packages (Non-Python)

### Employees (`.cursor/agents/`) — 8.0/10
10 specialist prompts + Engineering Manager. Loaded by Orchestrator `PromptBuilder` and `CursorProvider`. Aligned with `runtime/employee-registry.yaml`.

### Workflow (`workflow.yaml`) — 8.5/10
Canonical 11-phase definition. Runtime `WorkflowLoader` is exclusive consumer. Planning pipeline stops at architecture as designed.

### Handbook (`handbook/`) — 8.0/10
Content-only; no code imports. Supports governance narrative.

### Documentation (`docs/`) — 6.0/10
Good package-level READMEs; constitutional framework docs stale relative to orchestrator/ai_execution implementation.

---

## Subsystem Scores

| Subsystem | Score | Notes |
|-----------|:-----:|-------|
| Execution stack (RT→ORCH→AI) | **7.8** | Right shape; boundary leaks |
| Framework API | **6.5** | Works; violates own dependency rules |
| CLI surface | **8.5** | Clean |
| State & persistence | **7.5** | JSON store solid; orchestrator ephemeral state weak |
| Gate & validation | **8.0** | Engines match contract |
| Conversation lifecycle | **7.0** | AI Execution owns; dual routers (orch + platform) |
| Policy engine | **6.5** | Config exists; partial enforcement |
| Checkpoint system | **6.0** | In-memory; not durable |
| MCP integration | **7.0** | Functional; untested |
| Plugin system | **3.0** | `register_plugin` not implemented |
| Event bus | **7.5** | Works; some events missing per contract |

---

## Overall Package Architecture Score

**Weighted average: 7.4 / 10**

The package model is **sound**. No package should be merged or split for v1. Primary work is **boundary hardening and documentation sync**, not restructuring.
