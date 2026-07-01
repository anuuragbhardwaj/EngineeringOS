# Documentation Validation

**Version:** 1.0.0  
**Date:** 2026-07-01

Used by Documentation Engineer before G8 handoff. Results recorded in `documentation-report.md`.

---

## Validation Checklist

### 1. Artifact Consistency

- [ ] No statement contradicts `spec.md` Must-Haves or `architecture.md`
- [ ] Features listed in README exist in implementation or are marked roadmap
- [ ] Out-of-scope items from `requirements.md` not documented as shipped

### 2. Implementation Match

- [ ] Public API endpoints in API.md exist in source
- [ ] Config flags and env vars match code defaults
- [ ] Folder structure in docs matches repository
- [ ] Dependencies match `requirements.txt` / `package.json` / `pyproject.toml`

### 3. Links and References

- [ ] All relative links resolve to existing files
- [ ] External links reachable (or marked unverified with reduced confidence)
- [ ] No broken anchor references

### 4. Commands and Code

- [ ] Install/setup commands executed or marked `unverified`
- [ ] Test commands match `tasks.md` verify commands
- [ ] Code snippets syntactically valid for stated language
- [ ] No secrets in examples

### 5. Versions

- [ ] Version in README/CHANGELOG matches git tag or `release.md`
- [ ] Compatibility statements match `architecture.md`

### 6. Completeness

- [ ] Required outputs for project type generated (see documentation-platform.md)
- [ ] Traceability matrix complete — no orphan claims
- [ ] Known issues only from accepted QA/Review deferrals

### 7. Style

- [ ] Follows [documentation-style-guide.md](../../handbook/documentation/documentation-style-guide.md)
- [ ] Appropriate specialized guide applied per document type

### 8. MCP Evidence (when applicable)

- [ ] `documentation-lookup` used for framework/library API claims
- [ ] MCP Evidence footer in `documentation-report.md` per [evidence-policy.md](../../mcp/evidence-policy.md)
- [ ] Confidence level stated if MCP skipped

---

## Verdict Rules

| Verdict | Condition |
|---------|-----------|
| **PASS** | All mandatory checks pass; gaps explicitly documented and accepted |
| **FAIL** | Contradiction with artifacts, invented content, or broken install path |
| **BLOCKED** | Missing required inputs (e.g., review not approved) |

FAIL → fix and re-validate. EM does not pass G8 on FAIL.

---

## Gap Documentation

Allowed gaps (must list in report):

- Undocumented optional features
- Unverified commands (environment limitation)
- TBD license or version pending release

Forbidden: fabricating content to fill gaps.

---

## EM Gate Review

Engineering Manager spot-checks:

1. `documentation-report.md` verdict and traceability matrix
2. README quick-start plausibility
3. No internal SDLC leakage in public-facing docs

---

## References

- [documentation-templates.md](./documentation-templates.md) § documentation-report
- [handbook/documentation-standards.md](../../handbook/documentation-standards.md)
