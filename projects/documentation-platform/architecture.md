# Architecture — Documentation Platform

**Date:** 2026-07-01  
**Owner:** Senior Software Architect

---

## Overview

The Documentation Platform is a **process and standards layer** — not a runtime service. It comprises handbook standards, agent role definition, workflow phase insertion, and specification documents. No Python packages required for v1.

```
┌─────────────────────────────────────────────────────────────┐
│                    SDLC Workflow v1.1                        │
│  ... → Review (G7) → Documentation (G8) → Release (G9)    │
└───────────────────────────┬─────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│ handbook/     │   │ .cursor/      │   │ docs/         │
│ documentation/│   │ agents/       │   │ documentation/│
│ (writing SOT) │   │ doc-engineer  │   │ (platform)    │
└───────────────┘   └───────────────┘   └───────────────┘
        │                   │                   │
        └───────────────────┴───────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │  Project artifacts       │
              │  idea.md … review.md     │
              │  source, git, config     │
              └────────────┬────────────┘
                           ▼
              ┌─────────────────────────┐
              │  Generated docs          │
              │  README, CHANGELOG, docs/│
              │  documentation-report.md │
              └─────────────────────────┘
```

## Component Design

### 1. Documentation Handbook (`handbook/documentation/`)

| File | Role |
|------|------|
| `documentation-style-guide.md` | Master — voice, accuracy, structure, traceability |
| `github-style.md` | README, CONTRIBUTING, repo layout |
| `architecture-style.md` | ARCHITECTURE.md, system diagrams |
| `api-style.md` | API.md, endpoint reference |
| `release-notes-style.md` | CHANGELOG, RELEASE_NOTES |

Root `handbook/documentation-style-guide.md` — index only.  
`handbook/documentation-standards.md` — SDLC ownership and phase rules.

### 2. Documentation Engineer Agent

- **Location:** `.cursor/agents/documentation-engineer.md`
- **Phase:** 8 — Documentation
- **Primary artifact:** `documentation-report.md`
- **Generated outputs:** Per `docs/documentation/documentation-templates.md`
- **Constraints:** Handbook is sole writing authority; prompt contains behavior only

### 3. Workflow Changes (`workflow.yaml` v1.1)

| Phase | Order | Gate | Artifact |
|-------|-------|------|----------|
| Documentation | 8 | G8 | `documentation-report.md` + generated docs |
| Release | 9 | G9 | `release.md` |
| Closure | 10 | G10 | `closure.md` |

**Skip policy:** `skippable: true` when EM documents design-only exemption in `pipeline-status.md`.

### 4. Platform Docs (`docs/documentation/`)

| File | Purpose |
|------|---------|
| `documentation-platform.md` | System overview |
| `documentation-validation.md` | G8 validation checklist |
| `documentation-templates.md` | Output templates |
| `github-documentation.md` | GitHub repo standards |

### 5. MCP Integration

| Capability | When | Gate |
|------------|------|------|
| `documentation-lookup` | Framework/library/API documentation | G8 evidence when applicable |
| `structured-reasoning` | Complex multi-doc projects | Optional |

Fallback: continue with `confidence: reduced` in `documentation-report.md`.

## Task Coverage Matrix

| Task | Architecture element |
|------|---------------------|
| T-01 | Handbook |
| T-02 | Platform docs |
| T-03 | Agent |
| T-04 | Workflow |
| T-05 | Handbook integration |
| T-06 | Report template |
| T-07 | MCP matrix |
| T-08 | SDLC closure |

## Data Flow

1. G7 passes → EM delegates Documentation Engineer
2. Engineer reads artifacts + source + git
3. Engineer selects templates by project type (from architecture.md / release.md)
4. Engineer generates docs following handbook
5. Engineer runs validation checklist
6. Engineer produces `documentation-report.md` with traceability + verdict
7. EM validates G8 → Release (G9)

## Security

- No secrets in generated documentation
- Redact credentials from config examples
- `mcp_platform validate` for MCP config references only

## Risks

| Risk | Mitigation |
|------|------------|
| Gate renumber confusion | workflow-v1.md + EM table updated |
| Doc drift from code | Validation requires source cross-check |

## MCP Evidence

| Capability | MCP | Status | Notes |
|------------|-----|--------|-------|
| documentation-lookup | context7 | completed | Verified Typer/docs patterns for handbook structure; GitHub README conventions from public standards |
