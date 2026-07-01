# Domain Model — AI Company Framework

**Version:** 2.0.0  
**Date:** 2026-07-01  
**Parent:** [framework-architecture.md](./framework-architecture.md)

---

## Overview

This document defines **20 core concepts** with purpose, ownership, lifecycle, responsibilities, relationships, versioning, persistence, **configuration**, and **extension points**.

### Concept Relationship Diagram

```mermaid
erDiagram
    Framework ||--o{ CompanyInstance : "installed as"
    CompanyInstance ||--o{ Workspace : contains
    Workspace ||--o{ Project : hosts
    Project ||--o{ Artifact : produces
    Project }o--|| Workflow : follows
    Project }o--o{ Employee : delegates
    Framework ||--o{ Package : ships
    Framework ||--o{ Template : provides
    Framework ||--|| Manifest : described_by
    CompanyInstance ||--|| Manifest : configures
    Runtime ||--o{ Project : orchestrates
    MCPPlatform ||--o{ Capability : exposes
    Employee }o--o{ Capability : requests
    Integration ||--o{ Employee : surfaces
    CLI }o-- FrameworkAPI : consumes
    FrameworkAPI ||--o{ Product : serves
    Plugin }o-- Runtime : extends
    Extension }o-- Framework : extends
    Tool }o-- MCPPlatform : resolves_to
```

---

## 1. Framework

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Reusable, versioned delivery system: SDLc, employees, handbook, contracts, MCP platform, packages |
| **Ownership** | Framework maintainers; immutable between patch releases |
| **Lifecycle** | Released → installed → upgraded → deprecated |
| **Responsibilities** | Define workflow, agents, policies, kernel contracts, extension points |
| **Relationships** | Installed into host; configured by Company Instance; contains Packages |
| **Versioning** | Semver `framework.version` in manifest |
| **Persistence** | Git repository or pip-installed package on disk |
| **Configuration** | `framework.yaml` defaults; env `AI_COMPANY_*`; not user-editable in place |
| **Extension Points** | Packages, templates, `IFrameworkPlugin`, manifest schema fields |

**Not:** A single user project. Not workspace content. **Immutable** — projects never modify framework files.

---

## 2. Company Instance

| Attribute | Definition |
|-----------|------------|
| **Purpose** | A **configured deployment** of the Framework — enables multiple independent "companies" on one machine |
| **Ownership** | Company operator (user or organization) |
| **Lifecycle** | Created → configured → active → upgraded → archived |
| **Responsibilities** | Pin framework version; hold `company.yaml`; scope workspaces |
| **Relationships** | 1 Framework version : N Company Instances; 1 Instance : N Workspaces |
| **Versioning** | `company.instance_version` in manifest (independent of framework) |
| **Persistence** | `company.yaml` + optional `company.lock` at instance root |
| **Configuration** | `company.yaml` — paths, pins, integrations, plugins, MCP profiles |
| **Extension Points** | `extensions:`, `plugins:`, employee overrides path, custom templates |

**Distinction from Framework:** Framework is the **product**; Company Instance is a **deployment configuration**. The default dev setup is one instance co-located with the framework repo.

---

## 3. Workspace

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Isolated environment for user work — projects, local state, user assets |
| **Ownership** | User / team |
| **Lifecycle** | Initialized → active → archived → deleted |
| **Responsibilities** | Contain projects; isolate generated artifacts from framework |
| **Relationships** | Belongs to Company Instance; contains N Projects |
| **Versioning** | `workspace.schema_version` in `.company/workspace.yaml` |
| **Persistence** | `workspaces/<workspace-id>/` — default gitignored from framework repo |

See [workspace-model.md](./workspace-model.md).

---

## 4. Project

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Single SDLc execution unit — one feature, product, or infrastructure initiative |
| **Ownership** | Engineering Manager (orchestration) + phase owners |
| **Lifecycle** | Created → active (phases 0–9) → completed → archived |
| **Responsibilities** | Produce phase artifacts; pass gates G0–G9 |
| **Relationships** | Lives in Workspace; follows Workflow; uses Employees; orchestrated by Runtime |
| **Versioning** | `project.workflow_version` pinned from framework |
| **Persistence** | `workspaces/<ws>/projects/<project-id>/` |

---

## 5. Employee

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Specialist agent role — PM, BA, Planner, Architect, implementers, QA, Reviewer, EM |
| **Ownership** | Framework (prompt content); user may override in workspace |
| **Lifecycle** | Defined in framework release; upgraded with framework |
| **Responsibilities** | Produce phase-owned artifacts; request capabilities; STOP when blocked |
| **Relationships** | Assigned per Workflow phase; invoked via Integration or CLI |
| **Versioning** | Tied to `framework.version`; workspace overrides versioned separately |
| **Persistence** | `employees/<agent-id>.md` (framework); optional `workspaces/<ws>/employees/` overrides |

**Not:** MCP servers. Not runtime code.

---

