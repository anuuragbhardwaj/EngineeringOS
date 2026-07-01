# Architecture Sync Report

**Date:** 2026-07-02  
**Purpose:** Synchronize architectural diagrams and layer descriptions with implemented code

---

## Authoritative Execution Stack

The implemented execution model (frozen architecture direction, now documented):

```
User / CEO
    │
    ▼
EngineeringOS CLI (engineeringos)
    │
    ▼
Framework API (company_core.FrameworkAPI)
    │
    ├── Autonomous Company Platform ── supervises full lifecycle
    │       │
    │       ▼
    ├── Workspace Execution ── session, context, resume
    │       │
    │       ▼
    └── Runtime (runtime_engine) ── lifecycle, gates, state, validation
            │
            ▼
        Orchestrator ── sequencing, context, prompts, policies
            │
            ├── Parallel Execution Engine (when policy enables)
            │
            ▼
        AI Execution Platform ── provider boundary
            │
            ▼
        Employees (content: .cursor/agents/, prompts)
```

### Supporting platforms (Framework API surface)

| Platform | Package | Role |
|----------|---------|------|
| Installation & Lifecycle | `company_lifecycle` | init, workspaces, projects, templates |
| Knowledge | `knowledge` | Durable engineering intelligence |
| Source Control | `source_control` | Git operations, EM-approved commit/push |
| MCP Platform | `mcp_platform` | Registry validation and resolution |
| Parallel Execution | `parallel_execution` | Dependency graphs, worker pools |
| Autonomous Company | `autonomous_company` | Goal-based autonomous pipelines |

---

## Diagram Updates Applied

### `docs/framework/system-context.md`

- C4 Level 2 containers expanded: orchestrator, ai_execution, lifecycle, workspace_execution, knowledge, source_control, parallel_execution, autonomous_company
- Execution data flow shows Orchestrator and AI Execution layers
- Trust boundaries unchanged

### `docs/framework/dependency-map.md`

- Package DAG includes all 11 Python packages
- Data flow: CLI → Framework API → platforms → Runtime → Orchestrator → AI Execution
- **Documented violation:** `company_core` imports `runtime_engine` via `ProjectAPI` (monorepo coupling)

### `docs/framework/package-architecture.md`

- Status column updated: Shipped / Partial / Planned per package
- Dependency graph reflects live imports

---

## Layer Mapping (L0–L7)

| Layer | Implemented components |
|-------|------------------------|
| L0 Contracts | `company.yaml`, `runtime/interfaces.md`, `workflow.yaml` |
| L1 Domain content | handbook, employees, workflow, mcp YAML |
| L2 Platform services | mcp_platform, company_lifecycle, knowledge, source_control, workspace_execution, parallel_execution, autonomous_company |
| L3 Runtime kernel | runtime_engine |
| L3b Orchestrator | orchestrator (approved extension) |
| L3c AI Execution | ai_execution (approved extension) |
| L4 Extensions | MCP servers (external), plugins (not wired) |
| L5 Integrations | `.cursor/agents/` (Cursor adapter, partial) |
| L6 Application | company_cli (`engineeringos`), company_core Framework API |
| L7 User space | workspaces/, projects/, `.company/` state |

---

## Sync Gaps Acknowledged (Not Redesigned)

| Gap | Documented in |
|-----|---------------|
| Orchestrator mutates `PipelineState` in-process | Known Limitations (README) |
| Checkpoint/approval state not fully persisted | Known Limitations |
| Four `discover_framework_root` heuristics | technical-debt.md |
| `register_plugin` not implemented | plugin-architecture.md |
| Documentation Platform — spec only, no package | README Partial |

---

## Contract Version Recommendation

Frozen documents updated to **v2.0.0 alignment (2026-07-02)**. A future **interfaces.md v1.1** minor bump should formally add orchestrator layer to §3 dependency diagram and document `execute_planning_pipeline`, `pause`, `resume`, `history` extensions — documentation action only, no behavioral change.
