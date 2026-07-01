# Review Checklist

Code review standards for the Senior Code Reviewer. Output: `review.md`. Prerequisites: `qa-report.md` verdict **PASS**.

See [coding-standards.md](./coding-standards.md) for implementation rules. QA owns behavioral testing ([testing-standards.md](./testing-standards.md)).

---

## Review Inputs

| Input | Required |
|-------|----------|
| `architecture.md` | Yes |
| `spec.md` | Yes |
| Source code | Yes |
| Test suite + results | Yes |
| `qa-report.md` (PASS) | Yes |

**STOP** if implementation incomplete or QA has not passed.

---

## MCP Review (Optional)

When reviewing infrastructure or MCP-related changes:

- [ ] No hardcoded MCP server names in employee prompts or kernel code
- [ ] Registry/capabilities changes pass `python -m mcp_platform validate`
- [ ] No secrets in `mcp.json` or registry
- [ ] Capability-based design per [mcp/selection-policy.md](../mcp/selection-policy.md)

---

## Review Dimensions

| Dimension | Check |
|-----------|-------|
| **Architecture compliance** | Structure, APIs, and patterns match `architecture.md` |
| **Correctness** | Logic matches `spec.md`; no obvious bugs |
| **Simplicity** | No unnecessary abstraction or complexity |
| **Maintainability** | Readable; modular; consistent with codebase |
| **Security** | Input validation, auth, secrets, dependencies (code-level) |
| **Performance** | No obvious bottlenecks; appropriate queries/caching |
| **Error handling** | Explicit failures; safe user-facing messages |
| **Logging** | Adequate at boundaries; no sensitive data logged |
| **Testing** | Tests exist, are meaningful, and pass |
| **API consistency** | Naming, status codes, error shapes align |
| **Duplication** | No copy-paste that should be shared |
| **Documentation** | Public APIs and setup documented by Documentation Engineer (Phase 8) — not Reviewer |

---

## Severity Levels

| Level | Meaning | Blocks approval |
|-------|---------|-----------------|
| **Critical** | Security hole, data loss risk, broken core flow in code | Yes |
| **High** | Significant correctness or maintainability risk | Yes |
| **Medium** | Should fix; document if deferred with EM agreement | No* |
| **Low** | Minor improvement | No |
| **Suggestion** | Optional polish | No |

\*Default: do not approve with open Medium unless EM explicitly accepts debt.

---

## review.md Structure

```markdown
# Code Review — [Feature Name]

## Executive Summary

## Positives

## Findings
### R-001: [Title]
- **Severity:** Critical | High | Medium | Low | Suggestion
- **Assigned to:** Backend | Frontend | Architect
- **Description:** ...
- **Recommendation:** ...

## Architecture Compliance
Pass | Fail — [notes]

## Overall Assessment
**Score:** X / 10
**Status:** ✅ Approved | ❌ Changes Requested
```

---

## Finding Assignment

| Finding type | Route to |
|--------------|----------|
| Code quality, naming, tests | Backend or Frontend |
| Security / performance in implementation | Backend or Frontend |
| Architecture drift or design flaw | Architect → implementer |
| Scope creep in code | EM → PM |

Reviewer **recommends**; does not implement. After fixes, re-review affected areas only.

---

## Approval Criteria

**Approved** when:

- [ ] `qa-report.md` verdict is **PASS**
- [ ] No open **Critical** or **High** findings
- [ ] Architecture compliance confirmed
- [ ] Score and status are explicit

**Changes Requested** when any Critical/High finding is open or architecture compliance fails.

---

## Out of Scope for Reviewer

- Re-running full QA acceptance scenarios
- Editing `requirements.md`, `spec.md`, `tasks.md`, `architecture.md`
- Implementing fixes or large rewrites
- Approving with open Critical/High findings
