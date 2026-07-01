# Definition of Done

Phase completion criteria. Gates G0–G10: [workflow-v1.md](../workflow-v1.md). Enforced by Engineering Manager per [engineering-standards.md](./engineering-standards.md).

---

## Closure Definition of Done

A project is **closed** when:

- [ ] G10 passed — `closure.md` complete with retrospective
- [ ] Success metrics compared to `requirements.md`
- [ ] `pipeline-status.md` status = **closed**
- [ ] All artifacts listed in `closure.md` archive table

---

## Release Definition of Done

A feature is **released** when:

- [ ] G9 passed — `release.md` complete; user confirms ship
- [ ] G8 passed — documentation approved (or EM-documented skip for design-only)
- [ ] Post-deploy verification done or user accepts manual run
- [ ] `review.md` **Approved** and `qa-report.md` **PASS** still valid

---

## Ship-Ready Definition of Done

Implementation is **ship-ready** (eligible for Release) when:

- [ ] `review.md` status is **✅ Approved**
- [ ] `qa-report.md` verdict is **PASS** with no open Critical/High defects
- [ ] `documentation-report.md` verdict is **PASS** (or EM skip documented)
- [ ] Generated README reflects shipped behavior
- [ ] All Must-Have `FR-*` in `spec.md` are implemented and tested
- [ ] `pipeline-status.md` shows all phases **pass**
- [ ] No `TODO` / `FIXME` in production code paths

---

## Phase 0 — Idea (`idea.md`)

**Owner:** Engineering Manager

- [ ] Problem, users, and business value articulated
- [ ] Decision = Proceed to Requirements
- [ ] User confirms G0

---

## Phase 1 — Requirements (`requirements.md`)

**Owner:** Senior Product Manager

- [ ] Problem statement and target users are explicit
- [ ] Every feature has MoSCoW priority with rationale
- [ ] User stories exist at product level (intent, not technical detail)
- [ ] Success metrics are measurable
- [ ] Out-of-scope and product risks documented
- [ ] Open questions listed (not silently assumed)
- [ ] No technology, API, or architecture decisions in document

---

## Phase 2 — Specification (`spec.md`)

**Owner:** Senior Business Analyst

- [ ] Every functional requirement has unique ID (`FR-*`) and is testable
- [ ] Non-functional requirements numbered (`NFR-*`)
- [ ] Every Must-Have user story has acceptance criteria
- [ ] Edge cases documented for Must-Have features
- [ ] Assumptions, dependencies, and constraints explicit
- [ ] Planner can produce `tasks.md` without product clarification

---

## Phase 3 — Planning (`tasks.md`)

**Owner:** Senior Software Planner

- [ ] Every `FR-*` and `NFR-*` mapped in traceability table
- [ ] Task DAG complete; no circular dependencies
- [ ] Each task has: depends-on, acceptance criteria, tests, verify command
- [ ] Critical path and parallel tracks identified
- [ ] 8–15 right-sized tasks (or justified exception)
- [ ] No final tech stack or detailed API design (deferred to Architect)
- [ ] **MCP evidence:** `structured-reasoning` footer in `tasks.md` per [evidence-policy.md](../mcp/evidence-policy.md)

---

## Phase 4 — Architecture (`architecture.md`)

**Owner:** Senior Software Architect

- [ ] Every task in `tasks.md` covered in Task Coverage Matrix
- [ ] Tech stack, folder structure, APIs, and schema finalized
- [ ] Security: auth, authorization, validation addressed
- [ ] API contracts complete enough for parallel backend/frontend work
- [ ] Risks and assumptions documented
- [ ] No implementation code in document
- [ ] **MCP evidence:** `documentation-lookup` footer in `architecture.md` per [evidence-policy.md](../mcp/evidence-policy.md)

---

## Phase 5 — Implementation (source + tests)

**Owners:** Senior Backend Engineer, Senior Frontend Engineer

- [ ] Code matches `architecture.md`
- [ ] All assigned task acceptance criteria met
- [ ] Unit and integration tests pass
- [ ] [Coding standards](./coding-standards.md) satisfied
- [ ] No TODO/FIXME placeholders
- [ ] Backend and frontend integrated when both exist

---

## Phase 6 — Testing (`qa-report.md`)

**Owner:** Senior QA Engineer

- [ ] Every Must-Have `FR-*` has test result with evidence
- [ ] All `tasks.md` verify commands executed
- [ ] Critical paths: happy path, invalid input, auth, errors covered
- [ ] No open **Critical** or **High** defects
- [ ] Verdict explicitly stated: **PASS** or **FAIL**
- [ ] [Testing standards](./testing-standards.md) followed

---

## Phase 7 — Review (`review.md`)

**Owner:** Senior Code Reviewer

- [ ] `qa-report.md` PASS confirmed
- [ ] [Review checklist](./review-checklist.md) applied
- [ ] Architecture compliance verified
- [ ] No open **Critical** or **High** findings
- [ ] Score and **Approved** / **Changes Requested** status recorded

---

## Phase 8 — Documentation (`documentation-report.md`)

**Owner:** Documentation Engineer

- [ ] `review.md` **Approved** confirmed
- [ ] Required generated docs for project type exist per [documentation-templates.md](../docs/documentation/documentation-templates.md)
- [ ] [Validation checklist](../docs/documentation/documentation-validation.md) complete
- [ ] Traceability matrix complete — no invented claims
- [ ] Verdict explicitly stated: **PASS** or **FAIL**
- [ ] [Documentation standards](./documentation-standards.md) and style guides followed
- [ ] **MCP evidence:** `documentation-lookup` footer when library/API docs referenced (or reduced confidence documented)

---

## Phase 9 — Release (`release.md`)

**Owner:** Engineering Manager

- [ ] Deploy and rollback steps documented
- [ ] Post-deploy verification checklist executed or user accepts
- [ ] User confirms G9

---

## Phase 10 — Closure (`closure.md`)

**Owner:** Engineering Manager

- [ ] Metrics compared to `requirements.md` success criteria
- [ ] All artifacts archived and listed
- [ ] Retrospective recorded
- [ ] User confirms G10

---

## Task-Level Definition of Done

A single implementation task (from `tasks.md`) is done when:

- [ ] Acceptance criteria checked off
- [ ] Verify command passes
- [ ] Code reviewed by implementer (self-review against architecture)
- [ ] No scope outside the task description

---

## Rework Definition of Done

A rework cycle is done when:

- [ ] Original defect or finding ID is addressed
- [ ] Assigned owner confirms fix
- [ ] QA re-tests (behavioral) or Reviewer re-reviews (code) as appropriate
- [ ] `pipeline-status.md` Rework History updated
