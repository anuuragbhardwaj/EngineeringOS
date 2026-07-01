# Idea — Framework Architecture (Constitutional Design)

## Submitted by
User / Stakeholder (via Engineering Manager)

## Date
2026-07-01

## Problem / Opportunity

The AI Company repository has matured: employees, handbook, runtime contracts, MCP platform, repository structure, and manifest specification exist. The repo is evolving into a **reusable framework** — but there is no **unified constitutional architecture** describing how Framework, Company Instance, Workspace, Project, Runtime, CLI, Integrations, and Plugins relate.

Without finalized framework architecture:

- Future CLI, bootstrapper, and runtime implementations will make ad-hoc structural decisions
- Multi-company, multi-workspace, and multi-editor support lack a shared model
- Ownership boundaries remain implicit
- Plugin and extension design risks coupling to core

## Proposed solution (high level)

**Design-only** project to produce the permanent architectural model:

1. Complete domain model (18 concepts with purpose, ownership, lifecycle, versioning, persistence)
2. Framework lifecycle (installation → maintenance)
3. Workspace and package architecture
4. Editor integration model (Cursor, VS Code, future)
5. CLI architecture (commands — responsibilities only)
6. Versioning and plugin architecture
7. System context and dependency maps
8. ADRs for all major decisions

**No implementation.** No CLI code. No runtime code.

## Target users

- Framework architects and maintainers
- Runtime Engine implementers
- CLI / bootstrapper developers
- Integration authors (editors, plugins)
- Contributors onboarding to the framework

## Business value

- Single constitutional reference for all future components
- Eliminates redesign cycles before implementation
- Enables multiple companies, projects, editors, cloud execution without architectural churn

## Constraints

- Builds on approved repository architecture and `company-manifest.md`
- Does not modify handbook policies, employee prompts, workflow behavior, or `runtime/interfaces.md` content
- Does not implement CLI or runtime
- Organizational/conceptual only

## Decision

**Proceed to Requirements**