## 6. Artifact

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Deliverable output of a pipeline phase (markdown, code, reports) |
| **Ownership** | Phase owner per workflow (see handbook) |
| **Lifecycle** | Created → validated → gate passed → immutable for phase → rework may revise |
| **Responsibilities** | Satisfy exit criteria; traceable to spec |
| **Relationships** | Belongs to Project; validated by Runtime; may reference MCP evidence |
| **Versioning** | Content versioning via git; schema per artifact type in workflow |
| **Persistence** | Project artifact root (default: project directory) |

**Classes:** Phase artifacts (idea.md…closure.md), implementation (source), generated (pipeline state, events).

---

## 7. Workflow

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Canonical 10-phase SDLc — phases, gates, owners, transitions, rework routing |
| **Ownership** | Framework |
| **Lifecycle** | Versioned releases; projects pin to workflow version |
| **Responsibilities** | Single source of truth for pipeline; no hardcoded phases in runtime |
| **Relationships** | Loaded by Runtime via WorkflowLoader; referenced by handbook |
| **Versioning** | `workflow.yaml` `version` field |
| **Persistence** | `workflow/workflow.yaml`, `workflow/workflow-v1.md` |

---

## 8. Runtime

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Company Kernel — enforces workflow, state, gates, validation, events |
| **Ownership** | Framework package (`runtime_engine`); contracts in `runtime/interfaces.md` |
| **Lifecycle** | Designed → implemented → released with framework |
| **Responsibilities** | Orchestration enforcement; resumable state; event bus; plugin host |
| **Relationships** | Reads Workflow; persists Project state; delegates agents via Adapter |
| **Versioning** | Contract semver in `interfaces.md`; impl package semver |
| **Persistence** | `.company/state/<project-id>.json` per workspace |

**Boundary:** Runtime never imports editor or MCP vendor code.

---

## 9. Package

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Installable Python module — runtime, CLI, validators, mcp_platform |
| **Ownership** | Framework |
| **Lifecycle** | Developed → published → versioned → deprecated |
| **Responsibilities** | Encapsulate code; expose public API per contracts |
| **Relationships** | Listed in manifest `packages:`; depended on by CLI and tools |
| **Versioning** | Independent package semver |
| **Persistence** | `packages/<name>/` |

See [package-architecture.md](./package-architecture.md).

---

## 10. Integration

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Editor-specific adapter — surfaces employees and MCP to IDE |
| **Ownership** | Framework provides templates; user enables per editor |
| **Lifecycle** | Installed → configured → active → upgraded |
| **Responsibilities** | Map framework paths to editor conventions; never own business logic |
| **Relationships** | Reads Manifest; mirrors Employees; optional MCP config |
| **Versioning** | Per integration package |
| **Persistence** | `integrations/<editor>/` |

See [integration-architecture.md](./integration-architecture.md).

---

## 11. Manifest

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Machine-readable framework composition — path resolution authority |
| **Ownership** | Framework schema; Company Instance file |
| **Lifecycle** | Schema versioned; instance file created at company creation |
| **Responsibilities** | Resolve all subsystem paths; pin versions |
| **Relationships** | Read by CLI, integrations, bootstrapper |
| **Versioning** | `schema_version` + `framework.version` |
| **Persistence** | `company.yaml` |

Spec: [company-manifest.md](../../company-manifest.md).

---

## 12. Template

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Scaffold files for workspace, project, and artifacts |
| **Ownership** | Framework |
| **Lifecycle** | Versioned with framework; projects snapshot at creation |
| **Responsibilities** | Reduce boilerplate; convention over configuration |
| **Relationships** | Used by CLI `init`, `project create` |
| **Versioning** | `templates.version` in manifest |
| **Persistence** | `templates/` |

---

## 13. Tool (MCP)

| Attribute | Definition |
|-----------|------------|
| **Purpose** | External capability provider — MCP server resolved from registry |
| **Ownership** | Third-party; registry entry framework-owned |
| **Lifecycle** | Registered → installed → health-checked → deprecated |
| **Responsibilities** | Satisfy capability requests |
| **Relationships** | Employees request Capability; MCP Platform resolves Tool |
| **Versioning** | Per MCP entry in registry |
| **Persistence** | `mcp/registry.yaml`; user `mcp.json` for installed servers |

---

## 14. Capability

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Abstract tool need — e.g. `documentation-lookup`, `structured-reasoning` |
| **Ownership** | Framework (`mcp/capabilities.yaml`) |
| **Lifecycle** | Defined → mapped → resolved at runtime |
| **Responsibilities** | Decouple employees from MCP names |
| **Relationships** | Maps to Tool via registry; requested by Employees |
| **Versioning** | Capabilities file version |
| **Persistence** | `mcp/capabilities.yaml` |

---

## 15. Plugin (Kernel)

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Runtime event subscriber — metrics, memory, evidence validation |
| **Ownership** | Plugin author; hosted by Runtime |
| **Lifecycle** | Registered → active → unregistered |
| **Responsibilities** | React to `KernelEvent`; never mutate kernel state |
| **Relationships** | Implements `IPlugin` per `runtime/interfaces.md` |
| **Versioning** | `supported_contract_version` |
| **Persistence** | External package or `packages/plugins/` |

