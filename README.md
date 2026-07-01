# AI Company Framework

**Version:** 2.0.0 (constitutional architecture complete)  
**Type:** Installable, versioned AI Engineering Framework

The AI Company Framework provides a complete **11-phase SDLC**, ten specialist **employees** (AI agents), quality **gates**, **handbook** standards, **MCP Platform** tool governance, and **Company Kernel** runtime contracts — editor-independent by design.

---

## Quick Start

| I want to… | Go to |
|------------|-------|
| Understand the delivery pipeline | [handbook/company-handbook.md](./handbook/company-handbook.md) |
| See SDLc phases and gates | [workflow-v1.md](./workflow-v1.md) |
| Find employee roles | [.cursor/agents/](./.cursor/agents/) |
| Use MCP tools | [mcp/employee-matrix.md](./mcp/employee-matrix.md) |
| Read kernel API contracts | [runtime/interfaces.md](./runtime/interfaces.md) |
| Read framework constitution | [docs/framework/framework-architecture.md](./docs/framework/framework-architecture.md) |
| Documentation standards | [handbook/documentation-standards.md](./handbook/documentation-standards.md) |
| Validate MCP setup | `python -m mcp_platform validate` |
| Use EngineeringOS CLI | `engineeringos --help` — see [docs/cli/README.md](./docs/cli/README.md) |

---

## Repository Layout

```
ai-company/
├── handbook/              # Company standards and policies
├── mcp/                   # MCP Platform (registry, capabilities, policies)
├── mcp_platform/          # MCP validation tooling
├── packages/
│   ├── company_core/      # Framework API (manifest, models)
│   ├── company_cli/       # EngineeringOS CLI (engineeringos)
│   ├── runtime_engine/    # Company Kernel (Runtime v1)
│   ├── ai_execution/      # AI Execution Platform (provider boundary)
│   ├── orchestrator/      # Operational intelligence layer
│   ├── workspace_execution/ # Context-aware execution sessions
│   ├── knowledge/           # Permanent engineering intelligence
│   ├── source_control/      # Repository management platform
│   ├── parallel_execution/  # Concurrent employee scheduling
│   └── autonomous_company/  # Autonomous engineering company
│   └── company_lifecycle/ # Installation & lifecycle platform
├── tests/                 # CLI and Framework API tests
├── company.yaml           # Dev company instance manifest
├── .cursor/agents/        # Employee agent prompts (Cursor adapter)
├── workflow.yaml          # Machine-readable SDLc
├── workflow-v1.md         # Human-readable SDLc
├── runtime/
│   └── interfaces.md      # Company Kernel public API (constitution)
├── docs/
│   ├── framework/         # Constitutional architecture (v2)
│   └── adr/               # ADRs 0001–0012
├── projects/
│   └── framework-architecture/   # Active SDLc (design phase complete)
├── company-manifest.md    # company.yaml specification
├── cleanup-report.md      # GitHub release cleanup inventory
└── can_be_deleted/        # Historical files (preserved, not in release)
```

---

## Core Components

### SDLc Workflow

Eleven phases: Idea → Requirements → Specification → Planning → Architecture → Implementation → Testing → Review → **Documentation** → Release → Closure.

Each phase has a quality gate (G0–G9), artifact ownership, and rework routing.

### Employees

Ten specialist agents coordinated by the **Engineering Manager**:

| Agent | Phase |
|-------|-------|
| Engineering Manager | Orchestration |
| Product Manager | Requirements |
| Business Analyst | Specification |
| Software Planner | Planning |
| Software Architect | Architecture |
| Backend / Frontend Engineer | Implementation |
| QA Engineer | Testing |
| Code Reviewer | Review |
| **Documentation Engineer** | **Documentation** |

### MCP Platform

Employees request **capabilities** (not MCP names). The registry resolves tools.

```bash
python -m mcp_platform validate
python -m mcp_platform resolve documentation-lookup
```

See [mcp/selection-policy.md](./mcp/selection-policy.md).

### Company Kernel

Public runtime contracts in [runtime/interfaces.md](./runtime/interfaces.md). **Runtime v1** (`runtime_engine`) executes the planning pipeline (Idea → Architecture).

```bash
engineeringos project create --yes --name "My App" --location ./projects/my-app
engineeringos project status my-app
```

See [packages/runtime_engine/README.md](./packages/runtime_engine/README.md).

### AI Execution Platform

All AI provider communication flows through `ai_execution` — Runtime never calls Cursor or any provider directly.

See [packages/ai_execution/README.md](./packages/ai_execution/README.md) and [docs/ai-execution/README.md](./docs/ai-execution/README.md).

### Orchestrator

Sequences employees, assembles context, builds prompts, and routes conversations. Runtime delegates all orchestration intelligence here.

