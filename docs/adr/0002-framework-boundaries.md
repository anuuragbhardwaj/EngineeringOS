# ADR-0002: Framework Boundaries

**Status:** Accepted | **Date:** 2026-07-01

## Decision

Eight ownership classes: Framework-owned, Company-owned, Workspace-owned, Project-owned, Generated, User-owned, Temporary, Tool-generated, Cache. Every path maps to exactly one.

Framework assets never co-locate with workspace project code.

## References

- [domain-model.md](../framework/domain-model.md)
- Supersedes: `can_be_deleted/adr-legacy/0001-framework-boundaries.md`
