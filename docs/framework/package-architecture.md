# Package Architecture — AI Company Framework

**Version:** 2.0.0 (alignment 2026-07-02)  
**Date:** 2026-07-01  
**Parent:** [framework-architecture.md](./framework-architecture.md)

---

## Package Inventory

| Package | Status | Responsibility | Public Interface |
|---------|--------|----------------|------------------|
| `company_core` | **Shipped** | Framework API, manifest, models | `FrameworkAPI`, `company_core.api.*` |
| `company_cli` | **Shipped** | Operator CLI (`engineeringos`) | [cli-architecture.md](./cli-architecture.md) |
| `company_lifecycle` | **Shipped** | Installation, workspaces, projects, templates | `company_lifecycle.platform` |
| `runtime_engine` | **Shipped** | Company Kernel — lifecycle, gates, state | `runtime/interfaces.md` |
| `orchestrator` | **Shipped** | Sequencing, context, prompts, policies | `orchestrator.orchestrator` |
| `ai_execution` | **Shipped** | Provider boundary, adapter | `ai_execution.platform` |
| `workspace_execution` | **Shipped** | Session, context, resume, history | `workspace_execution.platform` |
| `knowledge` | **Shipped** | Engineering intelligence store | `knowledge.platform` |
| `source_control` | **Shipped** | Git operations, release planning | `source_control.platform` |
| `parallel_execution` | **Shipped** | Concurrent scheduling, workers | `parallel_execution.platform` |
| `autonomous_company` | **Shipped** | Goal-based autonomous execution | `autonomous_company.platform` |
| `mcp_platform` | **Shipped** | MCP registry validation, resolution | CLI: `python -m mcp_platform` |
| `validators` | Planned | Artifact validation beyond runtime | `IArtifactValidator` extensions |
| `integrations` | Partial | Editor configs — `.cursor/agents/` only | Per-editor README |
| `employees` | Content | Agent prompts (not pip package) | Markdown in `.cursor/agents/` |
| `documentation` | Spec | Documentation Platform spec | `docs/documentation/` |

---

## Dependency Graph

```
engineeringos CLI (company_cli)
    └── company_core (FrameworkAPI)
            ├── company_lifecycle
            ├── workspace_execution
            ├── knowledge
            ├── source_control
            ├── parallel_execution
            ├── autonomous_company
            ├── mcp_platform
            └── project → runtime_engine (documented coupling)
                    └── orchestrator
                            ├── ai_execution
                            └── parallel_execution (policy-gated)
```

**Documented violation:** `company_core` imports `runtime_engine` via `ProjectAPI`. Original rule intended zero coupling; monorepo v1 accepts this. See [technical-debt.md](../audit/technical-debt.md).

**Rule (intent):** Domain packages MUST NOT import editor or MCP vendor SDKs.

---

## Package Specifications

### `company_core` (shipped)

| Attribute | Value |
|-----------|-------|
| **Responsibilities** | `FrameworkAPI` aggregate; manifest load/validate; path discovery |
| **Dependencies** | PyYAML; delegates to platform packages; **imports runtime_engine via ProjectAPI** |
| **Public API** | `FrameworkAPI`, `ManifestAPI`, platform API facades |
| **Extension points** | Custom manifest validators |

### `runtime_engine` (shipped)

| Attribute | Value |
|-----------|-------|
| **Responsibilities** | `IRuntime` facade; engines; state store; event bus; delegates pipeline to Orchestrator |
| **Dependencies** | `orchestrator`, `ai_execution` (factory composition) |
| **Public API** | `runtime/interfaces.md`, `create_runtime()` |
| **Extension points** | `IStateStore`, `IAgentAdapter`, `IPlugin`, `IArtifactValidator` |

### `orchestrator` (shipped)

| Attribute | Value |
|-----------|-------|
| **Responsibilities** | Context, prompts, policies, phase/pipeline execution, checkpoints |
| **Dependencies** | `runtime_engine.types`, `ai_execution` adapter |
| **Public API** | `create_orchestrator()`, `Orchestrator` |
| **Extension points** | Policy YAML, checkpoint hooks |

### `ai_execution` (shipped)

| Attribute | Value |
|-----------|-------|
| **Responsibilities** | Provider registry, capability routing, conversation persistence |
| **Dependencies** | None upstream of runtime/orchestrator |
| **Public API** | `ExecutionPlatform`, `RuntimeAgentAdapter` |
| **Extension points** | Provider implementations |

### `company_cli` (shipped)

| Attribute | Value |
|-----------|-------|
| **Responsibilities** | `engineeringos` commands; user-facing orchestration |
| **Dependencies** | `company_core` via `get_api()` only |
| **Public API** | CLI only — no SDLc logic in CLI code |
| **Extension points** | Command modules in `registry.py` |

### `validators` (future)

| Attribute | Value |
|-----------|-------|
| **Responsibilities** | Company artifact validators (idea, spec, tasks, etc.) |
| **Dependencies** | `runtime_engine` interfaces |
| **Public API** | `IArtifactValidator` implementations |
| **Extension points** | Register per artifact type |

---

## Content Packages (Non-Python)

| Directory | Treat as | Versioning |
|-----------|----------|------------|
| `employees/` | Framework content package | `framework.version` |
| `handbook/` | Framework content package | `framework.version` |
| `workflow/` | Framework content package | `workflow.version` |
| `mcp/` | Framework content package | `mcp/registry.yaml` version |
| `templates/` | Framework content package | `templates.version` |
| `integrations/` | Integration templates | Per editor |

---

## Monorepo Layout

```
packages/
├── company_core/
├── company_cli/
├── company_lifecycle/
├── runtime_engine/
├── orchestrator/
├── ai_execution/
├── workspace_execution/
├── knowledge/
├── source_control/
├── parallel_execution/
├── autonomous_company/
└── mcp_platform/          # also at repo root: mcp_platform/
```

`pyproject.toml` workspace root with `[tool.uv.workspace]` or poetry workspaces.

---

## Extension Points Summary

| Package | Extension | Mechanism |
|---------|-----------|-----------|
| runtime_engine | Storage | `IStateStore` |
| runtime_engine | Agents | `IAgentAdapter` |
| runtime_engine | Validation | `IArtifactValidator` |
| runtime_engine | Observability | `IPlugin` |
| mcp_platform | Registry rules | Validator plugins |
| company_cli | Commands | Entry points (future) |
| framework | Employees | Workspace `employees/` override |
| framework | Extensions | `extensions/` manifest |

---

## References

- [dependency-map.md](./dependency-map.md)
- [runtime/interfaces.md](../../runtime/interfaces.md)
