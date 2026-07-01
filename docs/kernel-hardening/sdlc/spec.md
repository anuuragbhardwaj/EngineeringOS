# Spec — Kernel Hardening

## Project 1: Dependency Purity

- Extract `IRuntimePort` Protocol in `company_core/ports/`
- Add `runtime_bridge` with factory injection
- Wire factory in `company_cli/runtime_bootstrap.py`
- Rewrite `ProjectAPI` to use bridge

## Project 2: Runtime Ownership

- Add `PipelineStateMutator` in `runtime_engine/state/`
- Expose via `RuntimeLifecycleBridge.mutator`
- Replace orchestrator direct `state.*` writes with mutator calls

## Project 3: Persistent Checkpoints

- Store at `.company/checkpoints/orchestrator/{project_id}.yaml`
- Schema version `1.0.0`
- Load on manager init; persist on create/pause/complete/rollback

## Event Consistency

- Publish `AgentInvocationFailed` when adapter returns failed status in `phase_executor`

## MCP Platform

- Test `health.py`: npx, context7, sequential thinking, `run_health_checks`