See [packages/orchestrator/README.md](./packages/orchestrator/README.md) and [docs/orchestrator/README.md](./docs/orchestrator/README.md).

### Installation & Lifecycle Platform

Generates user-owned companies, workspaces, and projects. Framework is installed once; companies reference it via `framework.install_path`.

See [packages/company_lifecycle/README.md](./packages/company_lifecycle/README.md) and [docs/lifecycle/README.md](./docs/lifecycle/README.md).

### Workspace Execution Platform

Persistent execution context — active company, workspace, project, phase, and intelligent resume.

See [packages/workspace_execution/README.md](./packages/workspace_execution/README.md) and [docs/workspace-execution/README.md](./docs/workspace-execution/README.md).

### Knowledge Platform

Permanent engineering intelligence — durable knowledge with traceability, validation, and contextual retrieval.

See [packages/knowledge/README.md](./packages/knowledge/README.md) and [docs/knowledge/README.md](./docs/knowledge/README.md).

### Source Control Platform

Repository management by the Source Control Engineer — automatic repo discovery, knowledge-informed commits, EM-approved operations.

See [packages/source_control/README.md](./packages/source_control/README.md) and [docs/source-control/README.md](./docs/source-control/README.md).

### Parallel Execution Engine

Safe concurrent employee execution — dependency graphs, worker pools, synchronization barriers, and conflict detection.

See [packages/parallel_execution/README.md](./packages/parallel_execution/README.md) and [docs/parallel-execution/README.md](./docs/parallel-execution/README.md).

### Autonomous Company Platform

Self-operating engineering company — goal-based execution, blocker detection, explainable decisions, and automatic pipeline continuation.

See [packages/autonomous_company/README.md](./packages/autonomous_company/README.md) and [docs/autonomous-company/README.md](./docs/autonomous-company/README.md).

### Framework API

All products (CLI, editors, SDK, cloud) consume the [Framework API](./docs/framework/framework-api.md) — no bypass.

---

## Concept Stack

```
Framework (immutable product)
    └── Company Instance (company.yaml)
            └── Workspace (workspaces/<id>/)
                    └── Project (projects/<id>/)
```

See [docs/framework/domain-model.md](./docs/framework/domain-model.md) for 20 defined concepts.

---

## Development Setup

```bash
cd ai-company
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -e ".[dev]"
engineeringos version
python -m mcp_platform validate
```

### EngineeringOS CLI

```bash
engineeringos --help
engineeringos init ./my-instance --id my-company
engineeringos doctor
engineeringos validate
engineeringos mcp list
```

Full command reference: [docs/cli/README.md](./docs/cli/README.md).

Enable **sequential-thinking** MCP in Cursor (see [mcp/installation-guide.md](./mcp/installation-guide.md)).

---

## Framework Constitution

| Document | Purpose |
|----------|---------|
| [framework-architecture.md](./docs/framework/framework-architecture.md) | **Master index** |
| [framework-model.md](./docs/framework/framework-model.md) | Framework product definition |
| [company-instance-model.md](./docs/framework/company-instance-model.md) | Company Instance |
| [workspace-model.md](./docs/framework/workspace-model.md) | Workspace isolation |
| [project-model.md](./docs/framework/project-model.md) | Project SDLc |
| [framework-api.md](./docs/framework/framework-api.md) | Single consumption API |
| [product-ecosystem.md](./docs/framework/product-ecosystem.md) | CLI, editors, SDK, cloud |
| [cli-architecture.md](./docs/framework/cli-architecture.md) | `company` commands |
| [package-architecture.md](./docs/framework/package-architecture.md) | Installable packages |
| [integration-architecture.md](./docs/framework/integration-architecture.md) | Cursor, VS Code, Claude Code, Roo Code |
| [plugin-architecture.md](./docs/framework/plugin-architecture.md) | Kernel + framework plugins |
| [versioning-strategy.md](./docs/framework/versioning-strategy.md) | Semver and upgrades |
| [lifecycle.md](./docs/framework/lifecycle.md) | Installation → maintenance |
| [docs/adr/](./docs/adr/) | ADRs 0001–0012 |

**Design phase complete.** Future work is implementation — not architectural redesign.

---

## Historical Archives

Completed SDLc packages, meta-reports, and superseded planning documents are preserved in [can_be_deleted/](./can_be_deleted/). See [cleanup-report.md](./cleanup-report.md) for the full inventory.

---

## Contributing

1. Read [handbook/company-handbook.md](./handbook/company-handbook.md)
2. Follow SDLc — do not skip phases
3. Employees must not modify upstream artifacts outside their phase
4. MCP changes: edit `mcp/registry.yaml` only — not employee prompts
5. Do not modify framework files from workspace/project context

---

## License

TBD.
