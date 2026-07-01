# EngineeringOS Future Extension Readiness

**Date:** 2026-07-02  
**Question:** Can the current implementation naturally support future capabilities without architectural changes?

---

## Extension Readiness Score

# 7.8 / 10

The Orchestrator extraction and AI Execution Platform establish the **correct extension seams**. Future features should extend inward from those boundaries, not modify Runtime lifecycle internals.

---

## Capability Readiness Matrix

| Future capability | Ready? | Extension point | Architectural change needed? |
|-------------------|:------:|-----------------|:----------------------------:|
| **Memory** | **High** | Orchestrator `ContextEngine` + new memory provider feeding `AssembledContext` | No — add memory collector |
| **Metrics** | **High** | Orchestrator `HistoryRecorder`, AI Execution events, Runtime `EventBus` subscribers | No — subscribe/observe |
| **Cost optimization** | **High** | AI Execution `ExecutionPlatform` (provider selection, budget fields in `ExecutionPolicy`) | No — policy + platform |
| **Human approval (full)** | **Medium** | `approval/hooks.py` + Runtime pause; needs persistence | **Minor** — persist approval state |
| **Parallel execution** | **Medium** | `scheduler/`, `ExecutionState.parallel_tracks`, policy `parallel_ready` | **Minor** — scheduler + state rules |
| **Release Engineer** | **High** | New employee + phase executor; workflow phases 8–9 already defined | No — workflow extension |
| **Marketplace** | **Medium** | Provider registry plugin loading; employee package install | **Minor** — discovery mechanism |
| **Cloud** | **Medium** | `IAgentAdapter` network implementation; remote `ExecutionPlatform` | **Minor** — adapter transport |
| **VS Code** | **High** | `integration-architecture.md` — editor as adapter consuming Framework API | No — new L5 adapter |
| **GitHub** | **High** | CLI + GitHub Action calling `FrameworkAPI` / `engineeringos` | No — consumer |
| **Plugins** | **Low** | `IPlugin` defined; `register_plugin` not implemented | **Medium** — implement plugin host |
| **Employee packages** | **High** | `employee-registry.yaml` + `.cursor/agents/`; Orchestrator `PromptBuilder` | No — registry extension |
| **Project templates** | **High** | `templates/` content + `init` command | No — content + CLI |
| **MCP expansion** | **High** | `mcp_platform` + `capabilities.yaml` | No |
| **Distributed execution** | **Medium** | `dependency-map.md` already shows remote adapter | **Minor** — network adapter |

---

## Extension Seam Analysis

### Orchestrator as growth vector (Primary)

The following future capabilities **belong in Orchestrator**, not Runtime:

```
Memory          → context/engine.py collectors
Metrics         → history/recorder.py + exporters
Cost            → policy/engine.py budgets
Parallel tracks → scheduler/scheduler.py
Approval UI     → approval/hooks.py (Runtime only pauses)
Prompt variants → prompt_builder/builder.py
Employee routing→ scheduler/ + registry integration
```

**Evidence:** Mission statement and README already assign these responsibilities to Orchestrator. Implementation module layout matches.

### AI Execution as provider growth vector

```
New providers     → providers/*.py + registry
Cursor cloud API  → cursor.py implementation swap
Model routing     → capabilities.py + platform.py
Conversation sync → conversation/manager.py
```

**Evidence:** `IExecutionProvider` protocol, `ProviderRegistry`, placeholder pattern for unimplemented providers.

### Runtime should stay thin

Future capabilities that **must not** bloat Runtime:
- Prompt assembly ✓ (moved out)
- Employee sequencing ✓ (moved out)
- Provider calls ✓ (never in Runtime live path)

Runtime extensions that **are** appropriate:
- New gate types
- State schema migrations
- Additional validators (`IArtifactValidator`)
- Plugin event subscriptions (when implemented)

### Framework API as product growth vector

```
VS Code extension  → FrameworkAPI consumer
Cloud dashboard    → FrameworkAPI HTTP wrapper
SDK                → company_core public models + injected ports
Workspace UX       → WorkspaceAPI implementation (stub today)
```

