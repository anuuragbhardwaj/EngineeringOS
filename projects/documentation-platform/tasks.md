# Tasks — Documentation Platform

**Date:** 2026-07-01  
**Owner:** Senior Software Planner

---

## Traceability

| Task | FR/NFR |
|------|--------|
| T-01 | FR-04, FR-05, FR-06, FR-07 |
| T-02 | FR-14, FR-15, FR-16, FR-17 |
| T-03 | FR-01, FR-02 |
| T-04 | FR-08–FR-13, NFR-03 |
| T-05 | FR-27–FR-32, FR-03 |
| T-06 | FR-18–FR-23 |
| T-07 | FR-24–FR-26, FR-32 |
| T-08 | NFR-01, all |

---

## Task DAG

```
T-01 (handbook) ──┬──► T-03 (agent) ──► T-06 (validate behavior in report template)
T-02 (platform) ──┘         │
                            ▼
T-04 (workflow) ──► T-05 (handbook updates) ──► T-07 (MCP matrix)
                            │
                            ▼
                       T-08 (SDLC closure)
```

---

## Tasks

### T-01 — Documentation Handbook

**Depends on:** —  
**Owner:** Documentation standards (implementer)  
**FR:** FR-04–FR-07

**Description:** Create `handbook/documentation/` with master and specialized style guides plus `handbook/documentation-standards.md` and root index.

**Acceptance criteria:**
- [ ] All five handbook files exist with cross-references
- [ ] Master guide defines voice, accuracy, traceability, concision
- [ ] Specialized guides inherit and extend master

**Verify:** `ls handbook/documentation/` shows 5 files; `handbook/documentation-style-guide.md` links to master

---

### T-02 — Platform Specifications

**Depends on:** —  
**Owner:** Platform specs  
**FR:** FR-14–FR-17

**Description:** Create `docs/documentation/` platform docs.

**Acceptance criteria:**
- [ ] Four platform markdown files exist
- [ ] Templates include README, CHANGELOG, ARCHITECTURE, API, CONTRIBUTING
- [ ] Validation checklist complete

**Verify:** `ls docs/documentation/` shows 4 files

---

### T-03 — Documentation Engineer Agent

**Depends on:** T-01  
**Owner:** Agent author  
**FR:** FR-01, FR-02

**Description:** Create `.cursor/agents/documentation-engineer.md`.

**Acceptance criteria:**
- [ ] Phase 8 position documented
- [ ] Inputs/outputs match spec
- [ ] Capabilities table present
- [ ] Zero embedded writing rules — handbook links only

**Verify:** Grep agent file for "must use" writing rules — none; links to handbook present

---

### T-04 — Workflow Integration

**Depends on:** T-03  
**Owner:** Workflow editor  
**FR:** FR-08–FR-13, NFR-03

**Description:** Update `workflow.yaml` to v1.1 with Documentation phase; create `workflow-v1.md`.

**Acceptance criteria:**
- [ ] 11 phases; Documentation order 8
- [ ] G8 Documentation; G9 Release; G10 Closure
- [ ] `documentation-report.md` in artifacts
- [ ] Review `next: documentation`

**Verify:** Parse workflow.yaml — documentation phase exists with correct gate

---

### T-05 — Company Handbook & Employee Updates

**Depends on:** T-04  
**Owner:** Handbook editor  
**FR:** FR-27–FR-31, FR-03

**Description:** Update company-handbook, engineering-standards, definition-of-done, engineering-manager, senior-code-reviewer.

**Acceptance criteria:**
- [ ] All five files reference Phase 8 and G8–G10
- [ ] Artifact ownership includes `documentation-report.md`
- [ ] Ship-ready DoD requires documentation pass

**Verify:** Grep handbook for "Documentation Engineer" — matches in all required files

---

### T-06 — Documentation Report Template

**Depends on:** T-02, T-03  
**Owner:** Platform  
**FR:** FR-12, FR-21, FR-22, FR-23

**Description:** Embed `documentation-report.md` template in documentation-templates.md.

**Acceptance criteria:**
- [ ] Template includes traceability matrix, validation results, verdict, confidence
- [ ] Linked from documentation-validation.md

**Verify:** Template section exists in documentation-templates.md

---

### T-07 — MCP Matrix Update

**Depends on:** T-05  
**Owner:** MCP platform  
**FR:** FR-24–FR-26, FR-32

**Description:** Add Documentation Engineer to employee-matrix.md and evidence-policy.md.

**Acceptance criteria:**
- [ ] Matrix row with documentation-lookup required, structured-reasoning optional
- [ ] G8 evidence policy documented

**Verify:** Grep employee-matrix for documentation-engineer

---

### T-08 — SDLC Package Completion

**Depends on:** T-01–T-07  
**Owner:** EM  
**NFR:** NFR-01

**Description:** Complete qa-report, review, release, closure for this project.

**Acceptance criteria:**
- [ ] All deliverables present
- [ ] pipeline-status.md closed
- [ ] `python -m mcp_platform validate` PASS

**Verify:** EM validates all gates G0–G10

---

## MCP Evidence

| Capability | Status | Notes |
|------------|--------|-------|
| structured-reasoning | completed | Task DAG and phase insertion planned with dependency analysis |
