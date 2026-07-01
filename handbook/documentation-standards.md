# Documentation Standards

**Version:** 1.0.0  
**Date:** 2026-07-01  
**Authority:** Engineering Manager

Writing style: [documentation-style-guide.md](./documentation-style-guide.md)  
Platform reference: [docs/documentation/documentation-platform.md](../docs/documentation/documentation-platform.md)

---

## Purpose

Define documentation as a first-class SDLC deliverable — ownership, phase rules, inputs, outputs, and quality bar.

---

## Ownership

| Artifact / output | Owner | Readers |
|-------------------|-------|---------|
| `documentation-report.md` | Documentation Engineer | EM, all |
| README.md, CHANGELOG.md, docs/* (generated) | Documentation Engineer | Users, contributors |
| `idea.md` … `review.md` | Phase owners (unchanged) | Documentation Engineer reads only |
| Handbook writing standards | EM approves; Doc Engineer proposes | All |

**Documentation Engineer does NOT own:** requirements, spec, architecture decisions, implementation, testing, or code review.

---

## SDLC Position

**Phase 8 — Documentation** (after Review, before Release)

```
… → Review (G7) → Documentation (G8) → Release (G9) → Closure (G10)
```

| Gate | Approver | Pass when |
|------|----------|-----------|
| G8 Documentation | Engineering Manager | `documentation-report.md` verdict PASS; validation checklist complete |

**Mandatory** for production-bound work. **Skippable** for design-only projects when EM documents exemption in `pipeline-status.md`.

---

## Inputs (read-only)

| Input | Required |
|-------|----------|
| `idea.md` through `review.md` | Yes |
| `pipeline-status.md` | Yes |
| Source code | When project has implementation |
| Configuration / manifests | When present |
| Git history / diff | When `.git` exists |

STOP if `review.md` is not Approved.

---

## Outputs

Minimum per project type:

| Project type | Required outputs |
|--------------|------------------|
| Library / package | README.md, CHANGELOG.md (if versioned) |
| Application | README.md, INSTALLATION.md or SETUP.md, USAGE.md |
| API service | Above + API.md |
| Infrastructure | README.md, ARCHITECTURE.md |
| Internal design-only | `documentation-report.md` with skip justification |

Full catalog: [documentation-templates.md](../docs/documentation/documentation-templates.md)

---

## Principles

1. **Derived, not invented** — trace every claim to an artifact or source file
2. **No contradiction** — generated docs must align with `spec.md` and `architecture.md`
3. **Handbook is law** — writing rules live in `handbook/documentation/` only
4. **Validate before handoff** — [documentation-validation.md](../docs/documentation/documentation-validation.md)
5. **GitHub suitable** — public repos must be professional and accurate

---

## Ship-Ready Addition

A project is **not release-ready** until:

- [ ] G8 passed (or EM-documented skip)
- [ ] Generated README reflects shipped behavior
- [ ] Version references consistent with `release.md` / tags

See [definition-of-done.md](./definition-of-done.md).

---

## Rework Routing

| Symptom | Owner |
|---------|-------|
| Docs contradict implementation | Documentation Engineer (re-read source) |
| Missing features in docs | Documentation Engineer |
| Wrong architecture in docs | Architect revises `architecture.md`; Doc Engineer regenerates |
| Implementation changed post-review | Implementer fixes code → QA → Review → Documentation |

---

## MCP

| Capability | Required | When |
|------------|----------|------|
| `documentation-lookup` | Yes | Documenting frameworks, libraries, external APIs |
| `structured-reasoning` | Optional | Large multi-doc projects |

If MCP unavailable: continue; set confidence `reduced` in `documentation-report.md`.

Matrix: [mcp/employee-matrix.md](../mcp/employee-matrix.md)

---

## Revision Policy

Changes proposed via handbook PR or EM-approved edit. Agent prompts updated only for phase/handoff references — never for writing rules.
