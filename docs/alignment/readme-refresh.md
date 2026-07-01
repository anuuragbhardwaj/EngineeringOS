# README Refresh Report

**Date:** 2026-07-02  
**File:** `README.md` (repository root)

---

## Rationale

The previous README described EngineeringOS as "constitutional architecture complete" without distinguishing what is **actually runnable** from what remains **planned**. It listed core platforms but lacked:

- Honest **Implemented / Partially Implemented / Planned / Future Roadmap** sections
- **Known Limitations** transparency
- Link to published **self-audit** (`docs/audit/`)
- Accurate test count (128, not 58)
- Correct repository name context (`engineeringos/` not only `ai-company/`)

---

## Structure Changes

| Section | Before | After |
|---------|--------|-------|
| Title / positioning | Marketing tone | Factual product description |
| Quick Start | Links only | Links + honest capability summary |
| Repository Layout | Partial package list | All 11 Python packages |
| Core Components | All described as shipped | Split by implementation status |
| Execution stack | Missing autonomous layer | Full stack diagram |
| Development Setup | `ai-company` path | `engineeringos` path |
| Known Limitations | Absent | Dedicated section |
| Self-audit | Not linked | Links to `docs/audit/` |
| Contributing | Unchanged intent | Clarified doc-only vs implementation |

---

## Capability Matrix (README source of truth)

### Implemented

- 11-phase SDLc workflow (content + `workflow.yaml`)
- Runtime (`runtime_engine`) — lifecycle, gates, state, validation
- Orchestrator — sequencing, context, prompts, policies
- AI Execution Platform — provider boundary, scaffold/cursor providers
- Framework API (`FrameworkAPI` aggregate, 14 sub-APIs)
- EngineeringOS CLI (`engineeringos`, 40+ top-level command groups)
- Installation & Lifecycle Platform
- Workspace Execution Platform
- Knowledge Platform
- Source Control Platform
- Parallel Execution Engine
- Autonomous Company Platform
- MCP Platform validation (`mcp_platform`)
- 10 employee agent prompts
- 128 automated tests

### Partially Implemented

- EmployeeAPI / IntegrationAPI (stubs)
- CursorProvider (prompt + scaffold; not live Cursor AI API)
- Plugin system (`register_plugin` raises `NotImplementedError`)
- Documentation Platform (workflow + employee; no dedicated package)
- Editor integrations (`.cursor/agents/` only; no `integrations/` sync CLI)
- Placeholder AI providers (claude, openai, gemini, etc.)

### Planned

- VS Code / Claude Code / Roo Code integrations
- Python / TypeScript SDKs
- EventAPI, TemplateAPI, PluginAPI (Framework API tier)
- Distributed / cloud runtime
- Marketplace, Dashboard, REST API, Language Server

### Future Roadmap

- Memory platform, metrics, cost optimization (extension points exist)
- Provider plugin discovery (YAML-driven registration)
- Persisted orchestrator checkpoints across process restarts
- Shared contracts package (eliminate `company_core → runtime_engine` coupling)

---

## Marketing Language Removed

| Removed phrase | Replacement |
|----------------|---------------|
| "complete" (unqualified) | "implemented" with scope |
| "Design phase complete — implementation next" | Status table per component |
| Implied all CLI commands shipped | Per-command status in `docs/cli/README.md` |

---

## Cross-References Added

- `docs/alignment/` — this alignment project deliverables
- `docs/audit/` — architecture compliance, technical debt, release readiness
- Per-platform `docs/<platform>/` and `packages/<platform>/README.md`
