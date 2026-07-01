# ADR-0009: Editor Integrations

**Status:** Accepted | **Date:** 2026-07-01

## Decision

Editors (Cursor, VS Code, Claude Code, Roo Code, future) are adapters under `integrations/<editor>/`. Canonical employees in `employees/`. `company install --editor` syncs. Zero framework logic in editors.

## References

- [integration-architecture.md](../framework/integration-architecture.md)
