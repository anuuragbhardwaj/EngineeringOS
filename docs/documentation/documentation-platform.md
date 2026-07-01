# Documentation Platform

**Version:** 1.0.0  
**Date:** 2026-07-01  
**Authority:** AI Company Framework

---

## Overview

The Documentation Platform transforms project artifacts and source code into accurate, maintainable, GitHub-ready documentation. It is a **process layer** comprising standards, templates, validation, and the Documentation Engineer employee — not a separate runtime service in v1.

---

## Goals

| Goal | Mechanism |
|------|-----------|
| Eliminate manual doc assembly | Documentation Engineer owns generation |
| Traceability | `documentation-report.md` matrix |
| Consistent voice | `handbook/documentation/` style guides |
| Gate before release | G8 Documentation in workflow v1.1 |
| MCP-assisted accuracy | `documentation-lookup` for library/API docs |

---

## Architecture

```
Project Artifacts + Source + Git
            │
            ▼
   Documentation Engineer
   (reads handbook/documentation/)
            │
            ├──► README.md, docs/, CHANGELOG, …
            │
            └──► documentation-report.md
                      │
                      ▼
                 EM validates G8
                      │
                      ▼
                   Release G9
```

---

## Components

| Component | Location |
|-----------|----------|
| Writing standards | `handbook/documentation/` |
| SDLC rules | `handbook/documentation-standards.md` |
| Employee | `.cursor/agents/documentation-engineer.md` |
| Templates | [documentation-templates.md](./documentation-templates.md) |
| Validation | [documentation-validation.md](./documentation-validation.md) |
| GitHub guide | [github-documentation.md](./github-documentation.md) |
| Workflow | `workflow.yaml` v1.1 phase 8 |

---

## Inputs

See [documentation-standards.md](../../handbook/documentation-standards.md) § Inputs.

---

## Outputs

See [documentation-templates.md](./documentation-templates.md) for full catalog.

---

## Project Type Matrix

| Type | Typical outputs |
|------|-----------------|
| `framework` | README, ARCHITECTURE, CONTRIBUTING, docs/framework links |
| `library` | README, API (if public API), CHANGELOG |
| `application` | README, SETUP, USAGE, INSTALLATION |
| `infrastructure` | README, ARCHITECTURE, deployment guide |
| `design-only` | Minimal README or skip with EM approval |

Project type declared in `architecture.md` or `pipeline-status.md`.

---

## Future

| Feature | Status |
|---------|--------|
| `company docs generate` CLI | Planned |
| Runtime doc plugin | Planned |
| Auto-sync on phase complete | Planned |

---

## References

- [handbook/documentation-standards.md](../../handbook/documentation-standards.md)
- [workflow.yaml](../../workflow.yaml)
