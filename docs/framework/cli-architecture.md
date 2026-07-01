# CLI Architecture — AI Company Framework

**Version:** 2.0.0  
**Date:** 2026-07-01  
**Status:** Design only — delegates to [framework-api.md](./framework-api.md)

---

## Purpose

The `company` CLI is a **thin facade** over the Framework API. No SDLc, gate, or validation logic in CLI code.

---

## Command Index

| Command | API | Purpose |
|---------|-----|---------|
| `company init` | CompanyAPI | Bootstrap company in directory |
| `company create` | CompanyAPI | Create named company instance |
| `company open` | CompanyAPI + WorkspaceAPI | Set active context |
| `company doctor` | CompanyAPI | Full health check |
| `company status` | CompanyAPI | Company/workspace/project summary |
| `company validate` | McpAPI + validators | Run all validations |
| `company upgrade` | CompanyAPI | Framework version upgrade |
| `company migrate` | CompanyAPI | Major version migration |
| `company install` | IntegrationAPI | Sync editor integration |
| `company uninstall` | IntegrationAPI | Remove editor integration |
| `company version` | CompanyAPI | Show version info |
| `company workspace create` | WorkspaceAPI | New workspace |
| `company workspace list` | WorkspaceAPI | List workspaces |
| `company project create` | ProjectAPI | New project |
| `company project list` | ProjectAPI | List projects |
| `company project archive` | ProjectAPI | Archive project |
| `company mcp list` | McpAPI | List MCPs/capabilities |
| `company mcp validate` | McpAPI | Registry validation |
| `company mcp doctor` | McpAPI | MCP health checks |
| `company employees` | EmployeeAPI | List employees + phases |

Runtime commands (`gate`, `advance`, `rework`, `release`, `close`) delegate to `IRuntime` when available.

---

## Commands (Detail)

### `company init [PATH]`

| | |
|--|--|
| **Purpose** | Initialize company in target directory |
| **Input** | Path (default `.`) |
| **Output** | `company.yaml`, `workspaces/` scaffold |
| **Behaviour** | Write manifest from template; do not overwrite existing |
| **Exit** | 0 success; 1 exists |

### `company create <instance-id>`

| | |
|--|--|
| **Purpose** | Create named company instance (multi-company) |
| **Input** | Instance id |
| **Output** | Instance at configured instances root |
| **Behaviour** | Distinct from `init` when using `~/.ai-company/instances/` layout |

### `company open [--workspace ID]`

| | |
|--|--|
| **Purpose** | Set active company/workspace context |
| **Output** | Context pointer for subsequent commands |

### `company doctor`

| | |
|--|--|
| **Purpose** | Comprehensive health report |
| **Checks** | Manifest, MCP, integrations, runtime, disk |
| **Exit** | 0 all pass |

### `company status [--json]`

| | |
|--|--|
| **Purpose** | Company + workspace + active project summary |
| **Output** | Phase, gate, blockers table or JSON |

### `company validate`

| | |
|--|--|
| **Purpose** | Full validation suite |
| **Delegates** | `mcp validate`, manifest schema, optional project validators |

### `company upgrade [--version VER]`

| | |
|--|--|
| **Purpose** | Upgrade framework pin |
| **Behaviour** | Fetch package; update manifest; post-hooks |

### `company migrate [--dry-run]`

| | |
|--|--|
| **Purpose** | Run migration scripts (major bumps) |
| **Output** | Migration report |

### `company install --editor <name>`

| | |
|--|--|
| **Purpose** | Sync integration for cursor, vscode, claude-code, roo-code |
| **Behaviour** | Symlink/copy per integration-architecture.md |

### `company uninstall --editor <name>`

| | |
|--|--|
| **Purpose** | Remove editor symlinks without deleting canonical employees |

### `company version`

| | |
|--|--|
| **Purpose** | Show framework, API, manifest, CLI versions |

### `company workspace create <id>`

| | |
|--|--|
| **Purpose** | Create workspace under company |
| **Output** | `workspaces/<id>/` + `.company/workspace.yaml` |

### `company workspace list`

| | |
|--|--|
| **Purpose** | List workspaces with project counts |

### `company project create <id>`

| | |
|--|--|
| **Purpose** | Scaffold project from template; init runtime state |
| **Output** | Phase 0 artifacts |

### `company project list`

| | |
|--|--|
| **Purpose** | List projects in active workspace with status |

### `company project archive <id>`

| | |
|--|--|
| **Purpose** | Close and archive project; state read-only |

### `company mcp list`

| | |
|--|--|
| **Purpose** | List registry MCPs and capabilities |
| **Output** | Table: id, category, installation_status |

### `company mcp validate`

| | |
|--|--|
| **Purpose** | Run `mcp_platform validate` |
| **Exit** | 0 pass |

### `company mcp doctor`

| | |
|--|--|
| **Purpose** | Health check installed MCPs |

### `company employees [--phase PHASE]`

| | |
|--|--|
| **Purpose** | List employees, roles, required capabilities |
| **Output** | Roster from manifest + employee-matrix |

---

## References

- [framework-api.md](./framework-api.md)
- [ADR-0010](../adr/0010-plugin-system.md) — CLI as facade (see 0006 in new set)
