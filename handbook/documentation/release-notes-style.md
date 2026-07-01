# Release Notes Style

**Inherits:** [documentation-style-guide.md](./documentation-style-guide.md)  
**Version:** 1.0.0

---

## Scope

CHANGELOG.md, RELEASE_NOTES.md, migration guides, known-issues sections.

---

## CHANGELOG.md

Follow [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) structure:

```markdown
# Changelog

All notable changes to this project are documented here.

The format is based on Keep a Changelog,
and this project adheres to Semantic Versioning.

## [Unreleased]

### Added
### Changed
### Fixed
### Removed
### Security

## [1.0.0] - YYYY-MM-DD
```

### Rules

- Entries derived from `release.md`, git log, and merged PR scope — not invented features
- Imperative mood: "Add user authentication" not "Added authentication"
- Link PR/issue numbers when available in git messages
- **Unreleased** section for work since last tag
- Version dates from git tags or `release.md`

---

## RELEASE_NOTES.md

Audience: users upgrading or deploying. Structure:

1. **Version + date**
2. **Summary** — 2–3 sentences
3. **Highlights** — bullets for major changes
4. **Breaking changes** — migration steps required
5. **Upgrade steps** — ordered commands
6. **Known issues** — from `qa-report.md` or `review.md` accepted deferrals

Do not duplicate full CHANGELOG — summarize and link.

---

## Migration Guides

When breaking changes exist:

```markdown
# Migration Guide — v1 → v2

## Before you begin
- Backup [what]

## Step 1 — [action]
...

## Rollback
...
```

Each step must trace to `architecture.md` or `release.md` migration notes.

---

## Known Issues

| Issue | Workaround | Tracking |
|-------|------------|----------|
| Description from qa-report | If documented | DEF-* or issue # |

Only include issues explicitly accepted in QA/Review — do not expose unreviewed defects.

---

## References

- [documentation-templates.md](../../docs/documentation/documentation-templates.md) § CHANGELOG
- [release-notes-style.md](./release-notes-style.md) (this file)
