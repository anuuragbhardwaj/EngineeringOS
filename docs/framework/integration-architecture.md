# Integration Architecture — AI Company Framework

**Version:** 2.0.0  
**Date:** 2026-07-01  
**Parent:** [framework-architecture.md](./framework-architecture.md)

---

## Principle

**Editors are adapters.** The framework core never imports Cursor, VS Code, or any IDE API. Integrations translate framework assets into editor-native conventions.

```
┌─────────────────────────────────────────────────────────┐
│                    Framework Core                        │
│  employees/  handbook/  workflow/  mcp/  manifest       │
└───────────────────────────┬─────────────────────────────┘
                            │ reads company.yaml
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ CursorAdapter│ │ VSCodeAdapter│ │  CLIAdapter  │
    │ integrations/│ │ integrations/│ │ company_cli  │
    │   /cursor    │ │   /vscode    │ │              │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
            ▼               ▼               ▼
       .cursor/          .vscode/         terminal
```

---

## Integration Interface (Conceptual)

Every editor integration implements:

| Capability | Description |
|------------|-------------|
| `discover_employees()` | Map `employees/` → editor agent format |
| `discover_mcp()` | Map `mcp.json` → editor MCP config |
| `sync()` | Write editor-specific files from manifest |
| `doctor()` | Verify integration health |
| `invoke_employee(id, context)` | Delegate to agent (editor-native) |

**Not standardized as code yet** — design contract for future `integrations/base.py`.

---

## Supported Editors

| Editor | ID | Status | Path |
|--------|-----|--------|------|
| **Cursor** | `cursor` | Active | `integrations/cursor/` |
| **VS Code** | `vscode` | Planned | `integrations/vscode/` |
| **Claude Code** | `claude-code` | Planned | `integrations/claude-code/` |
| **Roo Code** | `roo-code` | Planned | `integrations/roo-code/` |

All editors: `company install --editor <id>` / `company uninstall --editor <id>`

## Cursor Integration (Active)

| Framework | Cursor | Mechanism |
|-----------|--------|-----------|
| `employees/*.md` | `.cursor/agents/*.md` | Symlink or `company install --editor cursor` sync |
| `integrations/cursor/mcp.json` | `.cursor/mcp.json` | Symlink |
| Capabilities | MCP tools | User MCP + context7 plugin |
| EM orchestration | Cursor Task / agents | User invokes agents |

**Sync command (future):** `company install --editor cursor`

---

## VS Code Integration (Future)

| Framework | VS Code | Mechanism |
|-----------|---------|-----------|
| `employees/*.md` | Custom agent extension config | TBD — extension reads manifest |
| MCP | VS Code MCP support | `integrations/vscode/mcp.json` |
| Workflow | Status bar / webview | Dashboard plugin |

**Status:** Design placeholder. No implementation.

---

## Claude Code Integration (Planned)

| Framework | Claude Code | Mechanism |
|-----------|-------------|-----------|
| `employees/*.md` | Agent/skill definitions | `integrations/claude-code/` sync |
| MCP | Claude MCP config | Registry-driven `mcp.json` mirror |
| Workflow | Project context files | `company open` injects manifest paths |

**Status:** Adapter only — no framework logic in Claude Code config.

---

## Roo Code Integration (Planned)

| Framework | Roo Code | Mechanism |
|-----------|----------|-----------|
| `employees/*.md` | Custom modes / prompts | `integrations/roo-code/` sync |
| MCP | Roo MCP settings | Capability-resolved config |
| Handbook | Rules injection | Optional `.roo/rules` from handbook excerpts |

**Status:** Adapter only — follows same `IEditorIntegration` contract as Cursor.

---

## Future Editors

| Editor | Integration path |
|--------|------------------|
| JetBrains | `integrations/jetbrains/` |
| Neovim | `integrations/neovim/` |
| Web IDE | `integrations/web/` + cloud runtime |
| SDK-only | No editor — `company_cli` + `IAgentAdapter` |

Adding an editor = **new `integrations/<editor>/` module** — zero core changes.

---

## Agent Adapter vs Editor Integration

| Layer | Purpose |
|-------|---------|
| **Editor Integration** | IDE wiring — where agents live, MCP config |
| **Agent Adapter** (`IAgentAdapter`) | Runtime invocation boundary — kernel contract |

```
CLI/Runtime → IAgentAdapter → CursorSdkAdapter → Cursor API
Editor Integration → surfaces employees to user → user invokes
```

V1: Human-in-loop via editor. V2: `SdkAdapter` programmatic.

---

## MCP Integration

MCP is **not** part of kernel. Integration layer:

1. Reads `company.yaml` → `mcp.config`
2. Writes editor MCP config
3. MCP Platform validates separately (`mcp_platform validate`)

Employees request **capabilities** — integration does not hardcode MCP names.

---

## Configuration Flow

```
company.yaml
  → integrations.cursor.agents_path
  → integrations.cursor.mcp_path
       ↓
company install --editor cursor
       ↓
writes/symlinks .cursor/agents, .cursor/mcp.json
```

Workspace overrides: `workspaces/<ws>/integrations/cursor/` (future).

---

## Doctor Checks

| Check | Pass criteria |
|-------|---------------|
| Agents discoverable | 9 employees in editor |
| MCP synced | mcp.json matches registry installed entries |
| Manifest valid | company.yaml schema OK |
| Capability health | `mcp_platform health` PASS |

---

## References

- [ADR-0009](../adr/0009-editor-integrations.md)
- [ADR-0006](../adr/0006-framework-api.md)
- [mcp/configuration-guide.md](../../mcp/configuration-guide.md)
