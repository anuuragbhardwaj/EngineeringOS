# Versioning Strategy — AI Company Framework

**Version:** 2.0.0  
**Date:** 2026-07-01  
**Parent:** [framework-architecture.md](./framework-architecture.md)

---

## Overview

The framework uses **independent semver tracks** per artifact class. No single global version covers all subsystems.

---

## Version Tracks

| Artifact | Field | Authority | Bump trigger |
|----------|-------|-----------|--------------|
| **Framework release** | `framework.version` | `company.yaml` | Structural change, employee roster, breaking path |
| **Company Instance** | `company.instance_version` | `company.yaml` | Operator config change |
| **Workspace** | `workspace.schema_version` | `.company/workspace.yaml` | Workspace layout change |
| **Project** | `project.workflow_version` | `.company-project.yaml` | Pinned workflow at creation |
| **Packages** | `pyproject.toml` version | Each package | Package API change |
| **Templates** | `templates.version` | manifest | Scaffold change |
| **Manifest schema** | `schema_version` | `company.yaml` | New manifest fields |
| **Workflow** | `workflow.version` | `workflow.yaml` | Phase/gate change |
| **Kernel contracts** | Contract version | `runtime/interfaces.md` | Public API change |
| **MCP registry** | `version` | `mcp/registry.yaml` | MCP catalog change |
| **Capabilities** | `version` | `mcp/capabilities.yaml` | Capability map change |
| **Generated state** | `schema_version` | `state.json` | PipelineState shape |
| **Integrations** | per package | `integrations/<editor>/` | Editor convention change |
| **Plugins** | `plugin.version` | Plugin metadata | Plugin API change |

---

## Semver Rules (Framework Release)

| Bump | Examples |
|------|----------|
| **MAJOR** | Remove employee; breaking manifest path; kernel contract major |
| **MINOR** | New employee; new MCP; additive manifest fields; new package |
| **PATCH** | Handbook typo; registry patch; doc fixes |

---

## Pinning Model

```yaml
# company.yaml
framework:
  version: "1.2.0"

# workspaces/default/.company/workspace.yaml
workspace:
  schema_version: "1.0"
  framework_pin: "1.2.0"

# projects/my-app/.company-project.yaml
project:
  workflow_version: "1.0"
  kernel_contract_version: "1.0.0"
  created_with_framework: "1.2.0"
```

**Rule:** Active projects **finish on pinned workflow**; new projects use latest compatible workflow.

---

## Upgrade Compatibility Matrix

| From → To | Auto? | Action |
|-----------|-------|--------|
| Framework patch | Yes | `company upgrade` |
| Framework minor | Yes | `company doctor` after upgrade |
| Framework major | No | `company migrate` |
| Kernel contract minor | Yes | Runtime handles optional fields |
| Kernel contract major | No | State migration + review |
| Workflow minor | New projects only | Existing projects unchanged |
| Workflow major | No | `company migrate --projects` |
| MCP registry minor | Yes | Validate only |
| Template minor | New scaffolds only | No retroactive change |

---

## Migration Strategy

### Framework Major Upgrade

1. `company doctor` — baseline
2. `company upgrade --version 2.0.0`
3. `company migrate --dry-run`
4. `company migrate`
5. `company doctor` — verify
6. Per-project: optional workflow migration or archive

### Project Migration

| Data | Strategy |
|------|----------|
| `state.json` | `schema_version` migration scripts in `runtime_engine` |
| Artifacts | Manual EM review if workflow phases change |
| Employee prompts | Automatic for new delegations only |
| MCP evidence | Re-validate if capability map changes |

### Rollback

- `company.yaml` framework pin revert
- Restore `state.json.bak` per project
- Git revert framework install

---

## Deprecation Policy

| Item | Notice | Removal |
|------|--------|---------|
| Manifest fields | 1 minor version deprecated flag | Next major |
| CLI commands | Alias with warning | 2 minors |
| Legacy paths (symlinks) | Documented in ADR-0006 | Framework v2.0.0 |
| Employees | Archive in `employees/deprecated/` | Major |

---

## Cloud / Multi-Instance (Future)

| Concern | Versioning |
|---------|------------|
| Remote runtime | `runtime.endpoint` + contract version negotiation |
| Shared state | `state.schema_version` + migration service |
| Company fleet | Central manifest registry with pinned versions |

No architectural change required — version fields already support negotiation.

---

## References

- [ADR-0006](../adr/0006-versioning-strategy.md)
- [lifecycle.md](./lifecycle.md) § Framework Upgrade
- [runtime/interfaces.md](../../runtime/interfaces.md) § Versioning
