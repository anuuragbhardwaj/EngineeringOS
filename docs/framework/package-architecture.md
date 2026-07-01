# Package Architecture — AI Company Framework

**Version:** 2.0.0  
**Date:** 2026-07-01  
**Parent:** [framework-architecture.md](./framework-architecture.md)

---

## Package Inventory

| Package | Status | Responsibility | Public Interface |
|---------|--------|----------------|------------------|
| `runtime_engine` | Planned | Company Kernel implementation | `runtime/interfaces.md` |
| `mcp_platform` | Shipped | MCP registry validation, resolution | CLI: `python -m mcp_platform` |
| `company_cli` | Planned | Operator CLI (`company` commands) | [cli-architecture.md](./cli-architecture.md) |
| `company_core` | Planned | Manifest loader, path resolution, shared models | Python API (future) |
| `validators` | Planned | Artifact validation beyond runtime | `IArtifactValidator` extensions |
| `templates` | Content | Scaffold files (not Python — directory) | Template manifest |
| `integrations` | Mixed | Editor configs (not pip packages) | Per-editor README |
| `employees` | Content | Agent prompts (not pip package) | Markdown files |
| `documentation` | Content | Handbook + framework docs | Markdown |

---

## Dependency Graph

```
company_cli
    ├── company_core
    ├── runtime_engine (optional — full orchestration)
    └── mcp_platform

runtime_engine
    ├── company_core (manifest paths only)
    └── [no editor, no MCP vendor imports]

mcp_platform
    └── company_core (optional — root discovery)

validators
    └── runtime_engine (IArtifactValidator)

plugins/*
    ├── runtime_engine (IPlugin — kernel tier)
    └── company_core (framework tier events)
```

**Rule:** `company_core` has zero dependencies on `runtime_engine`, editors, or MCP vendors.

---

## Package Specifications

### `company_core` (future)

| Attribute | Value |
|-----------|-------|
| **Responsibilities** | Load `company.yaml`; resolve paths; discover framework root; workspace/project models |
| **Dependencies** | PyYAML, pydantic |
| **Public API** | `CompanyManifest.load()`, `resolve_path(key)`, `Workspace.open()` |
| **Extension points** | Custom manifest validators |

### `runtime_engine` (future)

| Attribute | Value |
|-----------|-------|
| **Responsibilities** | Implement `IRuntime`, engines, state store, event bus |
| **Dependencies** | `company_core`, pydantic, typer (optional) |
| **Public API** | `runtime/interfaces.md` |
| **Extension points** | `IStateStore`, `IAgentAdapter`, `IPlugin`, `IArtifactValidator` |

### `mcp_platform` (current)

| Attribute | Value |
|-----------|-------|
| **Responsibilities** | Registry/capabilities load; validate; health; resolve |
| **Dependencies** | PyYAML |
| **Public API** | `mcp_platform.validate`, `resolve`, `health` CLI |
| **Extension points** | Custom registry schema rules (future) |

### `company_cli` (future)

| Attribute | Value |
|-----------|-------|
| **Responsibilities** | All `company` commands; user-facing orchestration |
| **Dependencies** | `company_core`, `mcp_platform`, typer, rich |
| **Public API** | CLI only — thin wrapper over libraries |
| **Extension points** | Plugin subcommands (future) |

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
├── runtime_engine/
├── mcp_platform/          # moved from root
├── validators/
└── plugins/               # optional bundled plugins
    ├── mcp_evidence/
    └── metrics/
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
