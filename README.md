# EngineeringOS

**Version:** 2.0.0  
**Type:** Installable AI Engineering Framework and runtime

EngineeringOS is an editor-independent framework for running an 11-phase software delivery lifecycle with specialist AI employees, quality gates, MCP tool governance, and a composable execution stack.

This README describes **what is implemented today**, what is partial, and what remains planned. It does not overstate capabilities.

---

## Quick Start

| I want to… | Go to |
|------------|-------|
| Install and run the CLI | [Development Setup](#development-setup) |
| Understand the delivery pipeline | [handbook/company-handbook.md](./handbook/company-handbook.md) |
| See SDLC phases and gates | [workflow-v1.md](./workflow-v1.md) |
| Read Framework API contracts | [docs/framework/framework-api.md](./docs/framework/framework-api.md) |
| Read kernel contracts | [runtime/interfaces.md](./runtime/interfaces.md) |
| Full CLI reference | [docs/cli/README.md](./docs/cli/README.md) |
| Architecture self-audit | [docs/audit/](./docs/audit/) |
| Documentation alignment (2026-07-02) | [docs/alignment/](./docs/alignment/) |

```bash
pip install -e ".[dev]"
engineeringos --help
engineeringos doctor
pytest tests/ -q    # 134 tests
```

---

## Implementation Status

### Implemented

| Component | Package / location | Notes |
|-----------|-------------------|-------|
| **11-phase SDLC** | `workflow.yaml`, `handbook/` | Content authority; machine-readable workflow |
| **Runtime** | `packages/runtime_engine` | Lifecycle, gates, state, validation, events |
| **Orchestrator** | `packages/orchestrator` | Sequencing, context, prompts, policies |
| **AI Execution Platform** | `packages/ai_execution` | Provider boundary; scaffold + cursor providers |
| **Framework API** | `packages/company_core` | `FrameworkAPI` aggregate — single consumption path |
| **EngineeringOS CLI** | `packages/company_cli` | Binary: `engineeringos` |
| **Installation & Lifecycle** | `packages/company_lifecycle` | init, workspaces, projects, templates, upgrade |
| **Workspace Execution** | `packages/workspace_execution` | Session, context, resume, history |
| **Knowledge Platform** | `packages/knowledge` | Store, retrieval, promotion, git hooks |
| **Source Control Platform** | `packages/source_control` | Git provider, EM-approved commit/push |
| **Parallel Execution Engine** | `packages/parallel_execution` | Dependency graphs, workers, orchestrator hook |
| **Autonomous Company Platform** | `packages/autonomous_company` | Goals, decisions, blockers, SDLC completion |
| **MCP Platform** | `mcp_platform/` | Registry validation and resolution |
| **Employees** | `.cursor/agents/` | 10 specialist agent prompts |
| **Automated tests** | `tests/` | 134 tests |

### Partially Implemented

| Component | Gap |
|-----------|-----|
| **EmployeeAPI / IntegrationAPI** | Framework API stubs — raise `NotImplementedFeatureError` |
| **CursorProvider** | Loads prompts and scaffolds artifacts; does not call live Cursor AI APIs |
| **Placeholder AI providers** | claude, openai, gemini, etc. — registered but not production-ready |
| **Plugin system** | `register_plugin` raises `NotImplementedError` |
| **Documentation Platform** | Spec in `docs/documentation/`; driven by Documentation Engineer employee — no Python package |
| **Editor integrations** | `.cursor/agents/` adapter only; no VS Code / Claude Code / Roo Code sync CLI |
| **Orchestrator checkpoints** | In-memory; not fully persisted across process restarts |
| **`company_core` purity** | `ProjectAPI` imports `runtime_engine` — documented monorepo coupling |

### Planned

| Component | Reference |
|-----------|-----------|
| VS Code, Claude Code, Roo Code integrations | [integration-architecture.md](./docs/framework/integration-architecture.md) |
| Python / TypeScript SDKs | [product-ecosystem.md](./docs/framework/product-ecosystem.md) |
| EventAPI, TemplateAPI, PluginAPI (Framework tier) | [framework-api.md](./docs/framework/framework-api.md) |
| YAML-driven provider plugin discovery | [ai-execution README](./packages/ai_execution/README.md) |
| Distributed / cloud runtime | [system-context.md](./docs/framework/system-context.md) |

### Future Roadmap

- Memory platform, metrics, cost optimization (extension points in orchestrator / AI execution)
- Shared contracts package to eliminate cross-package type imports
- Persisted orchestrator approval and checkpoint state
- Marketplace, Dashboard, REST API, Language Server

---

## Execution Stack

```
CEO / User
    │
    ▼
engineeringos CLI
    │
    ▼
Framework API (company_core)
    │
    ├── Autonomous Company ── goal-based supervision, SDLC completion
    ├── Workspace Execution ── session, context, resume
    ├── Knowledge / Source Control / Parallel Execution
    │
    ▼
Runtime (runtime_engine) ── lifecycle, gates, state
    │
    ▼
Orchestrator ── sequencing, context, prompts
    │
    ├── Parallel Execution (when policy enables)
    ▼
AI Execution Platform ── providers
    │
    ▼
Employees (agent prompts)
```

---

## Repository Layout

```
engineeringos/
├── handbook/                  # Company standards
├── mcp/                       # MCP registry, capabilities, policies
├── mcp_platform/              # MCP validation tooling
├── packages/
│   ├── company_core/          # Framework API
│   ├── company_cli/           # engineeringos CLI
│   ├── company_lifecycle/     # Installation & lifecycle
│   ├── runtime_engine/        # Company Kernel
│   ├── orchestrator/          # Operational intelligence
│   ├── ai_execution/          # Provider boundary
│   ├── workspace_execution/   # Execution sessions
│   ├── knowledge/             # Engineering intelligence
│   ├── source_control/        # Repository management
│   ├── parallel_execution/    # Concurrent scheduling
│   └── autonomous_company/    # Autonomous engineering company
├── runtime/
│   ├── interfaces.md          # Kernel public API (frozen)
│   └── employee-registry.yaml
├── docs/
│   ├── framework/             # Constitutional architecture
│   ├── alignment/             # Documentation alignment reports (2026-07-02)
│   ├── audit/                 # Architecture self-audit
│   ├── cli/, orchestrator/, ai-execution/, lifecycle/, …
│   └── adr/                   # ADRs 0001–0012
├── tests/                     # 128 automated tests
├── company.yaml               # Dev company instance
├── workflow.yaml              # Machine-readable SDLC
└── .cursor/agents/            # Employee prompts (Cursor adapter)
```

---

## Platform Documentation

| Platform | Package README | User docs |
|----------|---------------|-----------|
| Lifecycle | [packages/company_lifecycle/README.md](./packages/company_lifecycle/README.md) | [docs/lifecycle/](./docs/lifecycle/) |
| Workspace Execution | [packages/workspace_execution/README.md](./packages/workspace_execution/README.md) | [docs/workspace-execution/](./docs/workspace-execution/) |
| Knowledge | [packages/knowledge/README.md](./packages/knowledge/README.md) | [docs/knowledge/](./docs/knowledge/) |
| Source Control | [packages/source_control/README.md](./packages/source_control/README.md) | [docs/source-control/](./docs/source-control/) |
| Parallel Execution | [packages/parallel_execution/README.md](./packages/parallel_execution/README.md) | [docs/parallel-execution/](./docs/parallel-execution/) |
| Autonomous Company | [packages/autonomous_company/README.md](./packages/autonomous_company/README.md) | [docs/autonomous-company/](./docs/autonomous-company/) |
| Runtime | [packages/runtime_engine/README.md](./packages/runtime_engine/README.md) | [runtime/interfaces.md](./runtime/interfaces.md) |
| Orchestrator | [packages/orchestrator/README.md](./packages/orchestrator/README.md) | [docs/orchestrator/](./docs/orchestrator/) |
| AI Execution | [packages/ai_execution/README.md](./packages/ai_execution/README.md) | [docs/ai-execution/](./docs/ai-execution/) |
| CLI | [packages/company_cli/README.md](./packages/company_cli/README.md) | [docs/cli/README.md](./docs/cli/README.md) |

---

## Known Limitations

### Experimental / preview quality

- EngineeringOS is **architecture-stable** but **not production-hardened**. Suitable for development and evaluation, not unattended production deployment without review.
- Autonomous Company Platform runs supervision cycles; long-running unattended operation depends on local git identity, approvals, and policy configuration.

### Provider limitations

- **CursorProvider** does not invoke Cursor AI APIs — it loads employee prompts and scaffolds phase artifacts.
- **Placeholder providers** (OpenAI, Anthropic, Gemini, etc.) are registered but not fully implemented.
- Provider registration is **code-based** in `ai_execution/factory.py`, not YAML-plugin-driven.

### Autonomous limitations

- Runner executes discrete supervision cycles (`max_cycles` default 1 per `continue`); does not run an infinite background daemon.
- Blocker detection covers session, runtime, and repository states — not all blocker types are wired to live subsystems.
- `complete_sdlc()` requires commit approval and git author identity (env vars or local git config).
- Push occurs only when `policy.auto_push` or `auto_push=True` is set **and** push is approved.

### Checkpoint limitations

- Orchestrator checkpoints and approval hooks are **partially ephemeral** (in-memory). Process restart may lose checkpoint state not mirrored in Runtime `PipelineState` or `.company/` session files.
- Parallel execution checkpoint recovery depends on platform availability at recover time.

### Production readiness

- **128 tests** cover core platforms; `mcp_platform` has limited dedicated test coverage.
- Policy fields such as `timeout_seconds` and `mcp_evidence_required` are resolved but **not enforced** in all paths.
- `AgentInvocationFailed` kernel event is specified but **not emitted** on all adapter failures.

### Installation assumptions

- Monorepo editable install: `pip install -e ".[dev]"` from repository root.
- `company.yaml` `framework.install_path` should point at framework root for instance companies.
- Git operations require a configured author identity for commits.

### Architectural debt

Published openly in [docs/audit/](./docs/audit/):

| Issue | Severity |
|-------|----------|
| `company_core → runtime_engine` dependency | Documented violation |
| Orchestrator mutates `PipelineState` without Runtime-owned mutation port | High |
| Four `discover_framework_root` heuristics across packages | Medium — **consolidated** to `company_core.config.loader.discover_framework_root_from_path` |
| `mcp_platform` at repo root vs `packages/` convention | Medium |
| ~~Dead code: `em_runner.py`, `runtime_engine/adapters/scaffold.py`~~ | **Removed** (2026-07-02 cleanup) |

See [docs/audit/technical-debt.md](./docs/audit/technical-debt.md) and [docs/audit/architecture-compliance.md](./docs/audit/architecture-compliance.md).

---

## Self-Audit

EngineeringOS publishes its architecture audit — known issues are not hidden.

| Report | Purpose |
|--------|---------|
| [implementation-audit.md](./docs/audit/implementation-audit.md) | Full codebase audit |
| [architecture-compliance.md](./docs/audit/architecture-compliance.md) | Contract compliance matrix |
| [technical-debt.md](./docs/audit/technical-debt.md) | Debt register |
| [dependency-analysis.md](./docs/audit/dependency-analysis.md) | Import graph |
| [release-readiness.md](./docs/audit/release-readiness.md) | Release assessment |
| [future-extension-readiness.md](./docs/audit/future-extension-readiness.md) | Extension point analysis |

Documentation alignment deliverables: [docs/alignment/](./docs/alignment/).

---

## Development Setup

```bash
cd engineeringos
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
engineeringos version
python -m mcp_platform validate
pytest tests/ -q
```

### Example CLI flows

```bash
# Company instance
engineeringos init ./my-co --id my-co --yes
engineeringos open
engineeringos workspace create dev
engineeringos project create my-app --yes

# Autonomous execution
engineeringos work "Implement user authentication"
engineeringos continue
engineeringos autonomy status

# Knowledge and source control
engineeringos knowledge search "architecture"
engineeringos repo status
```

---

## Framework Constitution

| Document | Purpose |
|----------|---------|
| [framework-architecture.md](./docs/framework/framework-architecture.md) | Master index |
| [framework-api.md](./docs/framework/framework-api.md) | Framework API (implemented) |
| [package-architecture.md](./docs/framework/package-architecture.md) | Package inventory |
| [dependency-map.md](./docs/framework/dependency-map.md) | Layer rules and DAG |
| [system-context.md](./docs/framework/system-context.md) | C4 diagrams |
| [product-ecosystem.md](./docs/framework/product-ecosystem.md) | Product catalog |
| [runtime/interfaces.md](./runtime/interfaces.md) | Kernel API (frozen) |

**Architecture is frozen.** Future work extends implementation within approved seams — not redesign.

---

## Contributing

1. Read [handbook/company-handbook.md](./handbook/company-handbook.md)
2. Follow SDLC — do not skip phases
3. Employees must not modify upstream artifacts outside their phase
4. MCP changes: edit `mcp/registry.yaml` — not employee prompts
5. Do not modify framework files from workspace/project context

---

## License

TBD.