---

## Blockers to Specific Extensions

### Plugins (Low readiness — score 3/10)

`register_plugin` raises `NotImplementedError`. `plugin-architecture.md` describes two-tier model but host not wired.

**Change required:** Implement plugin host in Runtime — **additive**, not rewrite.

### Durable Memory (Medium readiness)

`ContextEngine` is stateless per invocation. No vector store or cross-session memory.

**Change required:** New `memory/` module under Orchestrator + optional persistence — **additive**.

### Parallel Execution (Medium readiness)

`ExecutionState.parallel_tracks` exists in types. Scheduler runs sequentially. Policy has `parallel_ready` name but not enforced.

**Change required:** Scheduler enhancement + Orchestrator state mutation rules — **evolutionary**.

### Marketplace (Medium readiness)

Providers hardcoded in `ai_execution/factory.py`. Employees loaded from fixed paths.

**Change required:** Entry-point or YAML class-path discovery — **additive configuration layer**.

---

## What Would Force a Rewrite (None Identified for Listed Capabilities)

A rewrite would only be triggered if:
- Runtime re-absorbs orchestration (anti-pattern — avoided)
- Providers called directly from CLI or Runtime (anti-pattern — avoided)
- Single monolithic execution module without boundaries (avoided)

Current structure **does not** exhibit these failure modes.

---

## Extension Patterns Already Present

| Pattern | Location | Reuse for |
|---------|----------|-----------|
| Factory composition | `runtime_engine/factory.py` | Cloud worker factory variant |
| Protocol adapter | `IAgentAdapter`, `IExecutionProvider` | Remote providers |
| Event bus | `runtime_engine/events/` | Metrics, plugins |
| Registry YAML | `employee-registry.yaml`, `providers.yaml` | Employee marketplace |
| Policy YAML | `policies.yaml` | Cost, timeout, approval |
| Placeholder providers | `placeholders.py` | Gradual provider rollout |
| Stub APIs | `company_core/api/stubs.py` | Workspace, Employee, Integration |

---

## Recommended Extension Roadmap (Architecture-Preserving)

### Phase A — Observability (no contract break)
- Metrics exporter on Orchestrator history + AI Execution events
- Cost fields in execution records

### Phase B — Durability (minor contract bump)
- Persist checkpoints and approval in Runtime state store
- Conversation ID unification between Orchestrator router and AI Execution manager

### Phase C — Scale (scheduler evolution)
- Parallel track execution in Orchestrator scheduler
- Policy enforcement for timeout and MCP evidence

### Phase D — Ecosystem (additive)
- Plugin host implementation
- Provider/employee discovery from entry points
- WorkspaceAPI implementation

---

## Future Extension Readiness by Layer

| Layer | Score | Rationale |
|-------|:-----:|-----------|
| Orchestrator | **8.5** | Purpose-built for intelligence extensions |
| AI Execution | **8.0** | Clean provider boundary; needs plugin loading |
| Runtime | **7.5** | Stable lifecycle; plugin host missing |
| Framework API | **7.0** | Good facade; stubs need implementation |
| CLI | **8.0** | Thin; new commands easy |
| MCP Platform | **7.5** | Ready for more servers/capabilities |
| Documentation | **6.0** | Must sync before external extension authors rely on docs |

---

## Conclusion

> **Can future capabilities be added without architectural changes?**

**Yes, for the majority of listed capabilities** (Memory, Metrics, Cost, Release Engineer, Employee Packages, Templates, GitHub, VS Code, MCP).

**Minor additive changes** needed for: Plugins, Marketplace discovery, durable approval/checkpoints, parallel execution, cloud transport.

**No capability on the roadmap requires dismantling the Runtime → Orchestrator → AI Execution stack.**

The orchestrator extraction was the **load-bearing decision** that enables long-term evolvability. Future investment should flow into Orchestrator and AI Execution modules, not Runtime expansion.
