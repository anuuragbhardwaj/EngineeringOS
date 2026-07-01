# AI Company Software Development Lifecycle (v1.1)

**Machine-readable authority:** [`workflow.yaml`](./workflow.yaml)  
**Version:** 1.1  
**Phases:** 11

---

## Pipeline

```
Idea → Requirements → Specification → Planning → Architecture
  → Implementation → Testing → Review → Documentation → Release → Closure
```

| Phase | Order | Artifact | Owner | Gate |
|-------|-------|----------|-------|------|
| Idea | 0 | `idea.md` | Engineering Manager | G0 |
| Requirements | 1 | `requirements.md` | Product Manager | G1 |
| Specification | 2 | `spec.md` | Business Analyst | G2 |
| Planning | 3 | `tasks.md` | Software Planner | G3 |
| Architecture | 4 | `architecture.md` | Software Architect | G4 |
| Implementation | 5 | source + tests | Backend / Frontend | G5 |
| Testing | 6 | `qa-report.md` | QA Engineer | G6 |
| Review | 7 | `review.md` | Code Reviewer | G7 |
| **Documentation** | **8** | **`documentation-report.md`** + generated docs | **Documentation Engineer** | **G8** |
| Release | 9 | `release.md` | Engineering Manager | G9 |
| Closure | 10 | `closure.md` | Engineering Manager | G10 |

Orchestration: `pipeline-status.md` (Engineering Manager)

---

## Documentation Phase (G8)

**Purpose:** Generate accurate, traceable documentation from project artifacts and source.

**Mandatory** for production-bound work. **Skippable** for design-only projects when EM documents exemption in `pipeline-status.md`.

**Standards:** [handbook/documentation-standards.md](./handbook/documentation-standards.md)  
**Platform:** [docs/documentation/documentation-platform.md](./docs/documentation/documentation-platform.md)

**Gate G8 pass when:**

- `documentation-report.md` verdict = PASS
- Validation checklist complete
- EM validates accuracy

---

## Gate Authority

| Gates | Approver |
|-------|----------|
| G1–G8 | Engineering Manager |
| G0, G9, G10 | User (facilitated by EM) |

---

## Golden Rules

1. One owner per artifact
2. STOP when blocked
3. Gates before handoff
4. Traceability: `FR-*` → tasks → tests → docs
5. Documentation derived from truth — never invented

---

## Handbook

See [handbook/company-handbook.md](./handbook/company-handbook.md)
