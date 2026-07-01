# Engineering Standards

Pipeline mechanics, artifact ownership, quality gates, handoffs, and rework. **Canonical SDLc:** [workflow-v1.md](../workflow-v1.md). See [company-handbook.md](./company-handbook.md) for the index.

---

## Artifact Ownership

| Artifact | Owner | Readers | Mutable by |
|----------|-------|---------|------------|
| `idea.md` | Engineering Manager | All | EM only |
| `requirements.md` | Product Manager | All | PM only |
| `spec.md` | Business Analyst | All | BA only |
| `tasks.md` | Software Planner | Architect, Implementers, QA | Planner only |
| `architecture.md` | Software Architect | Implementers, QA, Reviewer | Architect only |
| Source code + tests | Backend / Frontend | QA, Reviewer | Implementers only |
| `qa-report.md` | QA Engineer | Reviewer, EM | QA only |
| `review.md` | Code Reviewer | EM, Implementers, Doc Engineer | Reviewer only |
| `documentation-report.md` + generated docs | Documentation Engineer | EM, all | Documentation Engineer only |
| `release.md` | Engineering Manager | All | EM (+ implementer deploy input) |
| `closure.md` | Engineering Manager | All | EM only |
| `pipeline-status.md` | Engineering Manager | All | EM only |

**Implementers must not modify** `requirements.md`, `spec.md`, `tasks.md`, or `architecture.md`. Escalate via EM.

---

## Document Section Split (PM vs BA)

Avoid duplication between `requirements.md` and `spec.md`.

| Content | Document |
|---------|----------|
| Problem, users, business goals, MoSCoW, success metrics, product risks | `requirements.md` |
| Numbered `FR-*` / `NFR-*`, acceptance criteria, edge cases, business rules, assumptions, dependencies | `spec.md` |

BA references `requirements.md`; does not copy problem statement or priorities verbatim.

---

## Planner vs Architect Split

| Concern | Owner | Output |
|---------|-------|--------|
| Milestones, task DAG, traceability, per-task verify commands | Planner | `tasks.md` |
| Tech stack, folder structure, APIs, schema, security design | Architect | `architecture.md` |

Planner may list **planned paths (subject to architecture)** only. Final technical decisions live in `architecture.md`.

---

## Quality Gates

Advance only when **all** criteria pass. Gates G0–G10: [workflow-v1.md](../workflow-v1.md). Checklists: [definition-of-done.md](./definition-of-done.md).

| Phase | Artifact | Gate |
|-------|----------|------|
| 0 Idea | `idea.md` | G0 — User approves proceed |
| 1 Requirements | `requirements.md` | G1 |
| 2 Specification | `spec.md` | G2 |
| 3 Planning | `tasks.md` | G3 |
| 4 Architecture | `architecture.md` | G4 |
| 5 Implementation | source + tests | G5 |
| 6 Testing | `qa-report.md` | G6 — PASS |
| 7 Review | `review.md` | G7 — Approved |
| 8 Documentation | `documentation-report.md` | G8 — PASS (skippable design-only) |
| 9 Release | `release.md` | G9 — User confirms ship |
| 10 Closure | `closure.md` | G10 — User confirms close |

---

## Handoff Protocol

1. Owner confirms quality gate pass.
2. Owner delivers artifact at agreed path.
3. Next owner acknowledges required inputs present.
4. EM updates `pipeline-status.md`.

**Parallel work:** After Phase 4, Backend and Frontend may run concurrently when `architecture.md` defines complete API contracts. Merge before Phase 6.

---

## Rework Routing

| Issue | Route to |
|-------|----------|
| Product scope / priority | Product Manager |
| Missing / ambiguous acceptance criteria | Business Analyst |
| Task plan gaps | Software Planner |
| Design / API / schema flaw | Software Architect |
| Backend defect | Backend Engineer |
| Frontend / UI defect | Frontend Engineer |
| Code quality (no design change) | Implementer per `review.md` |
| Behavioral failure | QA re-test after fix |
| Security architecture | Architect → implementer |

Log rework in `pipeline-status.md` → **Rework History**. Same phase failing **3 times** → EM escalates to user.

---

## STOP Conditions (Universal)

STOP and report when:

- Required input artifact is missing
- Upstream artifact contradicts downstream work
- Product or spec question requires scope decision
- Same blocker persists after 2 escalation attempts

See [communication-guidelines.md](./communication-guidelines.md) for reporting format.

---

## MCP Usage

**Authority:** [mcp/](../mcp/) — MCP Platform. Supersedes ad-hoc MCP references.

Employees request **capabilities** (e.g. `structured-reasoning`, `documentation-lookup`). The [registry](../mcp/registry.yaml) resolves MCPs. **Never hardcode MCP server names in prompts or artifacts.**

| Agent | Required Capabilities | When |
|-------|----------------------|------|
| Software Planner | `structured-reasoning` | Before writing `tasks.md` — G3 evidence required |
| Software Architect | `documentation-lookup` | When writing `architecture.md` — G4 evidence required |
| Documentation Engineer | `documentation-lookup` | When documenting frameworks/libraries — G8 evidence when applicable |
| Backend / Frontend Engineer | `documentation-lookup` | Framework APIs — G5 advisory |
| All others | See [employee-matrix.md](../mcp/employee-matrix.md) | Optional per role |

**Validation:** `python -m mcp_platform validate`  
**Policy:** [selection-policy.md](../mcp/selection-policy.md), [evidence-policy.md](../mcp/evidence-policy.md)

---

## Implementation Standards Reference

Code: [coding-standards.md](./coding-standards.md)  
Tests: [testing-standards.md](./testing-standards.md)  
Review: [review-checklist.md](./review-checklist.md)  
Stack defaults: [tech-stack.md](./tech-stack.md) (overridden per project by `architecture.md`)
