# Requirements — Kernel Hardening

## Functional Requirements

| ID | Requirement |
|----|-------------|
| R1 | `company_core` must not import `runtime_engine` |
| R2 | Runtime must own all `PipelineState` mutations |
| R3 | Orchestrator must use Runtime mutation APIs |
| R4 | Checkpoints must persist under `.company/checkpoints/` |
| R5 | Adapter failures must emit `AgentInvocationFailed` (orchestrator path) |
| R6 | MCP health diagnostics must have test coverage |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NF1 | Preserve public APIs and backward compatibility |
| NF2 | Minimize code changes; prefer deletion over addition |
| NF3 | All 134+ existing tests must pass |
| NF4 | No architectural redesign |

## Out of Scope

Marketplace, dashboard, cloud runtime, new employees, UI, package renames.
