# MCP Evidence Policy

**Version:** 1.0.0

---

## Purpose

Provide auditable proof that required capabilities were used. EM validates evidence at quality gates.

---

## Evidence Format (Standard Footer)

Add to bottom of primary phase artifact:

```markdown
---
## MCP Evidence

| Capability | Resolved MCP | Status | Notes |
|------------|--------------|--------|-------|
| structured-reasoning | sequential-thinking | completed | N thoughts; nextThoughtNeeded=false |
| documentation-lookup | context7 | completed | Libraries: /fastapi/fastapi, /pydantic/pydantic |
```

---

## Phase Requirements

| Phase | Artifact | Required Evidence |
|-------|----------|-------------------|
| Planning | tasks.md | `structured-reasoning` — **required** |
| Architecture | architecture.md | `documentation-lookup` — **required** |
| Implementation | source / PR | `documentation-lookup` — on EM request |
| Testing | qa-report.md | `browser-automation` — if Playwright E2E |
| Documentation | documentation-report.md | `documentation-lookup` — when framework/library/API docs cited; or document reduced confidence |
| Review | review.md | Optional: `static-analysis`, `diff-inspection` |
| All others | — | None unless EM requests |

---

## Evidence Status Values

| Status | Meaning |
|--------|---------|
| `completed` | Capability used successfully |
| `fallback` | Primary unavailable; fallback MCP used (document which) |
| `skipped` | Optional capability not used (reason required) |
| `unavailable` | Required capability could not resolve — **gate must fail** |
| `n/a` | Capability not applicable to this artifact |

---

## Structured Reasoning Evidence (Planner)

Required content:
- Confirmation that capability `structured-reasoning` was invoked
- Summary: scope → decomposition → dependencies → coverage check
- `nextThoughtNeeded: false` reached

Example:
```markdown
## MCP Evidence
| Capability | Resolved MCP | Status | Notes |
|------------|--------------|--------|-------|
| structured-reasoning | sequential-thinking | completed | 8 thoughts; DAG verified against all FR-* |
```

---

## Documentation Lookup Evidence (Architect / Implementers)

Required content:
- Library IDs queried via `documentation-lookup`
- Brief note on what was verified

Example in architecture.md References:
```markdown
## MCP Evidence
| Capability | Resolved MCP | Status | Notes |
|------------|--------------|--------|-------|
| documentation-lookup | context7 | completed | Queried: FastAPI routing, Pydantic v2 models |
```

---

## Fallback Evidence

When fallback MCP used:

```markdown
| documentation-lookup | fetch | fallback | context7 unavailable; used fetch for public docs only |
```

EM must accept risk for framework API work without Context7.

---

## Failure Evidence

```markdown
| structured-reasoning | — | unavailable | sequential-thinking server down; STOPPED |
```

Gate **cannot pass** with `unavailable` on required capability.

---

## Audit Trail

- EM checks evidence footer at each gate
- Future: `McpEvidencePlugin` validates automatically via kernel events
- Failures logged in pipeline-status.md

---

## References

- [validation-policy.md](./validation-policy.md)
- [employee-matrix.md](./employee-matrix.md)
