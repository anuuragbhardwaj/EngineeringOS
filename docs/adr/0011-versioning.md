# ADR-0011: Versioning

**Status:** Accepted | **Date:** 2026-07-01

## Decision

Independent semver per artifact class (framework, company instance, workspace, project, packages, manifest, templates, kernel contracts, generated state). Projects pin workflow at creation. Major upgrades require `company migrate`.

## References

- [versioning-strategy.md](../framework/versioning-strategy.md)
