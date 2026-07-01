# Testing Standards

Behavioral validation for QA and implementers. QA owns `qa-report.md`. Reviewer owns code-quality assessment ([review-checklist.md](./review-checklist.md)).

---

## Scope Split

| Role | Owns |
|------|------|
| **QA Engineer** | Does the software behave correctly per `spec.md`? |
| **Code Reviewer** | Is the code maintainable, secure, and architecture-compliant? |
| **Implementers** | Unit/integration tests that prove their tasks |

QA does **not** review code style. Reviewer does **not** re-run full acceptance testing.

---

## Test Pyramid

| Level | Owner | Target |
|-------|-------|--------|
| Unit | Implementers | Business logic, utilities, components |
| Integration | Implementers | API + DB, service boundaries |
| E2E / UI | QA (+ implementer component tests) | Critical user flows |

Every task in `tasks.md` must have a **Verify** command. QA runs all verify commands plus spec-based scenarios.

---

## Required Test Coverage (QA)

For every Must-Have `FR-*` in `spec.md`:

| Category | Required |
|----------|----------|
| Happy path | Yes |
| Invalid / empty input | Yes |
| Boundary values | Yes |
| Authentication / authorization | Yes (if applicable) |
| Error handling | Yes |
| API contract (status, shape) | Yes (backend) |
| UI states (loading, error, empty) | Yes (frontend) |
| Regression | Prior critical paths on brownfield |

---

## MCP Testing Evidence

When E2E tests use browser automation:

- Document `browser-automation` capability evidence in `qa-report.md` per [mcp/evidence-policy.md](../mcp/evidence-policy.md)
- If Playwright MCP not installed, document shell-based fallback

Validate MCP platform changes: `python -m mcp_platform validate`

---

## Tools (Defaults)

See [tech-stack.md](./tech-stack.md). Typical stack:

- **Backend:** pytest, httpx
- **Frontend:** project test runner (e.g., Vitest/Jest), Playwright for E2E when applicable

Use tools defined in `architecture.md` when they differ.

---

## qa-report.md Structure

```markdown
# QA Report — [Feature Name]

## Summary
## Test Environment
## Results Overview
| Area | Pass | Fail | Blocked |

## Spec Coverage
| Spec ID | Test Case | Result | Evidence |

## Defects
### DEF-001: [Title]
- **Severity:** Critical | High | Medium | Low
- **Assigned to:** Backend | Frontend | Architect | BA
- **Steps to reproduce:** ...
- **Expected:** ...
- **Actual:** ...
- **Evidence:** ...

## Regression Checklist
## Performance Observations (if applicable)

## Verdict
**PASS** | **FAIL**
```

---

## Defect Severity

| Level | Definition | Blocks release |
|-------|------------|----------------|
| **Critical** | Data loss, security breach, core flow broken | Yes |
| **High** | Major feature unusable; no workaround | Yes |
| **Medium** | Feature degraded; workaround exists | No |
| **Low** | Minor cosmetic or edge issue | No |

**PASS verdict:** No open Critical or High defects. All Must-Have `FR-*` tested.

---

## Defect Routing

| Type | Assign to |
|------|-----------|
| API, server, DB, auth logic | Backend |
| UI, layout, client state, a11y | Frontend |
| Contract / schema / design mismatch | Architect |
| Untestable or missing acceptance criteria | BA (via EM) |

After fixes: QA re-runs affected tests and updates defect status. Do not close defects without evidence.

---

## Implementer Test Obligations

Before QA handoff:

- [ ] All task verify commands pass
- [ ] New code has tests proportional to risk
- [ ] No skipped or commented-out failing tests
- [ ] Test output is reproducible (document setup in README if non-obvious)