---

## 16. Extension (Framework)

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Framework-level extension — validators, templates, employee overrides |
| **Ownership** | User or marketplace author |
| **Lifecycle** | Declared in manifest `extensions:` → loaded at company init |
| **Responsibilities** | Extend without forking framework |
| **Relationships** | Loaded by CLI; must not patch core files |
| **Versioning** | Per extension semver |
| **Persistence** | `workspaces/<ws>/extensions/` or npm/pip package |

---

## 17. Generated Artifacts

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Outputs not part of immutable framework — state, events, meta-reports |
| **Ownership** | Classified: Generated (disposable) |
| **Lifecycle** | Created during execution → archived or deleted |
| **Responsibilities** | Audit trail, resumability |
| **Relationships** | Produced by Runtime and Projects |
| **Versioning** | `schema_version` on state files |
| **Persistence** | `.company/` in workspace; `projects/` for framework SDLc history |

---

## 18. User Assets

| Attribute | Definition |
|-----------|------------|
| **Purpose** | User-owned files — credentials, local config, custom scripts |
| **Ownership** | User |
| **Lifecycle** | User-managed |
| **Responsibilities** | Environment-specific configuration |
| **Relationships** | Never committed to framework git |
| **Versioning** | N/A |
| **Persistence** | `~/.config/ai-company/`, workspace `.env`, editor user config |
| **Configuration** | `.env`, editor settings, OS keychain |
| **Extension Points** | N/A — user space |

---

## 19. Framework API

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Single public consumption surface for all products — CLI, editors, SDK, cloud |
| **Ownership** | Framework (`packages/company_core`) |
| **Lifecycle** | Designed → versioned → implemented → deprecated per semver |
| **Responsibilities** | Manifest, company, workspace, project, MCP, validation, upgrade APIs |
| **Relationships** | Consumed by CLI, integrations, SDK; wraps kernel via `IRuntime` |
| **Versioning** | `FrameworkAPI.version` independent of kernel contract semver |
| **Persistence** | Contract docs in [framework-api.md](./framework-api.md); code in `company_core` |
| **Configuration** | API behaviour driven by `company.yaml` — no hardcoded paths |
| **Extension Points** | `IFrameworkPlugin` hooks; custom validators via manifest |

**Rule:** No product bypasses Framework API to read framework paths directly.

See [framework-api.md](./framework-api.md), [ADR-0006](../adr/0006-framework-api.md).

---

## 20. Product (Ecosystem)

| Attribute | Definition |
|-----------|------------|
| **Purpose** | Deliverable that consumes Framework API — CLI, editor adapter, SDK, cloud |
| **Ownership** | Product team per package |
| **Lifecycle** | Planned → released → upgraded → deprecated |
| **Responsibilities** | UX and transport; zero duplicated framework logic |
| **Relationships** | 1 Framework : N Products; each product depends on `company_core` |
| **Versioning** | Independent product semver pinned to `framework.version` range |
| **Persistence** | Separate packages: `company_cli`, `integrations/cursor`, etc. |
| **Configuration** | Product-specific config under `integrations.<product>` in manifest |
| **Extension Points** | Products may ship companion plugins — not framework patches |

See [product-ecosystem.md](./product-ecosystem.md), [ADR-0008](../adr/0008-product-ecosystem.md).

---

## Ownership Taxonomy (Complete)

| Class | Examples | Framework Git |
|-------|----------|---------------|
| **Framework-owned** | handbook, employees, workflow, mcp/, interfaces.md | Yes |
| **Company-owned** | company.yaml, company.lock | Deployment |
| **Workspace-owned** | workspace.yaml, extensions/ | User git optional |
| **Project-owned** | idea.md…closure.md, source | User git optional |
| **Generated** | state.json, events.jsonl, pipeline sync | No |
| **User-owned** | API keys, .env | Never |
| **Temporary** | .tmp, build caches | Never |
| **Tool-generated** | `__pycache__`, editor index | Never |

---

## Concept Distinction Table

| Question | Framework | Company Instance | Workspace | Project |
|----------|-----------|------------------|-----------|---------|
| What is it? | Product | Deployment config | User environment | SDLc run |
| How many? | 1 install | N per machine | N per instance | N per workspace |
| Mutability | Release cycle | Config edits | User control | Phase gates |
| Contains employees? | Yes (canonical) | References | May override | Uses |
| Contains code? | Packages only | No | Yes (user) | Yes (output) |

---

## References

- [framework-model.md](./framework-model.md)
- [framework-api.md](./framework-api.md)
- [product-ecosystem.md](./product-ecosystem.md)
- [workspace-model.md](./workspace-model.md)
- [lifecycle.md](./lifecycle.md)
- [ADR-0001](../adr/0001-framework-philosophy.md)
