# GitHub Documentation Guide

**Version:** 1.0.0  
**Date:** 2026-07-01

Style: [handbook/documentation/github-style.md](../../handbook/documentation/github-style.md)

---

## Purpose

Define what the Documentation Engineer produces for public GitHub repositories and how it maps to GitHub features.

---

## Repository Documentation Set

### Minimum (every public repo)

| Asset | Path | GitHub surface |
|-------|------|----------------|
| README | `README.md` | Repository home |
| License | `LICENSE` | GitHub license detector |
| Changelog | `CHANGELOG.md` | Releases companion |

### Recommended

| Asset | Path |
|-------|------|
| Contributing | `CONTRIBUTING.md` |
| Code of Conduct | `CODE_OF_CONDUCT.md` |
| Security policy | `SECURITY.md` |
| Architecture | `ARCHITECTURE.md` or `docs/architecture.md` |

### GitHub Features

| Feature | Path | When to generate |
|---------|------|------------------|
| Issue templates | `.github/ISSUE_TEMPLATE/*.md` | Open-source with external contributors |
| PR template | `.github/pull_request_template.md` | Team repos |
| Release notes | GitHub Release body | From RELEASE_NOTES.md at G9 |

---

## README Best Practices

1. **First 100 words** — what, why, quick start
2. **Badges** — only CI, version, license if accurate and maintained
3. **No internal paths** — hide `projects/*/pipeline-status.md` from public README
4. **Relative links** — survive fork and clone
5. **License section** — match LICENSE file

---

## Release Workflow Integration

```
G8 Documentation → generates CHANGELOG + RELEASE_NOTES
G9 Release → EM/user publishes GitHub Release using RELEASE_NOTES.md
```

Version tags must match CHANGELOG headings.

---

## Wiki Export (optional)

When wiki requested:

- One page per major doc (README content → Home)
- Link back to repo docs/ for canonical source
- Note in `documentation-report.md` that wiki is derivative

---

## Issue Template Example

```yaml
---
name: Bug Report
about: Report incorrect behavior
labels: bug
---

## Description

## Steps to reproduce

## Expected behavior

## Environment
- Version:
- OS:
```

---

## PR Template Example

```markdown
## Summary

## Type
- [ ] Bug fix
- [ ] Feature
- [ ] Documentation

## Checklist
- [ ] Tests pass
- [ ] Documentation updated (if behavior changed)
```

---

## AI Company Framework Repo

For `ai-company` itself:

- Public README: framework overview, quick start, constitution links
- Internal SDLc artifacts stay in `projects/` — not promoted to README
- `can_be_deleted/` never linked from public docs

---

## References

- [documentation-platform.md](./documentation-platform.md)
- [documentation-templates.md](./documentation-templates.md)
