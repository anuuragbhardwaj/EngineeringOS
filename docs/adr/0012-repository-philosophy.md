# ADR-0012: Repository Philosophy

**Status:** Accepted | **Date:** 2026-07-01

## Context

Pre-release repository mixed framework assets, SDLc history, meta-reports, and orphans at root — unsuitable for public GitHub release.

## Decision

1. **Framework root** contains only active framework assets + `docs/` + `projects/` (active SDLc)
2. **Historical artifacts** move to `can_be_deleted/` — preserve, do not delete
3. **`runtime/interfaces.md`** remains stable path
4. **`can_be_deleted/`** is not published in release tags (`.gitignore` or release script excludes)
5. First public release = clean root + constitutional docs in `docs/framework/`

## Consequences

- Improved discoverability for contributors
- Meta-reports and SDLc archives preserved but out of root

## References

- [cleanup-report.md](../../cleanup-report.md)
