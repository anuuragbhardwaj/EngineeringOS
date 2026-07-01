# Company Handbook

Internal reference for all AI company employees. **Do not duplicate this content in agent prompts** — link here instead.

---

## Purpose

This handbook defines how we build enterprise software: the delivery pipeline, shared standards, quality gates, and communication norms. Individual agent files (`.cursor/agents/`) define **role-specific behavior** only.

---

## Handbook Index

| Document | Audience | Contents |
|----------|----------|----------|
| [../workflow-v1.md](../workflow-v1.md) | All | **Canonical SDLc** — 10 phases, gates, artifacts |
| [engineering-standards.md](./engineering-standards.md) | All engineers, EM | Pipeline, artifacts, gates, handoffs, rework |
| [coding-standards.md](./coding-standards.md) | Backend, Frontend, Reviewer | Code quality, structure, security defaults |
| [testing-standards.md](./testing-standards.md) | QA, Backend, Frontend | Test strategy, `qa-report.md`, coverage |
| [review-checklist.md](./review-checklist.md) | Code Reviewer | Review criteria, severity, `review.md` |
| [definition-of-done.md](./definition-of-done.md) | All | Per-phase and release DoD |
| [communication-guidelines.md](./communication-guidelines.md) | All | Tone, escalation, STOP rules, blockers |
| [tech-stack.md](./tech-stack.md) | Architect, Implementers | Default stack; project overrides in `architecture.md` |
| [documentation-style-guide.md](./documentation-style-guide.md) | Documentation Engineer | Writing standards index |
| [documentation-standards.md](./documentation-standards.md) | Documentation Engineer, EM | Phase 8 rules, ownership, validation |
| [documentation/](./documentation/) | Documentation Engineer | Master and specialized style guides |
| [../docs/documentation/](../docs/documentation/) | Documentation Engineer | Platform specs, templates, validation |
| [../mcp/](../mcp/) | **All** | **MCP Platform** — registry, capabilities, policies, employee matrix |

### MCP Platform Index

| Document | Purpose |
|----------|---------|
| [mcp/registry.yaml](../mcp/registry.yaml) | Canonical MCP catalog (33+ servers) |
| [mcp/capabilities.yaml](../mcp/capabilities.yaml) | Capability → MCP resolution |
| [mcp/employee-matrix.md](../mcp/employee-matrix.md) | Employee × capability assignments |
| [mcp/selection-policy.md](../mcp/selection-policy.md) | Tool selection and fallback rules |
| [mcp/evidence-policy.md](../mcp/evidence-policy.md) | Gate evidence requirements |
| [mcp/installation-guide.md](../mcp/installation-guide.md) | Install procedures |

**Rule:** Employees request **capabilities**, never hardcode MCP server names. See [mcp/selection-policy.md](../mcp/selection-policy.md).

---

## Organization

| Role | Agent | Phase |
|------|-------|-------|
| Engineering Manager | `engineering-manager` | Orchestration (all phases) |
| Senior Product Manager | `senior-product-manager` | 1 — Requirements |
| Senior Business Analyst | `senior-business-analyst` | 2 — Specification |
| Senior Software Planner | `senior-software-planner` | 3 — Planning |
| Senior Software Architect | `senior-software-architect` | 4 — Architecture |
| Senior Backend Engineer | `senior-backend-engineer` | 5 — Implementation |
| Senior Frontend Engineer | `senior-frontend-engineer` | 5 — Implementation |
| Senior QA Engineer | `senior-qa-engineer` | 6 — Testing |
| Senior Code Reviewer | `senior-code-reviewer` | 7 — Review |
| Documentation Engineer | `documentation-engineer` | 8 — Documentation |

All specialists report to the Engineering Manager. The EM reports to the user/stakeholder.

---

## Delivery Pipeline

See **[workflow-v1.md](../workflow-v1.md)** for the canonical 11-phase SDLc.

```
Idea → Requirements → Specification → Planning → Architecture
  → Implementation → Testing → Review → Documentation → Release → Closure
```

| Phase | Artifact | Owner |
|-------|----------|-------|
| 0 Idea | `idea.md` | Engineering Manager |
| 1 Requirements | `requirements.md` | Product Manager |
| 2 Specification | `spec.md` | Business Analyst |
| 3 Planning | `tasks.md` | Software Planner |
| 4 Architecture | `architecture.md` | Software Architect |
| 5 Implementation | source + tests | Backend / Frontend |
| 6 Testing | `qa-report.md` | QA Engineer |
| 7 Review | `review.md` | Code Reviewer |
| 8 Documentation | `documentation-report.md` + generated docs | Documentation Engineer |
| 9 Release | `release.md` | Engineering Manager |
| 10 Closure | `closure.md` | Engineering Manager |

Orchestration log: `pipeline-status.md` (Engineering Manager). Machine-readable: [`workflow.yaml`](../workflow.yaml).

---

## Golden Rules

1. **One owner per artifact.** Do not edit upstream documents outside your phase.
2. **STOP when blocked.** Missing inputs → halt and report. Never guess.
3. **Gates before handoff.** Every phase must pass its quality gate ([definition-of-done.md](./definition-of-done.md)).
4. **Traceability.** Requirements flow `FR-*` / `NFR-*` in `spec.md` → tasks in `tasks.md` → tests in `qa-report.md`.
5. **Scope split.** PM = product intent. BA = testable spec. Planner = what/when. Architect = how/where. QA = behavior. Reviewer = code quality.

---

## When to Read What

| Starting work on… | Read first |
|-------------------|------------|
| Any feature | This file + [engineering-standards.md](./engineering-standards.md) |
| `requirements.md` | [definition-of-done.md](./definition-of-done.md) § Phase 1 |
| `spec.md` | [definition-of-done.md](./definition-of-done.md) § Phase 2 |
| `tasks.md` / `architecture.md` | [engineering-standards.md](./engineering-standards.md), [tech-stack.md](./tech-stack.md) |
| Implementation | [coding-standards.md](./coding-standards.md), [tech-stack.md](./tech-stack.md), `architecture.md` |
| Testing | [testing-standards.md](./testing-standards.md), `spec.md` |
| Code review | [review-checklist.md](./review-checklist.md), `qa-report.md` |
| Documentation | [documentation-standards.md](./documentation-standards.md), [documentation-style-guide.md](./documentation-style-guide.md) |

---

## Revision Policy

Handbook changes are proposed by any employee, approved by Engineering Manager, and must stay synchronized with `.cursor/agents/` role boundaries. Project-specific overrides always live in `architecture.md`, not in this handbook.
