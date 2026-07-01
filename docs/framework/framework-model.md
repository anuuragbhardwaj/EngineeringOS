# Framework Model — AI Company Framework

**Version:** 2.0.0  
**Date:** 2026-07-01  
**Parent:** [framework-architecture.md](./framework-architecture.md)

---

## What the Framework Is

The **AI Company Framework** is a versioned, installable **AI Engineering operating system** — not a single project, not an IDE plugin, and not a runtime process. It is the immutable product that defines how software is delivered through a multi-agent SDLc.

| Is | Is Not |
|----|--------|
| Reusable delivery system | A user feature repository |
| Versioned release artifact | A workspace |
| Source of employees, workflow, contracts | An editor extension with business logic |
| Installable (git clone or pip) | Mutable by projects |

---

## Purpose

Provide a **portable, editor-independent** foundation for:

- 10-phase workflow-driven delivery
- Nine specialist employees (agents)
- Quality gates and handbook policies
- Company Kernel contracts
- MCP capability platform
- Extension via plugins and integrations

---

## Responsibilities

| Area | Responsibility |
|------|----------------|
| **SDLc** | Define phases, gates, artifacts, rework routing |
| **Governance** | Handbook standards, DoD, communication norms |
| **Agents** | Canonical employee prompts and roles |
| **Contracts** | `runtime/interfaces.md` — kernel public API |
| **Tools** | MCP registry, capabilities, policies |
| **Extension** | Plugin and integration contracts |
| **Packaging** | Installable Python packages, templates |
| **API** | Framework API for all consuming products |

---

## Public Interfaces

| Interface | Document | Consumers |
|-----------|----------|-----------|
| **Framework API** | [framework-api.md](./framework-api.md) | CLI, SDK, editors, cloud |
| **Kernel API** | `runtime/interfaces.md` | Runtime, plugins |
| **Manifest** | [company-manifest.md](../../company-manifest.md) | Bootstrapper, CLI |
| **MCP Platform** | `mcp/registry.yaml` | Employees, CLI |
| **Workflow** | `workflow.yaml` | Runtime |

---

## Boundaries

```
┌─────────────────────────────────────────┐
│           FRAMEWORK (immutable)          │
│  handbook │ employees │ workflow │ mcp   │
│  contracts │ packages │ templates       │
└──────────────────┬──────────────────────┘
                   │ consumed by, never modified by
                   ▼
┌─────────────────────────────────────────┐
│        COMPANY INSTANCE (configured)     │
└──────────────────┬──────────────────────┘
                   ▼
              WORKSPACES → PROJECTS
```

**Hard rules:**
1. Projects **never** modify framework files
2. Framework **never** stores user source code
3. Editors **never** contain framework business logic
4. All products consume **Framework API** — no bypass

---

## Versioning

| Track | Field | Bump |
|-------|-------|------|
| Framework release | `framework.version` | Semver — see [versioning-strategy.md](./versioning-strategy.md) |
| Kernel contracts | `interfaces.md` version | Independent semver |
| Workflow | `workflow.yaml` version | Phase/gate changes |
| MCP registry | `mcp/registry.yaml` version | Catalog changes |

---

## Upgrade Model

| Bump | Behaviour |
|------|-----------|
| Patch | Auto-compatible; `company upgrade` |
| Minor | Compatible; new templates/employees additive |
| Major | Requires `company migrate`; projects may pin old workflow |

Framework upgrades **do not** rewrite user project artifacts retroactively.

---

## Installation Model

| Method | Path | Use case |
|--------|------|----------|
| **Git clone** | Developer machine | Framework development |
| **pip install** | `site-packages` | Production (future meta-package) |
| **Embedded** | Monorepo submodule | Enterprise |

Post-install: `company init` creates Company Instance (not part of framework git).

---

## Configuration Model

Configuration layers (outer overrides inner):

1. Framework defaults (`company.yaml` schema defaults)
2. Company Instance (`company.yaml`)
3. Workspace (`workspaces/<id>/.company/workspace.yaml`)
4. Project (`projects/<id>/.company-project.yaml`)
5. User env (`~/.config/ai-company/`)

**Rule:** Configuration over hardcoding — all paths via manifest.

---

## Dependency Model

```
L0 Contracts → L1 Domain → L2 Platform → L3 Runtime → L4 Extensions
    → L5 Integrations → L6 Products → L7 User Space
```

See [dependency-map.md](./dependency-map.md). Framework core (L0–L2) has **zero** upward dependencies.

---

## How Products Consume the Framework

| Product | Consumption |
|---------|-------------|
| Company CLI | Framework API → libraries |
| Cursor / VS Code | Framework API → integration sync |
| SDK | Framework API → Python/TS bindings |
| Cloud | Framework API → remote services |
| Dashboard | Framework API → event stream |
| Marketplace | Framework API → plugin registry |

No product duplicates workflow, employee, or gate logic.

---

## Immutability

Between framework releases, these are **frozen**:

- Handbook policy content (patch excepted)
- Employee prompt content (per release)
- Kernel public contracts (per contract version)
- Workflow phase definitions (per workflow version)

User overrides live in **Company Instance** or **Workspace** — never in framework git.

---

## Extension Points

| Point | Mechanism |
|-------|-----------|
| Employees | Workspace `employees/` override |
| Validators | `IArtifactValidator` |
| Plugins | Kernel + Framework plugin tiers |
| MCP | Registry edit only |
| Templates | `templates/` versioned |
| Integrations | `integrations/<editor>/` |

---

## Persistence

| Asset | Location |
|-------|----------|
| Framework install | Git repo or pip package path |
| Not in framework | Workspace state, project code, user secrets |

---

## References

- [company-instance-model.md](./company-instance-model.md)
- [framework-api.md](./framework-api.md)
- [product-ecosystem.md](./product-ecosystem.md)
