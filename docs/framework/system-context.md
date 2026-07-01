# System Context — AI Company Framework

**Version:** 2.0.0  
**Date:** 2026-07-01  
**Parent:** [framework-architecture.md](./framework-architecture.md)

---

## C4 Level 1 — System Context

```mermaid
flowchart TB
    User[User / Operator]
    EM[Engineering Manager]
    Maint[Framework Maintainer]

    subgraph AICompanyFramework [AI Company Framework]
        FW[Framework Core]
    end

    subgraph External [External Systems]
        Cursor[Cursor IDE]
        VSCode[VS Code]
        MCP[MCP Servers]
        Git[Git / GitHub]
        Cloud[Cloud Runtime - future]
    end

    User --> EM
    User --> FW
    EM --> FW
    Maint --> FW
    FW --> Cursor
    FW --> VSCode
    FW --> MCP
    FW --> Git
    FW -.-> Cloud
```

### Actors

| Actor | Interacts via | Goal |
|-------|---------------|------|
| **User / Stakeholder** | EM, CLI | Ship software through SDLc |
| **Engineering Manager** | Employees, Runtime | Orchestrate pipeline |
| **Framework Maintainer** | Git, SDLc | Evolve framework |
| **Specialist Employees** | Integrations | Produce artifacts |
| **CI/CD** | CLI `doctor`, `validate` | Gate framework health |

---

## C4 Level 2 — Containers

```mermaid
flowchart TB
    subgraph Framework [Framework Repository / Install]
        CLI[company CLI]
        Core[company_core]
        RT[runtime_engine]
        MCPPlat[mcp_platform]
        Content[Content: handbook, employees, workflow, mcp]
        Contracts[Contracts: interfaces.md, company.yaml]
    end

    subgraph Workspace [User Workspace - gitignored]
        Projects[Projects]
        State[.company/state]
    end

    subgraph Integrations [Editor Integrations]
        CursorInt[Cursor Adapter]
        VSCodeInt[VS Code Adapter]
    end

    CLI --> Core
    CLI --> RT
    CLI --> MCPPlat
    Core --> Contracts
    RT --> Content
    RT --> State
    MCPPlat --> Content
    CursorInt --> Content
    VSCodeInt --> Content
    Projects --> RT
```

### Container Descriptions

| Container | Technology | Responsibility |
|-----------|------------|----------------|
| **company CLI** | Python/Typer | Operator interface |
| **company_core** | Python | Manifest, paths, models |
| **runtime_engine** | Python | Kernel implementation |
| **mcp_platform** | Python | MCP validation |
| **Content packages** | Markdown/YAML | Policies, agents, workflow |
| **Contracts** | Markdown/YAML | Stable APIs |
| **Workspace** | Filesystem | User projects + state |
| **Integrations** | Config/symlinks | Editor wiring |

---

## C4 Level 3 — Runtime Components

```mermaid
flowchart LR
    subgraph RuntimeEngine [runtime_engine]
        Facade[IRuntime]
        PE[PipelineEngine]
        GE[GateEngine]
        RE[ReworkEngine]
        VE[ValidationEngine]
        AR[AgentRegistry]
        SS[StateStore]
        EB[EventBus]
        WL[WorkflowLoader]
        PM[PluginManager]
    end

    Facade --> PE
    Facade --> GE
    Facade --> RE
    Facade --> VE
    Facade --> AR
    Facade --> SS
    Facade --> EB
    Facade --> WL
    Facade --> PM
    PE --> WL
    GE --> VE
```

See [runtime/interfaces.md](../../runtime/interfaces.md) for interface details.

---

## Deployment Views

### Local Developer (Current)

```
Developer Machine
├── Framework install (git clone ai-company/)
├── .venv (local, not in git)
├── workspaces/default/
│   └── projects/<feature>/
└── Cursor IDE → integrations/cursor
```

### Installed Package (Future)

```
pip install ai-company-framework
~/.local/share/ai-company/<version>/
~/projects/my-workspace/
company init / company open / company project create
```

### Cloud Execution (Future)

```
Company CLI (local) ──► Remote Runtime API
                              │
                         Agent Workers
                              │
                         MCP Proxy
```

Architecture supports without container changes — `IAgentAdapter` + remote state store.

---

## Trust Boundaries

| Boundary | Inside | Outside |
|----------|--------|---------|
| **Framework core** | handbook, employees, contracts | User project code |
| **Workspace** | User artifacts, state | Framework git |
| **MCP** | Registry, policies | MCP server processes |
| **Secrets** | Env vars, user config | Never in framework git |

---

## References

- [framework-architecture.md](./framework-architecture.md)
- [domain-model.md](./domain-model.md)
