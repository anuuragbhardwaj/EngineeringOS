# Framework Architecture — AI Company Framework

**Version:** 2.0.0  
**Status:** Approved — constitutional design complete  
**Date:** 2026-07-01

---

## Constitutional Package (v2)

| Document | Scope |
|----------|-------|
| [framework-model.md](./framework-model.md) | What the Framework is — immutable product |
| [company-instance-model.md](./company-instance-model.md) | Company Instance — deployment config |
| [workspace-model.md](./workspace-model.md) | Workspace isolation |
| [project-model.md](./project-model.md) | Project SDLc execution |
| [domain-model.md](./domain-model.md) | 18+ concepts — full attribute sets |
| [framework-api.md](./framework-api.md) | **Framework API** — single consumption path |
| [product-ecosystem.md](./product-ecosystem.md) | CLI, editors, SDK, cloud, marketplace |
| [package-architecture.md](./package-architecture.md) | Installable packages |
| [integration-architecture.md](./integration-architecture.md) | Cursor, VS Code, Claude Code, Roo Code |
| [cli-architecture.md](./cli-architecture.md) | 20+ `company` commands |
| [plugin-architecture.md](./plugin-architecture.md) | Kernel + framework plugins |
| [versioning-strategy.md](./versioning-strategy.md) | Semver + migration |
| [lifecycle.md](./lifecycle.md) | Installation → maintenance |
| [dependency-map.md](./dependency-map.md) | Layer rules |
| [system-context.md](./system-context.md) | C4 diagrams |

**Kernel (separate constitution):** [runtime/interfaces.md](../../runtime/interfaces.md)

---

## Concept Stack

```
Framework (immutable product)
    └── Company Instance (company.yaml)
            └── Workspace (workspaces/<id>/)
                    └── Project (projects/<id>/)
```

---

## Implementation Status (2026-07-02)

| Component | Architecture source | Implementation | Status |
|-----------|--------------------|--------------------|--------|
| Framework API | framework-api.md | `packages/company_core` | **Shipped** |
| CLI | cli-architecture.md | `packages/company_cli` (`engineeringos`) | **Shipped** |
| Runtime | runtime/interfaces.md | `packages/runtime_engine` | **Shipped** |
| Orchestrator | Mission spec | `packages/orchestrator` | **Shipped** |
| AI Execution | Mission spec | `packages/ai_execution` | **Shipped** |
| Lifecycle | lifecycle.md | `packages/company_lifecycle` | **Shipped** |
| Workspace Execution | Mission spec | `packages/workspace_execution` | **Shipped** |
| Knowledge | Mission spec | `packages/knowledge` | **Shipped** |
| Source Control | Mission spec | `packages/source_control` | **Shipped** |
| Parallel Execution | Mission spec | `packages/parallel_execution` | **Shipped** |
| Autonomous Company | Mission spec | `packages/autonomous_company` | **Shipped** |
| Integrations | integration-architecture.md | `.cursor/agents/` only | **Partial** |
| Plugins | plugin-architecture.md | `register_plugin` not wired | **Planned** |
| Documentation Platform | docs/documentation/ | Employee-driven; no package | **Partial** |

**Architecture is frozen.** Documentation alignment completed 2026-07-02 — see [docs/alignment/](../alignment/).

**No further architectural redesign required** — future work extends within approved seams.

---

## ADRs

[docs/adr/](../adr/) — 0001 Framework Philosophy through 0012 Repository Philosophy

---

## Release Cleanup

[cleanup-report.md](../../cleanup-report.md) — historical files → `can_be_deleted/`

---

## Document History

| Version | Date | Change |
|---------|------|--------|
| 1.0.0 | 2026-07-01 | Initial constitutional design |
| 2.0.0 | 2026-07-01 | Framework API, product ecosystem, expanded models, GitHub release prep |
