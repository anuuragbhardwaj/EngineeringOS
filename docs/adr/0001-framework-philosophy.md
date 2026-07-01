# ADR-0001: Framework Philosophy

**Status:** Accepted | **Date:** 2026-07-01

## Context

AI Company evolved from prompts and markdown into a multi-subsystem repository. Risk of ad-hoc growth without governing philosophy.

## Decision

Adopt **Framework as immutable product** philosophy:

1. Framework defines SDLc — projects never modify it
2. Company Instance configures deployment
3. Workspace isolates user work
4. Project executes one SDLc run
5. All products consume Framework API
6. Editors are adapters; kernel is editor-independent

## Consequences

- Clear upgrade and ownership boundaries
- Implementation projects derive from architecture — no redesign

## References

- [framework-model.md](../framework/framework-model.md)
