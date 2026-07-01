# ADR-0006: Framework API

**Status:** Accepted | **Date:** 2026-07-01

## Decision

Single Framework API (`CompanyAPI`, `WorkspaceAPI`, `ProjectAPI`, `McpAPI`, `IntegrationAPI`, `EmployeeAPI`, etc.) is the only consumption path for CLI, editors, SDK, cloud, dashboard. Kernel API (`runtime/interfaces.md`) remains separate subset for runtime orchestration.

## Consequences

- No product bypasses API to read handbook/workflow directly
- Python `company_core` implements contracts first

## References

- [framework-api.md](../framework/framework-api.md)
