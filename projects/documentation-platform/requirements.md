# Requirements — Documentation Platform

**Date:** 2026-07-01  
**Owner:** Senior Product Manager

---

## Problem Statement

The AI Company produces high-quality software artifacts through a 10-phase pipeline, but project documentation (README, guides, changelogs, API reference) is not owned by any employee and is not gated before release. This creates inconsistent GitHub presence, stale setup instructions, and manual rework.

## Target Users

1. **Engineering Manager** — validates documentation quality at a new gate before release
2. **Documentation Engineer** — generates and validates all project documentation
3. **Open-source / GitHub consumers** — read accurate, maintainable docs
4. **Implementers** — freed from writing READMEs and release notes

## Goals

| ID | Goal |
|----|------|
| G-01 | Introduce Documentation Engineer as tenth specialist employee |
| G-02 | Insert Documentation phase between Review and Release |
| G-03 | Centralize writing standards in handbook (not agent prompts) |
| G-04 | Generate docs from project artifacts and source — zero invention |
| G-05 | Support GitHub-standard documentation set |
| G-06 | Validate docs against implementation before release |

## Features (MoSCoW)

### Must Have

| ID | Feature | Rationale |
|----|---------|-----------|
| F-01 | Documentation Engineer agent prompt | New role in roster |
| F-02 | Documentation handbook (`handbook/documentation/`) | Single source of writing truth |
| F-03 | SDLC phase + gate G8 Documentation | Mandatory before release (production) |
| F-04 | `documentation-report.md` phase artifact | Gate evidence and validation record |
| F-05 | Platform specs (templates, validation, GitHub guide) | Repeatable process |
| F-06 | Workflow + DoD updates | Company-wide adoption |
| F-07 | Artifact traceability in every doc set | FR against invention |
| F-08 | MCP `documentation-lookup` for framework/API docs | Required when documenting libraries |

### Should Have

| ID | Feature | Rationale |
|----|---------|-----------|
| F-09 | `docs/` directory convention for extended documentation | Scalable projects |
| F-10 | CHANGELOG + RELEASE_NOTES generation from git/release artifacts | Release hygiene |
| F-11 | Confidence scoring when MCP verification skipped | Transparency |

### Could Have

| ID | Feature | Rationale |
|----|---------|-----------|
| F-12 | GitHub issue/PR template generation | Repo polish |
| F-13 | Wiki export format | Enterprise users |

### Won't Have (this project)

| ID | Feature | Reason |
|----|---------|--------|
| F-14 | Automated CLI doc generator | Future implementation project |
| F-15 | Runtime kernel plugin | Out of scope |

## Success Metrics

| Metric | Target |
|--------|--------|
| Production projects pass G8 Documentation before G9 Release | 100% |
| Every generated doc has traceability entry in `documentation-report.md` | 100% |
| Handbook is sole writing standard reference in Documentation Engineer prompt | Yes |
| Zero contradictions with `spec.md` / `architecture.md` at G8 | 0 tolerated |

## Out of Scope

- Employee prompt content for non-documentation roles (except handoff lines)
- `runtime/interfaces.md` changes
- Implementation code beyond illustrative templates

## Open Questions

| # | Question | Resolution |
|---|----------|------------|
| Q-1 | Gate numbering after insert? | G8 Documentation; G9 Release; G10 Closure |
| Q-2 | Design-only projects skip docs? | EM documents skip in `pipeline-status.md` |

## Product Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Docs invented not derived | High | Validation + STOP rules |
| Reviewer still writes docs | Medium | Review checklist update — docs owned by Doc Engineer |
